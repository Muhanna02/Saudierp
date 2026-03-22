from odoo import http
from odoo.http import request


class SaudiERPPortal(http.Controller):

    @http.route('/', type='http', auth='public', website=True)
    def homepage(self, **kwargs):
        return request.render('saudi_erp_portal.homepage', {})

    @http.route('/features', type='http', auth='public', website=True)
    def features_page(self, **kwargs):
        features = [
            {
                'icon': '📊',
                'title': 'Saudi Accounting',
                'title_ar': 'المحاسبة السعودية',
                'desc': 'ZATCA e-invoicing, VAT 15%, Saudi chart of accounts',
                'desc_ar': 'الفوترة الإلكترونية زاتكا، ضريبة 15%، دليل الحسابات',
            },
            {
                'icon': '👥',
                'title': 'Saudi HR & Payroll',
                'title_ar': 'الموارد البشرية والرواتب',
                'desc': 'GOSI, End of Service, Iqama tracking, WPS payroll',
                'desc_ar': 'التأمينات الاجتماعية، نهاية الخدمة، متابعة الإقامات',
            },
            {
                'icon': '🛒',
                'title': 'Saudi Point of Sale',
                'title_ar': 'نقطة البيع السعودية',
                'desc': 'Mada, STC Pay, ZATCA receipts, Arabic UI',
                'desc_ar': 'مدى، STC Pay، إيصالات زاتكا، واجهة عربية',
            },
            {
                'icon': '🏛️',
                'title': 'ZATCA Compliance',
                'title_ar': 'الامتثال لهيئة زاتكا',
                'desc': 'Phase 1 & 2 e-invoicing, QR codes, XML/UBL 2.1',
                'desc_ar': 'المرحلة 1 و 2، رموز QR، XML/UBL 2.1',
            },
            {
                'icon': '📈',
                'title': 'Custom Dashboard',
                'title_ar': 'لوحة تحكم مخصصة',
                'desc': 'Real-time KPIs, charts, alerts in a modern admin UI',
                'desc_ar': 'مؤشرات الأداء الفورية، الرسوم البيانية، التنبيهات',
            },
            {
                'icon': '🌐',
                'title': 'Arabic / English',
                'title_ar': 'عربي / إنجليزي',
                'desc': 'Full RTL Arabic support and bilingual documents',
                'desc_ar': 'دعم كامل للغة العربية والمستندات ثنائية اللغة',
            },
        ]
        return request.render('saudi_erp_portal.features_page', {'features': features})
