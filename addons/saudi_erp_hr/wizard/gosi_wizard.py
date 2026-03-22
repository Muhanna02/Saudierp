from odoo import api, fields, models
from datetime import date


class GosiMonthlyWizard(models.TransientModel):
    _name = 'gosi.monthly.wizard'
    _description = 'Generate Monthly GOSI Report'

    period_date = fields.Date(string='Month', required=True, default=date.today())
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    employee_ids = fields.Many2many('hr.employee', string='Employees',
                                    help='Leave empty to include all active employees')

    def action_generate_gosi(self):
        employees = self.employee_ids or self.env['hr.employee'].search([
            ('company_id', '=', self.company_id.id),
            ('active', '=', True),
            ('gosi_registered', '=', True),
        ])

        contributions = []
        for emp in employees:
            existing = self.env['gosi.contribution'].search([
                ('employee_id', '=', emp.id),
                ('period_date', '=', self.period_date),
            ])
            if not existing:
                self.env['gosi.contribution'].create({
                    'employee_id': emp.id,
                    'period_date': self.period_date,
                    'basic_salary': emp.basic_salary,
                    'housing_allowance': emp.housing_allowance,
                    'company_id': self.company_id.id,
                })

        return {
            'type': 'ir.actions.act_window',
            'name': 'GOSI Contributions',
            'res_model': 'gosi.contribution',
            'view_mode': 'tree,form',
            'domain': [('period_date', '=', self.period_date),
                       ('company_id', '=', self.company_id.id)],
        }
