{
    'name': 'Saudi ERP - HR & Payroll',
    'version': '17.0.1.0.0',
    'summary': 'Saudi HR: GOSI, Iqama, End of Service Benefits, Saudi Labor Law',
    'description': """
        Saudi ERP HR Module
        ===================
        - GOSI (General Organization for Social Insurance)
          * Saudi employees: 10% employee + 12% employer = 22%
          * Non-Saudi employees: 2% employer only
        - Iqama (Residence Permit) tracking and alerts
        - End of Service Benefits (مكافأة نهاية الخدمة)
          per Saudi Labor Law Article 84
        - Saudi payroll structure (SAR)
        - Annual leave calculations (21/30 days)
        - Work permits management
        - Saudization (Nitaqat) tracking
        - Employee performance based on Saudi standards
    """,
    'author': 'Saudi ERP Team',
    'website': 'https://saudi-erp.com',
    'category': 'Human Resources/Saudi Arabia',
    'license': 'LGPL-3',
    'depends': [
        'saudi_erp_base',
        'hr',
        'hr_payroll',
        'hr_attendance',
        'hr_leave',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/hr_payroll_structure.xml',
        'views/hr_employee_views.xml',
        'views/gosi_views.xml',
        'views/eos_views.xml',
        'wizard/eos_wizard_views.xml',
        'wizard/gosi_wizard_views.xml',
        'report/eos_report.xml',
        'report/gosi_report.xml',
    ],
    'installable': True,
    'application': False,
}
