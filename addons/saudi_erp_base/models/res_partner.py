from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # Saudi ID fields
    national_id = fields.Char(
        string='National ID / Iqama No.',
        help='Saudi National ID (هوية وطنية) or Iqama Number (إقامة)'
    )
    id_type = fields.Selection([
        ('national_id', 'National ID (هوية وطنية)'),
        ('iqama', 'Iqama (إقامة)'),
        ('passport', 'Passport (جواز سفر)'),
        ('company', 'Company (شركة)'),
        ('gcc', 'GCC ID'),
    ], string='ID Type', default='national_id')
    id_expiry = fields.Date(string='ID Expiry Date')

    # VAT / Business
    vat_registration = fields.Char(
        string='VAT Number (ZATCA)',
        help='15-digit VAT registration number'
    )
    cr_number = fields.Char(string='Commercial Registration No.')

    # Arabic name
    name_ar = fields.Char(string='Arabic Name (الاسم بالعربي)')

    # Saudi address fields
    district = fields.Char(string='District / Neighborhood (الحي)')
    building_number = fields.Char(string='Building Number')
    additional_number = fields.Char(string='Additional Number')

    @api.constrains('vat_registration')
    def _check_vat_number(self):
        for partner in self:
            if partner.vat_registration and len(partner.vat_registration) != 15:
                raise models.ValidationError(
                    'VAT Registration number must be exactly 15 digits.'
                )
