from odoo import api, fields, models


class PosConfig(models.Model):
    _inherit = 'pos.config'

    # Saudi POS settings
    saudi_vat_enabled = fields.Boolean(
        string='Apply VAT 15% (ZATCA)',
        default=True,
        help='Automatically apply 15% VAT on all POS transactions'
    )
    zatca_qr_on_receipt = fields.Boolean(
        string='Print ZATCA QR on Receipt',
        default=True
    )
    arabic_receipt = fields.Boolean(
        string='Bilingual Receipt (Arabic/English)',
        default=True
    )
    branch_name = fields.Char(string='Branch Name (اسم الفرع)')
    branch_name_ar = fields.Char(string='Branch Name Arabic (الاسم بالعربي)')

    # Saudi Payment Methods
    stc_pay_enabled = fields.Boolean(string='STC Pay', default=False)
    mada_enabled = fields.Boolean(string='Mada', default=True)
    apple_pay_enabled = fields.Boolean(string='Apple Pay', default=False)
    tabby_enabled = fields.Boolean(string='Tabby (BNPL)', default=False)

    # Z-Report settings
    z_report_auto = fields.Boolean(
        string='Auto Z-Report at Session Close',
        default=True
    )

    # Loyalty
    loyalty_enabled = fields.Boolean(string='Customer Loyalty Program', default=False)
    loyalty_points_per_sar = fields.Float(
        string='Points per SAR',
        default=1.0
    )


class PosPaymentMethod(models.Model):
    _inherit = 'pos.payment.method'

    saudi_payment_type = fields.Selection([
        ('cash', 'Cash (نقداً)'),
        ('mada', 'Mada (مدى)'),
        ('visa', 'Visa / Mastercard'),
        ('stc_pay', 'STC Pay'),
        ('apple_pay', 'Apple Pay'),
        ('tabby', 'Tabby'),
        ('bank_transfer', 'Bank Transfer (تحويل بنكي)'),
    ], string='Saudi Payment Type')
