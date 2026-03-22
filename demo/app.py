"""
Saudi ERP - Live Demo Server
Runs the full UI demo without Odoo/Docker
"""
from flask import Flask, render_template, jsonify, request, redirect, url_for
from datetime import date, datetime
import random
import json

app = Flask(__name__)
app.secret_key = 'saudi-erp-demo-2024'

# ── Fake demo data ──────────────────────────────────────────────────────────

DEMO_COMPANY = {
    'name': 'Al-Faisal Trading Co. (شركة الفيصل التجارية)',
    'cr_number': '1010234567',
    'vat_number': '300123456700003',
    'zatca_status': 'phase2',
    'subscription_plan': 'Professional',
    'subscription_expiry': '2025-12-31',
    'city': 'Riyadh',
}

MONTHS_AR = ['يناير','فبراير','مارس','أبريل','مايو','يونيو',
              'يوليو','أغسطس','سبتمبر','أكتوبر','نوفمبر','ديسمبر']

def make_monthly_data():
    base = [185000, 210000, 198000, 225000, 243000, 285000]
    labels = ['Oct 2024','Nov 2024','Dec 2024','Jan 2025','Feb 2025','Mar 2025']
    vat    = [v * 0.15 for v in base]
    return labels, base, vat

RECENT_INVOICES = [
    {'id':1, 'name':'INV/2025/00312', 'partner':'Aramco Trading Ltd.', 'date':'2025-03-20', 'amount':48500.00, 'vat':7275.00, 'status':'paid', 'zatca':'cleared'},
    {'id':2, 'name':'INV/2025/00311', 'partner':'STC Solutions Co.', 'date':'2025-03-19', 'amount':12750.00, 'vat':1912.50, 'status':'pending', 'zatca':'submitted'},
    {'id':3, 'name':'INV/2025/00310', 'partner':'Almarai Company', 'date':'2025-03-18', 'amount':33200.00, 'vat':4980.00, 'status':'paid', 'zatca':'cleared'},
    {'id':4, 'name':'INV/2025/00309', 'partner':'SABIC Industrial', 'date':'2025-03-17', 'amount':67890.00, 'vat':10183.50, 'status':'overdue', 'zatca':'not_submitted'},
    {'id':5, 'name':'INV/2025/00308', 'partner':'Jarir Bookstore', 'date':'2025-03-16', 'amount':9450.00, 'vat':1417.50, 'status':'paid', 'zatca':'cleared'},
    {'id':6, 'name':'INV/2025/00307', 'partner':'Al-Rajhi Trading', 'date':'2025-03-15', 'amount':24600.00, 'vat':3690.00, 'status':'pending', 'zatca':'submitted'},
    {'id':7, 'name':'INV/2025/00306', 'partner':'Mobily Telecom', 'date':'2025-03-14', 'amount':18300.00, 'vat':2745.00, 'status':'paid', 'zatca':'cleared'},
    {'id':8, 'name':'INV/2025/00305', 'partner':'Red Sea Mall', 'date':'2025-03-13', 'amount':41200.00, 'vat':6180.00, 'status':'paid', 'zatca':'cleared'},
]

EMPLOYEES = [
    {'name':'محمد العمري', 'name_en':'Mohammed Al-Omari', 'nationality':'Saudi', 'dept':'Finance', 'basic':12000, 'iqama':None, 'iqama_exp':None, 'status':'active'},
    {'name':'فهد الحربي', 'name_en':'Fahad Al-Harbi', 'nationality':'Saudi', 'dept':'HR', 'basic':10000, 'iqama':None, 'iqama_exp':None, 'status':'active'},
    {'name':'سارة القحطاني', 'name_en':'Sara Al-Qahtani', 'nationality':'Saudi', 'dept':'Sales', 'basic':9500, 'iqama':None, 'iqama_exp':None, 'status':'active'},
    {'name':'Raj Kumar', 'name_en':'Raj Kumar', 'nationality':'Expat', 'dept':'IT', 'basic':8000, 'iqama':'2484123456', 'iqama_exp':'2025-04-15', 'status':'expiring'},
    {'name':'Ahmed Hassan', 'name_en':'Ahmed Hassan', 'nationality':'Expat', 'dept':'Operations', 'basic':7500, 'iqama':'2484987654', 'iqama_exp':'2025-06-30', 'status':'active'},
    {'name':'John Smith', 'name_en':'John Smith', 'nationality':'Expat', 'dept':'Engineering', 'basic':15000, 'iqama':'2484567890', 'iqama_exp':'2025-03-01', 'status':'expired'},
    {'name':'خالد السبيعي', 'name_en':'Khalid Al-Subaie', 'nationality':'Saudi', 'dept':'Procurement', 'basic':11000, 'iqama':None, 'iqama_exp':None, 'status':'active'},
    {'name':'Maria Santos', 'name_en':'Maria Santos', 'nationality':'Expat', 'dept':'Admin', 'basic':6000, 'iqama':'2484111222', 'iqama_exp':'2025-09-15', 'status':'active'},
]

