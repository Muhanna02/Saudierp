from odoo import api, fields, models
from odoo.exceptions import ValidationError
import uuid
import logging

_logger = logging.getLogger(__name__)


class SaudiTenant(models.Model):
    """SaaS Tenant management for Saudi ERP multi-company setup"""
    _name = 'saudi.tenant'
    _description = 'Saudi ERP Tenant'
    _order = 'create_date desc'

    name = fields.Char(string='Company Name', required=True)
    name_ar = fields.Char(string='Company Name (Arabic)')
    tenant_code = fields.Char(
        string='Tenant Code',
        required=True,
        readonly=True,
        default=lambda self: str(uuid.uuid4())[:8].upper()
    )
    company_id = fields.Many2one('res.company', string='Odoo Company')
    admin_user_id = fields.Many2one('res.users', string='Admin User')
    admin_email = fields.Char(string='Admin Email', required=True)
    admin_phone = fields.Char(string='Admin Phone')
    cr_number = fields.Char(string='Commercial Registration No.')
    vat_number = fields.Char(string='VAT Number')

    plan = fields.Selection([
        ('trial', 'Trial'),
        ('starter', 'Starter'),
        ('professional', 'Professional'),
        ('enterprise', 'Enterprise'),
    ], string='Plan', default='trial', required=True)

    status = fields.Selection([
        ('pending', 'Pending Setup'),
        ('active', 'Active'),
        ('suspended', 'Suspended'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='pending')

    subscription_start = fields.Date(string='Start Date')
    subscription_expiry = fields.Date(string='Expiry Date')
    modules_installed = fields.Many2many(
        'ir.module.module',
        string='Installed Modules'
    )

    # Usage tracking
    user_count = fields.Integer(string='Active Users', compute='_compute_user_count')
    invoice_count = fields.Integer(string='Invoices This Month', compute='_compute_invoice_count')

    @api.depends('company_id')
    def _compute_user_count(self):
        for tenant in self:
            if tenant.company_id:
                tenant.user_count = self.env['res.users'].search_count([
                    ('company_ids', 'in', [tenant.company_id.id]),
                    ('active', '=', True),
                ])
            else:
                tenant.user_count = 0

    @api.depends('company_id')
    def _compute_invoice_count(self):
        for tenant in self:
            if tenant.company_id:
                tenant.invoice_count = self.env['account.move'].search_count([
                    ('company_id', '=', tenant.company_id.id),
                    ('move_type', 'in', ['out_invoice', 'out_refund']),
                ])
            else:
                tenant.invoice_count = 0

    def action_activate(self):
        self.status = 'active'

    def action_suspend(self):
        self.status = 'suspended'
