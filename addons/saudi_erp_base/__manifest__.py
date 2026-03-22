{
    'name': 'Saudi ERP - Base',
    'version': '17.0.1.0.0',
    'summary': 'Base module for Saudi ERP customizations',
    'description': """
        Saudi ERP Base Module
        =====================
        Core configurations for Saudi Arabia ERP:
        - Saudi Arabia localization settings
        - Hijri calendar support
        - Arabic/English bilingual support
        - Multi-company SaaS setup
        - Saudi regulatory compliance base
    """,
    'author': 'Saudi ERP Team',
    'website': 'https://saudi-erp.com',
    'category': 'Localization/Saudi Arabia',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'base_setup',
        'mail',
        'web',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/groups.xml',
        'data/res_country_data.xml',
        'data/res_lang_data.xml',
        'views/res_company_views.xml',
        'views/res_partner_views.xml',
        'views/menu_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'saudi_erp_base/static/src/css/saudi_base.css',
            'saudi_erp_base/static/src/js/saudi_base.js',
        ],
    },
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
    'sequence': 1,
}
