from odoo import http
from odoo.http import request
from datetime import date, timedelta
import logging
import uuid

_logger = logging.getLogger(__name__)

PLAN_PRICES = {
    'trial': 0,
    'starter': 500,
    'professional': 1500,
    'enterprise': 0,  # Custom pricing
}

PLAN_FEATURES = {
    'trial': {'users': 5, 'modules': ['accounting', 'hr'], 'days': 14},
    'starter': {'users': 10, 'modules': ['accounting', 'hr', 'pos'], 'days': 30},
    'professional': {'users': 50, 'modules': ['accounting', 'hr', 'pos', 'inventory'], 'days': 30},
    'enterprise': {'users': 999, 'modules': 'all', 'days': 365},
}


class SaudiERPRegistration(http.Controller):

    @http.route('/register', type='http', auth='public', website=True)
    def registration_page(self, plan='trial', **kwargs):
        return request.render('saudi_erp_portal.registration_page', {
            'plan': plan,
            'plans': PLAN_FEATURES,
            'prices': PLAN_PRICES,
        })

    @http.route('/register/submit', type='http', auth='public', website=True, methods=['POST'], csrf=True)
    def submit_registration(self, **post):
        """Process company registration"""
        # Validate required fields
        required = ['company_name', 'admin_email', 'admin_phone', 'plan']
        errors = {}
        for field in required:
            if not post.get(field):
                errors[field] = f'{field} is required'

        if errors:
            return request.render('saudi_erp_portal.registration_page', {
                'errors': errors,
                'values': post,
                'plan': post.get('plan', 'trial'),
                'plans': PLAN_FEATURES,
                'prices': PLAN_PRICES,
            })

        plan = post.get('plan', 'trial')
        plan_info = PLAN_FEATURES.get(plan, PLAN_FEATURES['trial'])

        # Create tenant record
        tenant_code = str(uuid.uuid4())[:8].upper()

        try:
            tenant = request.env['saudi.tenant'].sudo().create({
                'name': post['company_name'],
                'name_ar': post.get('company_name_ar', ''),
                'admin_email': post['admin_email'],
                'admin_phone': post.get('admin_phone', ''),
                'cr_number': post.get('cr_number', ''),
                'vat_number': post.get('vat_number', ''),
                'plan': plan,
                'tenant_code': tenant_code,
                'status': 'pending',
                'subscription_start': date.today(),
                'subscription_expiry': date.today() + timedelta(days=plan_info['days']),
            })

            # Send confirmation email
            template = request.env.ref(
                'saudi_erp_portal.mail_template_registration_confirm', raise_if_not_found=False
            )
            if template:
                template.sudo().send_mail(tenant.id, force_send=True)

            return request.render('saudi_erp_portal.registration_success', {
                'tenant': tenant,
                'plan': plan,
                'plan_info': plan_info,
            })

        except Exception as e:
            _logger.error(f'Registration failed: {e}')
            return request.render('saudi_erp_portal.registration_page', {
                'error': 'Registration failed. Please try again.',
                'values': post,
                'plan': plan,
                'plans': PLAN_FEATURES,
                'prices': PLAN_PRICES,
            })

    @http.route('/pricing', type='http', auth='public', website=True)
    def pricing_page(self, **kwargs):
        return request.render('saudi_erp_portal.pricing_page', {
            'plans': PLAN_FEATURES,
            'prices': PLAN_PRICES,
        })

    @http.route('/my/subscription', type='http', auth='user', website=True)
    def my_subscription(self, **kwargs):
        tenant = request.env['saudi.tenant'].sudo().search([
            ('admin_email', '=', request.env.user.email),
        ], limit=1)
        return request.render('saudi_erp_portal.subscription_portal', {
            'tenant': tenant,
        })
