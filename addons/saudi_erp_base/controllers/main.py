from odoo import http
from odoo.http import request


class SaudiERPBase(http.Controller):

    @http.route('/saudi_erp/company_info', type='json', auth='user')
    def get_company_info(self):
        company = request.env.company
        return {
            'name': company.name,
            'vat': company.vat,
            'cr_number': company.cr_number,
            'zatca_status': company.zatca_status,
            'subscription_plan': company.subscription_plan,
            'subscription_expiry': str(company.subscription_expiry) if company.subscription_expiry else None,
        }
