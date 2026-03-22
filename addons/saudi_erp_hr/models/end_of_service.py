from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from datetime import date
import logging

_logger = logging.getLogger(__name__)


class EndOfServiceBenefit(models.Model):
    """
    Saudi Labor Law - End of Service Gratuity (مكافأة نهاية الخدمة)
    Article 84 of Saudi Labor Law:
    - Less than 2 years: No entitlement
    - 2-5 years: 1/3 of monthly wage per year
    - 5-10 years: 2/3 of monthly wage per year
    - Over 10 years: Full monthly wage per year
    """
    _name = 'hr.eos.benefit'
    _description = 'End of Service Benefit (مكافأة نهاية الخدمة)'
    _order = 'termination_date desc'

    name = fields.Char(string='Reference', compute='_compute_name', store=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True,
                                  ondelete='restrict')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)

    # Dates
    joining_date = fields.Date(string='Joining Date', related='employee_id.joining_date',
                               store=True)
    termination_date = fields.Date(string='Termination Date', required=True)

    # Service calculation
    years_of_service = fields.Float(string='Years of Service',
                                    compute='_compute_eos', store=True)
    months_of_service = fields.Integer(string='Total Months',
                                       compute='_compute_eos', store=True)

    # Termination reason
    termination_reason = fields.Selection([
        ('resignation', 'Resignation (استقالة)'),
        ('termination_employer', 'Terminated by Employer (فصل من قبل صاحب العمل)'),
        ('contract_end', 'Contract Ended (انتهاء العقد)'),
        ('mutual_agreement', 'Mutual Agreement (اتفاق متبادل)'),
        ('death', 'Death (وفاة)'),
        ('disability', 'Disability (عجز)'),
        ('retirement', 'Retirement (تقاعد)'),
    ], string='Reason for Termination', required=True)

    # Salary basis
    last_basic_salary = fields.Monetary(string='Last Basic Salary (الراتب الأساسي)',
                                        currency_field='currency_id')
    last_housing_allowance = fields.Monetary(string='Housing Allowance (بدل السكن)',
                                             currency_field='currency_id')
    eos_salary_basis = fields.Monetary(string='EOS Salary Basis',
                                       compute='_compute_eos', store=True,
                                       currency_field='currency_id',
                                       help='Basic + Housing for EOS calculation')

    # EOS Amount
    eos_amount = fields.Monetary(string='EOS Gratuity Amount (مكافأة نهاية الخدمة)',
                                 compute='_compute_eos', store=True,
                                 currency_field='currency_id')
    eos_multiplier = fields.Float(string='EOS Multiplier', compute='_compute_eos', store=True)

    # Deductions
    advance_deduction = fields.Monetary(string='Salary Advance Deduction',
                                        currency_field='currency_id')
    other_deductions = fields.Monetary(string='Other Deductions',
                                       currency_field='currency_id')
    net_eos = fields.Monetary(string='Net EOS Payable',
                              compute='_compute_net_eos', store=True,
                              currency_field='currency_id')

    currency_id = fields.Many2one('res.currency',
                                  default=lambda self: self.env.ref('base.SAR'))

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
    ], default='draft')

    notes = fields.Text(string='Notes')

    @api.depends('employee_id', 'termination_date')
    def _compute_name(self):
        for rec in self:
            rec.name = f'EOS/{rec.employee_id.name or "New"}/{rec.termination_date or ""}'

    @api.depends('joining_date', 'termination_date', 'last_basic_salary',
                 'last_housing_allowance', 'termination_reason')
    def _compute_eos(self):
        for rec in self:
            if not rec.joining_date or not rec.termination_date:
                rec.years_of_service = 0
                rec.months_of_service = 0
                rec.eos_salary_basis = 0
                rec.eos_amount = 0
                rec.eos_multiplier = 0
                continue

            # Calculate service duration
            delta = rec.termination_date - rec.joining_date
            total_days = delta.days
            rec.months_of_service = int(total_days / 30.44)
            rec.years_of_service = total_days / 365.25

            # EOS Salary Basis = Basic + Housing
            rec.eos_salary_basis = (rec.last_basic_salary or 0) + (rec.last_housing_allowance or 0)
            monthly_wage = rec.eos_salary_basis

            years = rec.years_of_service

            # Apply Saudi Labor Law Article 84
            if years < 2:
                # No entitlement for less than 2 years (resignation)
                if rec.termination_reason == 'resignation':
                    rec.eos_amount = 0
                    rec.eos_multiplier = 0
                else:
                    # Employer termination: entitled even before 2 years
                    rec.eos_amount = monthly_wage * (total_days / 365.25) * (1/3)
                    rec.eos_multiplier = 1/3
            elif years <= 5:
                rec.eos_multiplier = 1/3
                rec.eos_amount = monthly_wage * years * (1/3)
            elif years <= 10:
                # First 5 years at 1/3, remainder at 2/3
                eos_first_5 = monthly_wage * 5 * (1/3)
                eos_remainder = monthly_wage * (years - 5) * (2/3)
                rec.eos_amount = eos_first_5 + eos_remainder
                rec.eos_multiplier = 2/3
            else:
                # First 5 years at 1/3, next 5 at 2/3, remainder full
                eos_first_5 = monthly_wage * 5 * (1/3)
                eos_next_5 = monthly_wage * 5 * (2/3)
                eos_remainder = monthly_wage * (years - 10) * 1.0
                rec.eos_amount = eos_first_5 + eos_next_5 + eos_remainder
                rec.eos_multiplier = 1.0

            # Resignation reduction (Article 85)
            if rec.termination_reason == 'resignation':
                if 2 <= years < 5:
                    rec.eos_amount *= 1/3
                elif 5 <= years < 10:
                    rec.eos_amount *= 2/3
                # >= 10 years: full amount even for resignation

    @api.depends('eos_amount', 'advance_deduction', 'other_deductions')
    def _compute_net_eos(self):
        for rec in self:
            rec.net_eos = max(
                0,
                (rec.eos_amount or 0) - (rec.advance_deduction or 0) - (rec.other_deductions or 0)
            )

    def action_confirm(self):
        for rec in self:
            if rec.years_of_service < 1:
                raise UserError('Employee must have served at least 1 year for EOS.')
            rec.state = 'confirmed'

    def action_pay(self):
        for rec in self:
            if rec.state != 'confirmed':
                raise UserError('Please confirm EOS before marking as paid.')
            rec.state = 'paid'
            # Update employee status
            rec.employee_id.active = False
