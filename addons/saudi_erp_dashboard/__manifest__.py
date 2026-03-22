{
    'name': 'Saudi ERP - Custom Admin Dashboard',
    'version': '17.0.1.0.0',
    'summary': 'Modern custom admin dashboard theme replacing Odoo default UI',
    'description': """
        Saudi ERP Custom Dashboard
        ==========================
        - Completely replaces Odoo default backend theme
        - Modern dark/light sidebar navigation
        - Real-time KPI cards (Revenue, VAT, Employees, Orders)
        - Interactive charts (Chart.js)
        - ZATCA compliance status widget
        - Saudi calendar widget (Hijri/Gregorian)
        - Multi-company quick switcher
        - Responsive for desktop, tablet, mobile
        - Arabic/English RTL support
        - Subscription/tenant status panel
    """,
    'author': 'Saudi ERP Team',
    'website': 'https://saudi-erp.com',
    'category': 'Themes/Saudi Arabia',
    'license': 'LGPL-3',
    'depends': [
        'saudi_erp_base',
        'web',
        'mail',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/dashboard_views.xml',
        'views/dashboard_menus.xml',
    ],
    'assets': {
        'web.assets_backend': [
            # Fonts
            'https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;500;700&family=Inter:wght@300;400;500;600;700&display=swap',
            # Dashboard Theme CSS
            'saudi_erp_dashboard/static/src/css/dashboard_theme.css',
            'saudi_erp_dashboard/static/src/css/sidebar.css',
            'saudi_erp_dashboard/static/src/css/widgets.css',
            # Dashboard JS
            'saudi_erp_dashboard/static/src/js/dashboard_main.js',
            'saudi_erp_dashboard/static/src/js/kpi_widgets.js',
            'saudi_erp_dashboard/static/src/js/charts.js',
        ],
        'web.assets_frontend': [
            'saudi_erp_dashboard/static/src/css/dashboard_theme.css',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}
