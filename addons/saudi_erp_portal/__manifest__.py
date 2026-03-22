{
    'name': 'Saudi ERP - SaaS Registration Portal',
    'version': '17.0.1.0.0',
    'summary': 'Public portal for companies to register and subscribe to Saudi ERP',
    'description': """
        Saudi ERP SaaS Portal
        =====================
        - Public-facing registration page (saudi-erp.com style)
        - Plan selection (Trial, Starter, Professional, Enterprise)
        - Automatic tenant provisioning
        - Email confirmation with admin credentials
        - Payment integration (HyperPay, PayTabs)
        - Subscription management portal
        - Arabic/English bilingual
    """,
    'author': 'Saudi ERP Team',
    'website': 'https://saudi-erp.com',
    'category': 'Website/Saudi Arabia',
    'license': 'LGPL-3',
    'depends': [
        'saudi_erp_base',
        'website',
        'portal',
        'mail',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/portal_templates.xml',
        'views/registration_templates.xml',
        'views/pricing_templates.xml',
        'data/mail_templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'saudi_erp_portal/static/src/css/portal.css',
            'saudi_erp_portal/static/src/js/portal.js',
        ],
    },
    'installable': True,
    'application': False,
}
