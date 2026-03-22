from odoo import http
from odoo.http import request
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
import json


class SaudiDashboard(http.Controller):

    @http.route('/saudi_erp/dashboard/data', type='json', auth='user')
    def get_dashboard_data(self):
        """Main dashboard KPI data endpoint"""
        company = request.env.company
        today = date.today()
        month_start = today.replace(day=1)
        last_month_start = (month_start - relativedelta(months=1))
        last_month_end = month_start - timedelta(days=1)
        year_start = today.replace(month=1, day=1)

        AccountMove = request.env['account.move']
        HrEmployee = request.env['hr.employee']

        # Revenue This Month
        invoices_month = AccountMove.search([
            ('company_id', '=', company.id),
            ('move_type', '=', 'out_invoice'),
            ('state', '=', 'posted'),
            ('invoice_date', '>=', month_start),
            ('invoice_date', '<=', today),
        ])
        revenue_month = sum(invoices_month.mapped('amount_untaxed'))
        vat_month = sum(invoices_month.mapped('amount_tax'))

        # Revenue Last Month
        invoices_last_month = AccountMove.search([
            ('company_id', '=', company.id),
            ('move_type', '=', 'out_invoice'),
            ('state', '=', 'posted'),
            ('invoice_date', '>=', last_month_start),
            ('invoice_date', '<=', last_month_end),
        ])
        revenue_last_month = sum(invoices_last_month.mapped('amount_untaxed'))

        # Revenue Growth
        growth = 0
        if revenue_last_month > 0:
            growth = ((revenue_month - revenue_last_month) / revenue_last_month) * 100

        # Employees
        total_employees = HrEmployee.search_count([
            ('company_id', '=', company.id),
            ('active', '=', True),
        ])
        saudi_employees = HrEmployee.search_count([
            ('company_id', '=', company.id),
            ('active', '=', True),
            ('nationality_category', '=', 'saudi'),
        ])
        expat_employees = total_employees - saudi_employees

        # Saudization percentage
        saudization_pct = (saudi_employees / total_employees * 100) if total_employees else 0

        # Pending ZATCA invoices
        pending_zatca = AccountMove.search_count([
            ('company_id', '=', company.id),
            ('move_type', 'in', ['out_invoice', 'out_refund']),
            ('state', '=', 'posted'),
            ('zatca_status', '=', 'not_submitted'),
        ])

        # Outstanding invoices
        outstanding = AccountMove.search([
            ('company_id', '=', company.id),
            ('move_type', '=', 'out_invoice'),
            ('payment_state', 'in', ['not_paid', 'partial']),
            ('state', '=', 'posted'),
        ])
        outstanding_amount = sum(outstanding.mapped('amount_residual'))

        # Monthly revenue chart (last 6 months)
        monthly_revenue = []
        monthly_labels = []
        for i in range(5, -1, -1):
            m_start = (month_start - relativedelta(months=i))
            m_end = m_start + relativedelta(months=1) - timedelta(days=1)
            m_invoices = AccountMove.search([
                ('company_id', '=', company.id),
                ('move_type', '=', 'out_invoice'),
                ('state', '=', 'posted'),
                ('invoice_date', '>=', m_start),
                ('invoice_date', '<=', m_end),
            ])
            monthly_revenue.append(round(sum(m_invoices.mapped('amount_untaxed')), 2))
            monthly_labels.append(m_start.strftime('%b %Y'))

        # Expiring Iqamas
        expiring_soon = 0
        expired = 0
        try:
            expiring_soon = HrEmployee.search_count([
                ('company_id', '=', company.id),
                ('iqama_status', '=', 'expiring_soon'),
            ])
            expired = HrEmployee.search_count([
                ('company_id', '=', company.id),
                ('iqama_status', '=', 'expired'),
            ])
        except Exception:
            pass

        return {
            'company': {
                'name': company.name,
                'zatca_status': company.zatca_status,
                'subscription_plan': company.subscription_plan,
                'subscription_expiry': str(company.subscription_expiry) if company.subscription_expiry else None,
                'cr_number': company.cr_number,
                'vat_number': company.zatca_vat_number or company.vat,
            },
            'kpis': {
                'revenue_month': round(revenue_month, 2),
                'vat_month': round(vat_month, 2),
                'revenue_growth': round(growth, 1),
                'outstanding_amount': round(outstanding_amount, 2),
                'outstanding_count': len(outstanding),
                'pending_zatca': pending_zatca,
            },
            'employees': {
                'total': total_employees,
                'saudi': saudi_employees,
                'expat': expat_employees,
                'saudization_pct': round(saudization_pct, 1),
                'expiring_iqama': expiring_soon,
                'expired_iqama': expired,
            },
            'charts': {
                'monthly_labels': monthly_labels,
                'monthly_revenue': monthly_revenue,
            },
        }

    @http.route('/saudi_erp/dashboard/recent_invoices', type='json', auth='user')
    def get_recent_invoices(self, limit=10):
        """Get recent invoices for dashboard"""
        company = request.env.company
        invoices = request.env['account.move'].search([
            ('company_id', '=', company.id),
            ('move_type', '=', 'out_invoice'),
            ('state', '=', 'posted'),
        ], limit=limit, order='invoice_date desc')

        return [{
            'id': inv.id,
            'name': inv.name,
            'partner': inv.partner_id.name,
            'date': str(inv.invoice_date),
            'amount': round(inv.amount_total, 2),
            'payment_state': inv.payment_state,
            'zatca_status': inv.zatca_status,
        } for inv in invoices]

    @http.route('/saudi_erp/dashboard/saudization', type='json', auth='user')
    def get_saudization_data(self):
        """Get Nitaqat/Saudization data"""
        company = request.env.company
        HrEmployee = request.env['hr.employee']

        by_nationality = {}
        employees = HrEmployee.search([
            ('company_id', '=', company.id),
            ('active', '=', True),
        ])
        for emp in employees:
            nat = emp.nationality_category or 'unknown'
            by_nationality[nat] = by_nationality.get(nat, 0) + 1

        return {
            'breakdown': by_nationality,
            'total': len(employees),
        }
