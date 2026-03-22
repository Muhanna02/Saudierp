{
    'name': 'Saudi ERP - Accounting & ZATCA',
    'version': '17.0.1.0.0',
    'summary': 'Saudi Arabia Accounting: VAT 15%, ZATCA E-Invoicing (Phase 1 & 2), Zakat',
    'description': """
        Saudi ERP Accounting Module
        ===========================
        - VAT 15% (ضريبة القيمة المضافة)
        - ZATCA E-Invoicing Phase 1 & Phase 2
        - UBL 2.1 / XML invoice generation
        - QR Code generation (TLV encoded)
        - Zakat calculation
        - Saudi Chart of Accounts
        - Withholding Tax (WHT)
        - IFRS-compliant financial reports
        - Arabic invoice templates
        - IBAN validation for Saudi banks
    """,
    'author': 'Saudi ERP Team',
    'website': 'https://saudi-erp.com',
    'category': 'Accounting/Saudi Arabia',
    'license': 'LGPL-3',
    'depends': [
        'saudi_erp_base',
        'account',
        'account_accountant',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/account_tax_data.xml',
        'data/account_chart_template.xml',
        'views/account_move_views.xml',
        'views/zatca_views.xml',
        'views/account_report_views.xml',
        'wizard/zatca_wizard_views.xml',
        'report/invoice_report.xml',
        'report/invoice_template.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