TENANTS = [
    {'code':'ALP7K2', 'company':'شركة الألفا التجارية', 'plan':'Professional', 'status':'active', 'users':23, 'expiry':'2025-12-31', 'email':'admin@alpha.sa'},
    {'code':'BET3X9', 'company':'Beta Solutions Ltd', 'plan':'Starter', 'status':'active', 'users':7, 'expiry':'2025-06-30', 'email':'it@beta.sa'},
    {'code':'GAM1Q5', 'company':'Gamma Retail Co.', 'plan':'Trial', 'status':'active', 'users':3, 'expiry':'2025-04-05', 'email':'info@gamma.sa'},
    {'code':'DEL8W4', 'company':'Delta Logistics', 'plan':'Enterprise', 'status':'active', 'users':85, 'expiry':'2026-01-01', 'email':'erp@delta.sa'},
    {'code':'EPS2Y7', 'company':'Epsilon Foods', 'plan':'Starter', 'status':'suspended', 'users':5, 'expiry':'2025-03-01', 'email':'admin@epsilon.sa'},
]

# ── Routes ──────────────────────────────────────────────────────────────────

@app.route('/')
def homepage():
    return render_template('homepage.html', company=DEMO_COMPANY)

@app.route('/pricing')
def pricing():
    return render_template('pricing.html')

@app.route('/register')
def register():
    plan = request.args.get('plan', 'trial')
    return render_template('register.html', plan=plan)

@app.route('/register/submit', methods=['POST'])
def register_submit():
    data = request.form
    import uuid
    tenant_code = str(uuid.uuid4())[:6].upper()
    return render_template('register_success.html', data=data, tenant_code=tenant_code)

# ── Admin Dashboard ──────────────────────────────────────────────────────────

@app.route('/admin')
@app.route('/admin/dashboard')
def admin_dashboard():
    labels, revenue, vat = make_monthly_data()
    saudi_emp = sum(1 for e in EMPLOYEES if e['nationality'] == 'Saudi')
    expat_emp = len(EMPLOYEES) - saudi_emp
    expiring  = sum(1 for e in EMPLOYEES if e['status'] == 'expiring')
    expired   = sum(1 for e in EMPLOYEES if e['status'] == 'expired')
    saudization = round(saudi_emp / len(EMPLOYEES) * 100, 1)

    return render_template('dashboard.html',
        company=DEMO_COMPANY,
        revenue_month=285000,
        vat_month=42750,
        revenue_growth=17.3,
        outstanding_amount=121290,
        outstanding_count=3,
        pending_zatca=2,
        total_employees=len(EMPLOYEES),
        saudi_employees=saudi_emp,
        expat_employees=expat_emp,
        expiring_iqama=expiring,
        expired_iqama=expired,
        saudization_pct=saudization,
        invoices=RECENT_INVOICES,
        chart_labels=json.dumps(labels),
        chart_revenue=json.dumps(revenue),
        chart_vat=json.dumps(vat),
        saudi_count=saudi_emp,
        expat_count=expat_emp,
        active_page='dashboard',
    )

@app.route('/admin/accounting')
def admin_accounting():
    return render_template('accounting.html',
        company=DEMO_COMPANY,
        invoices=RECENT_INVOICES,
        active_page='accounting',
    )

@app.route('/admin/hr')
def admin_hr():
    saudi_emp = sum(1 for e in EMPLOYEES if e['nationality'] == 'Saudi')
    saudization = round(saudi_emp / len(EMPLOYEES) * 100, 1)
    return render_template('hr.html',
        company=DEMO_COMPANY,
        employees=EMPLOYEES,
        saudization_pct=saudization,
        active_page='hr',
    )

@app.route('/admin/pos')
def admin_pos():
    return render_template('pos.html',
        company=DEMO_COMPANY,
        active_page='pos',
    )

@app.route('/admin/tenants')
def admin_tenants():
    return render_template('tenants.html',
        company=DEMO_COMPANY,
        tenants=TENANTS,
        active_page='tenants',
    )

@app.route('/admin/zatca')
def admin_zatca():
    return render_template('zatca.html',
        company=DEMO_COMPANY,
        invoices=RECENT_INVOICES,
        active_page='zatca',
    )

# ── API endpoints ────────────────────────────────────────────────────────────

@app.route('/api/dashboard')
def api_dashboard():
    labels, revenue, vat = make_monthly_data()
    return jsonify({
        'revenue_month': 285000,
        'vat_month': 42750,
        'growth': 17.3,
        'labels': labels,
        'revenue': revenue,
        'vat': vat,
    })

if __name__ == '__main__':
    print("=" * 50)
    print("  Saudi ERP Demo Server")
    print("  نظام إدارة موارد المؤسسات السعودية")
    print("=" * 50)
    print("  🌐 Homepage:   http://localhost:8888")
    print("  📊 Dashboard:  http://localhost:8888/admin")
    print("  💰 Pricing:    http://localhost:8888/pricing")
    print("  📝 Register:   http://localhost:8888/register")
    print("=" * 50)
    app.run(host='0.0.0.0', port=8888, debug=False)
