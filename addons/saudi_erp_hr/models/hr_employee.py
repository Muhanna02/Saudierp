from odoo import api, fields, models
from odoo.exceptions import ValidationError
from datetime import date, timedelta
import logging

_logger = logging.getLogger(__name__)


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    # Saudi Employee Classification
    nationality_category = fields.Selection([
        ('saudi', 'Saudi National (مواطن سعودي)'),
        ('gcc', 'GCC National'),
        ('expat', 'Expatriate (وافد)'),
    ], string='Nationality Category', compute='_compute_nationality_category', store=True)

    # Iqama (Residence Permit) - for non-Saudis
    iqama_number = fields.Char(string='Iqama Number (رقم الإقامة)')
    iqama_expiry = fields.Date(string='Iqama Expiry (تاريخ انتهاء الإقامة)')
    iqama_status = fields.Selection([
        ('valid', 'Valid (سارية)'),
        ('expiring_soon', 'Expiring Soon (تنتهي قريباً)'),
        ('expired', 'Expired (منتهية)'),
    ], string='Iqama Status', compute='_compute_iqama_status', store=True)

    # Work Permit
    work_permit_number = fields.Char(string='Work Permit No. (تصريح عمل)')
    work_permit_expiry = fields.Date(string='Work Permit Expiry')

    # Saudi National ID
    saudi_national_id = fields.Char(string='Saudi National ID (هوية وطنية)')
    national_id_expiry = fields.Date(string='National ID Expiry')

    # GOSI
    gosi_number = fields.Char(string='GOSI Number')
    gosi_registered = fields.Boolean(string='GOSI Registered', default=False)

    # Employment Details
    joining_date = fields.Date(string='Joining Date (تاريخ التعيين)')
    probation_end_date = fields.Date(string='Probation End Date (نهاية الاختبار)')
    contract_type = fields.Selection([
        ('unlimited', 'Unlimited Contract (عقد غير محدد المدة)'),
        ('limited', 'Fixed-Term Contract (عقد محدد المدة)'),
    ], string='Contract Type', default='unlimited')
    contract_end_date = fields.Date(string='Contract End Date')

    # Salary Components
    basic_salary = fields.Monetary(string='Basic Salary (الراتب الأساسي)',
                                   currency_field='currency_id')
    housing_allowance = fields.Monetary(string='Housing Allowance (بدل سكن)',
                                        currency_field='currency_id')
    transport_allowance = fields.Monetary(string='Transport Allowance (بدل مواصلات)',
                                          currency_field='currency_id')
    other_allowances = fields.Monetary(string='Other Allowances (بدلات أخرى)',
                                       currency_field='currency_id')
    total_salary = fields.Monetary(string='Total Salary (إجمالي الراتب)',
                                   compute='_compute_total_salary',
                                   currency_field='currency_id')

    currency_id = fields.Many2one('res.currency',
                                  default=lambda self: self.env.ref('base.SAR'))

    # Saudization / Nitaqat
    is_saudi_count = fields.Boolean(string='Count for Saudization (يُحسب في نطاقات)',
                                    default=False)

    # Leave entitlements
    annual_leave_days = fields.Integer(
        string='Annual Leave Days',
        compute='_compute_annual_leave',
        help='21 days for < 5 years, 30 days for >= 5 years (Saudi Labor Law)'
    )

    @api.depends('country_id')
    def _compute_nationality_category(self):
        gcc_countries = ['SA', 'AE', 'KW', 'BH', 'QA', 'OM']
        for emp in self:
            if emp.country_id and emp.country_id.code == 'SA':
                emp.nationality_category = 'saudi'
            elif emp.country_id and emp.country_id.code in gcc_countries:
                emp.nationality_category = 'gcc'
            else:
                emp.nationality_category = 'expat'

    @api.depends('iqama_expiry')
    def _compute_iqama_status(self):
        today = date.today()
        for emp in self:
            if not emp.iqama_expiry:
                emp.iqama_status = False
                continue
            days_left = (emp.iqama_expiry - today).days
            if days_left < 0:
                emp.iqama_status = 'expired'
            elif days_left <= 90:
                emp.iqama_status = 'expiring_soon'
            else:
                emp.iqama_status = 'valid'

    @api.depends('basic_salary', 'housing_allowance', 'transport_allowance', 'other_allowances')
    def _compute_total_salary(self):
        for emp in self:
            emp.total_salary = (
                (emp.basic_salary or 0) +
                (emp.housing_allowance or 0) +
                (emp.transport_allowance or 0) +
                (emp.other_allowances or 0)
            )

    @api.depends('joining_date')
    def _compute_annual_leave(self):
        today = date.today()
        for emp in self:
            if not emp.joining_date:
                emp.annual_leave_days = 21
                continue
            years_of_service = (today - emp.joining_date).days / 365.25
            emp.annual_leave_days = 30 if years_of_service >= 5 else 21

    def _get_years_of_service(self, to_date=None):
        """Calculate years of service from joining date"""
        self.ensure_one()
        if not self.joining_date:
            return 0
        end_date = to_date or date.today()
        delta = end_date - self.joining_date
        return delta.days / 365.25
