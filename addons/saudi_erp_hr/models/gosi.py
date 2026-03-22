from odoo import api, fields, models
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

# GOSI Rates (2024)
GOSI_SAUDI_EMPLOYEE_RATE = 0.10   # 10% from Saudi employee
GOSI_SAUDI_EMPLOYER_RATE = 0.12   # 12% from employer for Saudi
GOSI_EXPAT_EMPLOYER_RATE = 0.02   # 2% from employer for expat (Occupational Hazard only)
GOSI_ANNUITY_CEILING = 45000      # Monthly salary ceiling for annuity branch


class GosiContribution(models.Model):
    """Monthly GOSI contribution records"""
    _name = 'gosi.contribution'
    _description = 'GOSI Monthly Contribution'
    _order = 'period_date desc, employee_id'

    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env.company)
    period_date = fields.Date(string='Period (Month)', required=True)
    nationality_category = fields.Selection(related='employee_id.nationality_category',
                                            store=True)

    # Salary basis
    basic_salary = fields.Monetary(string='Basic Salary', currency_field='currency_id')
    housing_allowance = fields.Monetary(string='Housing Allowance', currency_field='currency_id')
    gosi_salary = fields.Monetary(string='GOSI Liable Salary',
                                  compute='_compute_gosi_salary', store=True,
                                  currency_field='currency_id')

    # Contributions
    employee_contribution = fields.Monetary(string='Employee Contribution (10%)',
                                            compute='_compute_contributions', store=True,
                                            currency_field='currency_id')
    employer_contribution = fields.Monetary(string='Employer Contribution',
                                            compute='_compute_contributions', store=True,
                                            currency_field='currency_id')
    total_contribution = fields.Monetary(string='Total GOSI',
                                         compute='_compute_contributions', store=True,
                                         currency_field='currency_id')

    currency_id = fields.Many2one('res.currency',
                                  default=lambda self: self.env.ref('base.SAR'))
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted to GOSI'),
        ('paid', 'Paid'),
    ], default='draft')

    payslip_id = fields.Many2one('hr.payslip', string='Related Payslip')

    @api.depends('basic_salary', 'housing_allowance')
    def _compute_gosi_salary(self):
        for rec in self:
            # GOSI salary = Basic + Housing, capped at 45,000 SAR
            gosi_base = (rec.basic_salary or 0) + (rec.housing_allowance or 0)
            rec.gosi_salary = min(gosi_base, GOSI_ANNUITY_CEILING)

    @api.depends('gosi_salary', 'nationality_category')
    def _compute_contributions(self):
        for rec in self:
            if rec.nationality_category == 'saudi':
                rec.employee_contribution = rec.gosi_salary * GOSI_SAUDI_EMPLOYEE_RATE
                rec.employer_contribution = rec.gosi_salary * GOSI_SAUDI_EMPLOYER_RATE
            elif rec.nationality_category == 'gcc':
                # GCC treated same as Saudi for GOSI
                rec.employee_contribution = rec.gosi_salary * GOSI_SAUDI_EMPLOYEE_RATE
                rec.employer_contribution = rec.gosi_salary * GOSI_SAUDI_EMPLOYER_RATE
            else:
                # Expat - employer pays 2% occupational hazard only
                rec.employee_contribution = 0
                rec.employer_contribution = rec.gosi_salary * GOSI_EXPAT_EMPLOYER_RATE

            rec.total_contribution = rec.employee_contribution + rec.employer_contribution

    def action_submit_gosi(self):
        for rec in self:
            rec.state = 'submitted'


class GosiReport(models.Model):
    """Monthly GOSI report for bulk submission"""
    _name = 'gosi.monthly.report'
    _description = 'GOSI Monthly Report'
    _order = 'period_date desc'

    name = fields.Char(string='Reference', required=True)
    period_date = fields.Date(string='Period', required=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    contribution_ids = fields.One2many('gosi.contribution', 'payslip_id',
                                       string='Contributions')
    total_employees = fields.Integer(string='Total Employees',
                                     compute='_compute_totals')
    total_saudi = fields.Integer(string='Saudi Employees',
                                 compute='_compute_totals')
    total_expat = fields.Integer(string='Expat Employees',
                                 compute='_compute_totals')
    total_employee_cont = fields.Monetary(string='Total Employee Contributions',
                                          compute='_compute_totals',
                                          currency_field='currency_id')
    total_employer_cont = fields.Monetary(string='Total Employer Contributions',
                                          compute='_compute_totals',
                                          currency_field='currency_id')
    grand_total = fields.Monetary(string='Grand Total',
                                  compute='_compute_totals',
                                  currency_field='currency_id')
    currency_id = fields.Many2one('res.currency',
                                  default=lambda self: self.env.ref('base.SAR'))

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('submitted', 'Submitted to GOSI'),
    ], default='draft')

    @api.depends('contribution_ids')
    def _compute_totals(self):
        for report in self:
            contribs = self.env['gosi.contribution'].search([
                ('period_date', '=', report.period_date),
                ('company_id', '=', report.company_id.id),
            ])
            report.total_employees = len(contribs)
            report.total_saudi = len(contribs.filtered(
                lambda c: c.nationality_category in ['saudi', 'gcc']))
            report.total_expat = len(contribs.filtered(
                lambda c: c.nationality_category == 'expat'))
            report.total_employee_cont = sum(contribs.mapped('employee_contribution'))
            report.total_employer_cont = sum(contribs.mapped('employer_contribution'))
            report.grand_total = report.total_employee_cont + report.total_employer_cont
