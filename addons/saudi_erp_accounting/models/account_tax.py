from odoo import api, fields, models


class AccountJournalSaudi(models.Model):
    _inherit = 'account.journal'

    # Saudi bank IBAN validation
    saudi_bank_code = fields.Char(string='Saudi Bank Code (4 digits)')

    @api.constrains('bank_acc_number')
    def _validate_saudi_iban(self):
        for journal in self:
            if (journal.bank_acc_number and
                    journal.bank_acc_number.startswith('SA') and
                    len(journal.bank_acc_number) != 24):
                raise models.ValidationError(
                    'Saudi IBAN must be 24 characters (SA + 22 digits).'
                )
