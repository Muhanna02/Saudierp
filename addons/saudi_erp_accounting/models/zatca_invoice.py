from odoo import api, fields, models


class ZatcaLog(models.Model):
    """ZATCA submission log"""
    _name = 'zatca.log'
    _description = 'ZATCA Submission Log'
    _order = 'create_date desc'

    name = fields.Char(string='Reference', required=True)
    move_id = fields.Many2one('account.move', string='Invoice', ondelete='cascade')
    submission_type = fields.Selection([
        ('clearance', 'Clearance (Phase 2 B2B)'),
        ('reporting', 'Reporting (Phase 2 B2C)'),
        ('phase1', 'Phase 1 Generation'),
    ], string='Submission Type')
    status = fields.Selection([
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('pending', 'Pending'),
    ], string='Status')
    request_payload = fields.Text(string='Request')
    response_payload = fields.Text(string='Response')
    error_message = fields.Text(string='Error')
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env.company)


class AccountTaxSaudi(models.Model):
    _inherit = 'account.tax'

    zatca_category_code = fields.Selection([
        ('S', 'Standard Rate (15%)'),
        ('Z', 'Zero Rate (0%)'),
        ('E', 'Exempt'),
        ('O', 'Out of Scope'),
    ], string='ZATCA Tax Category', default='S')
