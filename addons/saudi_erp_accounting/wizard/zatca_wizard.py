from odoo import api, fields, models


class ZatcaOnboardingWizard(models.TransientModel):
    _name = 'zatca.onboarding.wizard'
    _description = 'ZATCA Onboarding Wizard'

    phase = fields.Selection([
        ('phase1', 'Phase 1 - Invoice Generation'),
        ('phase2', 'Phase 2 - ZATCA Integration'),
    ], string='ZATCA Phase', required=True, default='phase1')

    vat_number = fields.Char(string='VAT Registration Number', required=True)
    otp = fields.Char(string='OTP (from Fatoora Portal)')
    environment = fields.Selection([
        ('sandbox', 'Sandbox (Testing)'),
        ('production', 'Production'),
    ], string='Environment', default='sandbox')

    def action_configure_zatca(self):
        company = self.env.company
        company.zatca_vat_number = self.vat_number
        company.zatca_status = self.phase

        if self.phase == 'phase2':
            company.zatca_otp = self.otp
            if self.environment == 'sandbox':
                company.zatca_api_url = 'https://gw-fatoora.zatca.gov.sa/e-invoicing/developer-portal'
            else:
                company.zatca_api_url = 'https://gw-fatoora.zatca.gov.sa/e-invoicing/core'

        return {'type': 'ir.actions.act_window_close'}
