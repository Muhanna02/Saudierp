import base64
import hashlib
import json
import struct
from datetime import datetime
from odoo import api, fields, models
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'

    # ZATCA Fields
    zatca_status = fields.Selection([
        ('not_submitted', 'Not Submitted'),
        ('submitted', 'Submitted to ZATCA'),
        ('accepted', 'Accepted by ZATCA'),
        ('rejected', 'Rejected by ZATCA'),
        ('cleared', 'Cleared (Phase 2)'),
        ('reported', 'Reported (Phase 2)'),
    ], string='ZATCA Status', default='not_submitted', copy=False)

    zatca_uuid = fields.Char(string='ZATCA UUID', copy=False)
    zatca_hash = fields.Char(string='Invoice Hash', copy=False)
    zatca_qr_code = fields.Binary(string='QR Code', copy=False)
    zatca_qr_code_str = fields.Char(string='QR Code String', copy=False)
    zatca_xml = fields.Binary(string='ZATCA XML', copy=False, attachment=True)
    zatca_xml_name = fields.Char(string='ZATCA XML Filename', copy=False)
    zatca_response = fields.Text(string='ZATCA Response', copy=False)
    zatca_clearance_status = fields.Char(string='Clearance Status', copy=False)

    # Invoice Type for ZATCA
    zatca_invoice_type = fields.Selection([
        ('388', 'Tax Invoice (فاتورة ضريبية)'),
        ('381', 'Credit Note (إشعار دائن)'),
        ('383', 'Debit Note (إشعار مدين)'),
    ], string='ZATCA Invoice Type', compute='_compute_zatca_invoice_type', store=True)

    # Saudi specific
    invoice_sequence_number = fields.Char(string='Sequential Invoice No.', copy=False)
    supply_date = fields.Date(string='Supply Date (تاريخ التوريد)')
    supply_end_date = fields.Date(string='Supply End Date')

    # Payment method for B2C
    payment_means_code = fields.Selection([
        ('10', 'Cash (نقداً)'),
        ('30', 'Bank Transfer (تحويل بنكي)'),
        ('42', 'Bank Account (حساب بنكي)'),
        ('48', 'Bank Card (بطاقة بنكية)'),
        ('1', 'Instrument Not Defined'),
    ], string='Payment Method', default='10')

    @api.depends('move_type')
    def _compute_zatca_invoice_type(self):
        for move in self:
            if move.move_type == 'out_invoice':
                move.zatca_invoice_type = '388'
            elif move.move_type == 'out_refund':
                move.zatca_invoice_type = '381'
            else:
                move.zatca_invoice_type = '388'

    def _generate_zatca_qr_tlv(self):
        """Generate ZATCA-compliant QR code using TLV encoding"""
        self.ensure_one()
        company = self.company_id

        def tlv_encode(tag, value):
            value_bytes = value.encode('utf-8') if isinstance(value, str) else value
            length = len(value_bytes)
            return bytes([tag]) + bytes([length]) + value_bytes

        invoice_date = self.invoice_date or datetime.now().date()
        invoice_datetime = datetime.combine(invoice_date, datetime.min.time())

        tlv_data = b''
        tlv_data += tlv_encode(1, company.name)
        tlv_data += tlv_encode(2, company.zatca_vat_number or company.vat or '')
        tlv_data += tlv_encode(3, invoice_datetime.strftime('%Y-%m-%dT%H:%M:%SZ'))
        tlv_data += tlv_encode(4, '{:.2f}'.format(self.amount_total))
        tlv_data += tlv_encode(5, '{:.2f}'.format(self.amount_tax))

        qr_b64 = base64.b64encode(tlv_data).decode('utf-8')
        return qr_b64

    def action_generate_zatca_qr(self):
        for move in self:
            if move.move_type not in ['out_invoice', 'out_refund']:
                continue
            move.zatca_qr_code_str = move._generate_zatca_qr_tlv()
            import uuid
            move.zatca_uuid = str(uuid.uuid4())

    def action_submit_zatca(self):
        """Submit invoice to ZATCA (Phase 2 integration)"""
        for move in self:
            if move.zatca_status in ['accepted', 'cleared']:
                raise UserError('Invoice already submitted to ZATCA.')

            move.action_generate_zatca_qr()
            xml_content = move._generate_zatca_xml()
            move.zatca_xml = base64.b64encode(xml_content.encode('utf-8'))
            move.zatca_xml_name = f'invoice_{move.name}.xml'

            company = move.company_id
            if company.zatca_status == 'phase2' and company.zatca_api_url:
                move._call_zatca_api(xml_content)
            else:
                move.zatca_status = 'submitted'
                _logger.info(f'ZATCA Phase 1: Invoice {move.name} XML generated')

    def _generate_zatca_xml(self):
        """Generate ZATCA-compliant UBL 2.1 XML"""
        self.ensure_one()
        company = self.company_id
        partner = self.partner_id
        invoice_date = self.invoice_date or datetime.now().date()

        lines_xml = ''
        for i, line in enumerate(self.invoice_line_ids.filtered(lambda l: not l.display_type), 1):
            tax_amount = sum(t.amount for t in line.tax_ids)
            lines_xml += f"""
        <cac:InvoiceLine>
            <cbc:ID>{i}</cbc:ID>
            <cbc:InvoicedQuantity unitCode="PCE">{line.quantity}</cbc:InvoicedQuantity>
            <cbc:LineExtensionAmount currencyID="SAR">{line.price_subtotal:.2f}</cbc:LineExtensionAmount>
            <cac:Item>
                <cbc:Name>{line.name}</cbc:Name>
            </cac:Item>
            <cac:Price>
                <cbc:PriceAmount currencyID="SAR">{line.price_unit:.2f}</cbc:PriceAmount>
            </cac:Price>
        </cac:InvoiceLine>"""

        xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"
    xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
    xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
    xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2">
    <cbc:UBLVersionID>2.1</cbc:UBLVersionID>
    <cbc:ProfileID>reporting:1.0</cbc:ProfileID>
    <cbc:ID>{self.name}</cbc:ID>
    <cbc:UUID>{self.zatca_uuid}</cbc:UUID>
    <cbc:IssueDate>{invoice_date.strftime('%Y-%m-%d')}</cbc:IssueDate>
    <cbc:IssueTime>00:00:00</cbc:IssueTime>
    <cbc:InvoiceTypeCode name="{self._get_invoice_sub_type()}">{self.zatca_invoice_type}</cbc:InvoiceTypeCode>
    <cbc:DocumentCurrencyCode>SAR</cbc:DocumentCurrencyCode>
    <cbc:TaxCurrencyCode>SAR</cbc:TaxCurrencyCode>
    <cac:AdditionalDocumentReference>
        <cbc:ID>QR</cbc:ID>
        <cac:Attachment>
            <cbc:EmbeddedDocumentBinaryObject mimeCode="text/plain">{self.zatca_qr_code_str}</cbc:EmbeddedDocumentBinaryObject>
        </cac:Attachment>
    </cac:AdditionalDocumentReference>
    <cac:AccountingSupplierParty>
        <cac:Party>
            <cac:PartyName><cbc:Name>{company.name}</cbc:Name></cac:PartyName>
            <cac:PostalAddress>
                <cbc:StreetName>{company.street or ''}</cbc:StreetName>
                <cbc:CityName>{company.city or ''}</cbc:CityName>
                <cbc:CountrySubentity>SA</cbc:CountrySubentity>
                <cac:Country><cbc:IdentificationCode>SA</cbc:IdentificationCode></cac:Country>
            </cac:PostalAddress>
            <cac:PartyTaxScheme>
                <cbc:CompanyID>{company.zatca_vat_number or company.vat or ''}</cbc:CompanyID>
                <cac:TaxScheme><cbc:ID>VAT</cbc:ID></cac:TaxScheme>
            </cac:PartyTaxScheme>
        </cac:Party>
    </cac:AccountingSupplierParty>
    <cac:AccountingCustomerParty>
        <cac:Party>
            <cac:PartyName><cbc:Name>{partner.name}</cbc:Name></cac:PartyName>
            <cac:PartyTaxScheme>
                <cbc:CompanyID>{partner.vat_registration or partner.vat or 'NA'}</cbc:CompanyID>
                <cac:TaxScheme><cbc:ID>VAT</cbc:ID></cac:TaxScheme>
            </cac:PartyTaxScheme>
        </cac:Party>
    </cac:AccountingCustomerParty>
    <cac:TaxTotal>
        <cbc:TaxAmount currencyID="SAR">{self.amount_tax:.2f}</cbc:TaxAmount>
    </cac:TaxTotal>
    <cac:LegalMonetaryTotal>
        <cbc:LineExtensionAmount currencyID="SAR">{self.amount_untaxed:.2f}</cbc:LineExtensionAmount>
        <cbc:TaxExclusiveAmount currencyID="SAR">{self.amount_untaxed:.2f}</cbc:TaxExclusiveAmount>
        <cbc:TaxInclusiveAmount currencyID="SAR">{self.amount_total:.2f}</cbc:TaxInclusiveAmount>
        <cbc:PayableAmount currencyID="SAR">{self.amount_total:.2f}</cbc:PayableAmount>
    </cac:LegalMonetaryTotal>
    {lines_xml}
