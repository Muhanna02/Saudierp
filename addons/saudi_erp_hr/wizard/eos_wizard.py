from odoo import api, fields, models
from datetime import date


class EosCalculatorWizard(models.TransientModel):
    _name = 'hr.eos.calculator.wizard'
    _description = 'EOS Calculator Wizard'

    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    termination_date = fields.Date(string='Termination Date', default=date.today())
    termination_reason = fields.Selection([
        ('resignation', 'Resignation'),
        ('termination_employer', 'Terminated by Employer'),
        ('contract_end', 'Contract Ended'),
        ('mutual_agreement', 'Mutual Agreement'),
        ('death', 'Death'),
        ('disability', 'Disability'),
        ('retirement', 'Retirement'),
    ], string='Reason', required=True, default='resignation')

    # Preview fields
    joining_date = fields.Date(related='employee_id.joining_date')
    years_of_service = fields.Float(string='Years of Service', compute='_compute_preview')
    basic_salary = fields.Monetary(related='employee_id.basic_salary',
                                   currency_field='currency_id')
    eos_amount_preview = fields.Monetary(string='Estimated EOS Amount',
                                         compute='_compute_preview',
                                         currency_field='currency_id')
    currency_id = fields.Many2one('res.currency',
                                  default=lambda self: self.env.ref('base.SAR'))

    @api.depends('employee_id', 'termination_date', 'termination_reason')
    def _compute_preview(self):
        for wizard in self:
            if wizard.employee_id and wizard.termination_date and wizard.employee_id.joining_date:
                delta = wizard.termination_date - wizard.employee_id.joining_date
                wizard.years_of_service = delta.days / 365.25
                # Simple estimate
                monthly = (wizard.employee_id.basic_salary or 0) + (wizard.employee_id.housing_allowance or 0)
                years = wizard.years_of_service
                if years < 2 and wizard.termination_reason == 'resignation':
                    wizard.eos_amount_preview = 0
                elif years <= 5:
                    wizard.eos_amount_preview = monthly * years * (1/3)
                elif years <= 10:
                    wizard.eos_amount_preview = monthly * 5 * (1/3) + monthly * (years - 5) * (2/3)
                else:
                    wizard.eos_amount_preview = monthly * 5 * (1/3) + monthly * 5 * (2/3) + monthly * (years - 10)
            else:
                wizard.years_of_service = 0
                wizard.eos_amount_preview = 0

    def action_create_eos(self):
        emp = self.employee_id
        eos = self.env['hr.eos.benefit'].create({
            'employee_id': emp.id,
            'termination_date': self.termination_date,
            'termination_reason': self.termination_reason,
            'last_basic_salary': emp.basic_salary,
            'last_housing_allowance': emp.housing_allowance,
        })
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'hr.eos.benefit',
            'res_id': eos.id,
            'view_mode': 'form',
        }
