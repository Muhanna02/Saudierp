from odoo import api, fields, models


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    # Saudi payslip additions
    gosi_employee = fields.Monetary(string='GOSI Employee (10%)',
                                    compute='_compute_saudi_deductions',
                                    currency_field='currency_id')
    gosi_employer = fields.Monetary(string='GOSI Employer',
                                    compute='_compute_saudi_deductions',
                                    currency_field='currency_id')
    currency_id = fields.Many2one('res.currency',
                                  default=lambda self: self.env.ref('base.SAR'))
    wps_file_ready = fields.Boolean(string='WPS File Ready', default=False)
    wps_file = fields.Binary(string='WPS File')
    wps_filename = fields.Char(string='WPS Filename')

    @api.depends('employee_id', 'line_ids')
    def _compute_saudi_deductions(self):
        for slip in self:
            emp = slip.employee_id
            if not emp:
                slip.gosi_employee = 0
                slip.gosi_employer = 0
                continue

            gosi_salary = min(
                (emp.basic_salary or 0) + (emp.housing_allowance or 0),
                45000
            )

            if emp.nationality_category in ['saudi', 'gcc']:
                slip.gosi_employee = gosi_salary * 0.10
                slip.gosi_employer = gosi_salary * 0.12
            else:
                slip.gosi_employee = 0
                slip.gosi_employer = gosi_salary * 0.02

    def action_generate_wps(self):
        """Generate WPS (Wage Protection System) file"""
        for slip in self:
            lines = []
            lines.append('EDR|01|{date}|{company}|SAR'.format(
                date=slip.date_to.strftime('%Y%m%d') if slip.date_to else '',
                company=slip.company_id.cr_number or slip.company_id.name
            ))
            lines.append('EMP|{name}|{iban}|{salary}|SAR|{days}'.format(
                name=slip.employee_id.name,
                iban='SA' + '0' * 22,  # Placeholder
                salary='{:.2f}'.format(slip.net_wage),
                days=slip.date_to.day if slip.date_to else 30,
            ))
            wps_content = '\n'.join(lines)
            import base64
            slip.wps_file = base64.b64encode(wps_content.encode('utf-8'))
            slip.wps_filename = f'WPS_{slip.name}_{slip.date_to}.txt'
            slip.wps_file_ready = True