</Invoice>"""
        return xml

    def _get_invoice_sub_type(self):
        """Return ZATCA invoice subtype (B2B=0100000, B2C=0200000)"""
        partner = self.partner_id
        if partner.vat_registration or partner.vat:
            return '0100000'
        return '0200000'

    def _call_zatca_api(self, xml_content):
        """Call ZATCA Fatoora API for clearance/reporting"""
        import requests
        company = self.company_id
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Accept-Version': 'V2',
        }
        if company.zatca_certificate:
            credentials = base64.b64encode(
                f'{company.zatca_certificate}:{company.zatca_private_key}'.encode()
            ).decode()
            headers['Authorization'] = f'Basic {credentials}'

        payload = {
            'invoiceHash': self.zatca_hash or '',
            'uuid': self.zatca_uuid,
            'invoice': base64.b64encode(xml_content.encode()).decode(),
        }

        try:
            endpoint = f"{company.zatca_api_url}/invoices/clearance/single"
            response = requests.post(endpoint, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            result = response.json()
            self.zatca_response = json.dumps(result, indent=2)
            self.zatca_status = 'cleared'
            self.zatca_clearance_status = result.get('clearanceStatus', '')
        except Exception as e:
            _logger.error(f'ZATCA API Error: {str(e)}')
            self.zatca_response = str(e)
            self.zatca_status = 'rejected'
