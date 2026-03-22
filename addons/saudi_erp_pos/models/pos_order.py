from odoo import api, fields, models
import base64
import struct


class PosOrder(models.Model):
    _inherit = 'pos.order'

    zatca_qr_code = fields.Char(string='ZATCA QR Code (TLV)', copy=False)
    is_zatca_generated = fields.Boolean(string='ZATCA QR Generated', default=False)

    @api.model
    def create(self, vals):
        order = super().create(vals)
        if order.config_id.zatca_qr_on_receipt:
            order._generate_pos_qr()
        return order

    def _generate_pos_qr(self):
        """Generate ZATCA TLV QR for POS receipt"""
        for order in self:
            company = order.company_id

            def tlv_encode(tag, value):
                value_bytes = value.encode('utf-8') if isinstance(value, str) else value
                return bytes([tag]) + bytes([len(value_bytes)]) + value_bytes

            order_date = order.date_order
            tlv = b''
            tlv += tlv_encode(1, company.name)
            tlv += tlv_encode(2, company.zatca_vat_number or company.vat or '')
            tlv += tlv_encode(3, order_date.strftime('%Y-%m-%dT%H:%M:%SZ') if order_date else '')
            tlv += tlv_encode(4, '{:.2f}'.format(order.amount_total))
            tlv += tlv_encode(5, '{:.2f}'.format(order.amount_tax))

            order.zatca_qr_code = base64.b64encode(tlv).decode('utf-8')
            order.is_zatca_generated = True


class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    # Arabic product name on receipt
    product_name_ar = fields.Char(
        related='product_id.name',
        string='Product Name Arabic',
    )
