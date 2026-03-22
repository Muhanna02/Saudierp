from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    # Saudi Business Registration
    cr_number = fields.Char(
        string='Commercial Registration No.',
        help='Saudi Arabia Commercial Registration Number (السجل التجاري)'
    )
    unified_national_number = fields.Char(
        string='Unified National Number (UNN)',
        help='الرقم الوطني الموحد'
    )
    gosi_registration = fields.Char(
        string='GOSI Registration No.',
        help='General Organization for Social Insurance registration number'
    )
    chamber_membership = fields.Char(
        string='Chamber of Commerce Membership'
    )

    # ZATCA (Zakat, Tax and Customs Authority)
    zatca_vat_number = fields.Char(
        string='VAT Registration No. (ZATCA)',
        help='رقم تسجيل ضريبة القيمة المضافة'
    )
    zatca_status = fields.Selection([
        ('not_registered', 'Not Registered'),
        ('phase1', 'Phase 1 - Generation'),
        ('phase2', 'Phase 2 - Integration'),
    ], string='ZATCA E-Invoicing Phase', default='not_registered')
    zatca_api_url = fields.Char(string='ZATCA API URL')
    zatca_certificate = fields.Text(string='ZATCA Certificate (Base64)')
    zatca_private_key = fields.Text(string='ZATCA Private Key (Base64)')
    zatca_otp = fields.Char(string='ZATCA OTP (One-Time Password)')

    # SaaS Subscription
    subscription_plan = fields.Selection([
        ('trial', 'Trial (14 Days)'),
        ('starter', 'Starter - 500 SAR/month'),
        ('professional', 'Professional - 1,500 SAR/month'),
        ('enterprise', 'Enterprise - Custom'),
    ], string='Subscription Plan', default='trial')
    subscription_start = fields.Date(string='Subscription Start')
    subscription_expiry = fields.Date(string='Subscription Expiry')
    max_users = fields.Integer(string='Max Users', default=5)
    tenant_code = fields.Char(string='Tenant Code', readonly=True)

    # Saudi Locale
    hijri_calendar = fields.Boolean(
        string='Use Hijri Calendar',
        default=True,
        help='Display Hijri (Islamic) calendar alongside Gregorian'
    )
    saudi_timezone = fields.Selection([
        ('Asia/Riyadh', 'Arabia Standard Time (AST) - Riyadh'),
    ], string='Saudi Timezone', default='Asia/Riyadh')

    @api.model
    def _get_saudi_company_defaults(self):
        return {
            'country_id': self.env.ref('base.sa').id,
            'currency_id': self.env.ref('base.SAR').id,
        }
