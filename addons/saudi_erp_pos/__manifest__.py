{
    'name': 'Saudi ERP - Point of Sale',
    'version': '17.0.1.0.0',
    'summary': 'Saudi Arabia POS: VAT receipts, ZATCA QR, Arabic UI, SAR currency',
    'description': """
        Saudi ERP Point of Sale
        =======================
        - ZATCA-compliant receipts with QR code
        - VAT 15% auto-applied
        - Arabic/English bilingual receipt
        - SAR currency display
        - Saudi payment methods (STC Pay, Mada, Apple Pay)
        - Daily sales Z-report
        - Inventory tracking per branch
        - Customer loyalty points
    """,
    'author': 'Saudi ERP Team',
    'website': 'https://saudi-erp.com',
    'category': 'Point of Sale/Saudi Arabia',
    'license': 'LGPL-3',
    'depends': [
        'saudi_erp_accounting',
        'point_of_sale',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/pos_config_views.xml',
        'report/pos_receipt_template.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'saudi_erp_pos/static/src/css/saudi_pos.css',
            'saudi_erp_pos/static/src/js/saudi_pos.js',
        ],
    },
    'installable': True,
    'application': False,
}
