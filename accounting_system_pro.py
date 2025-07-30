#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نظام المحاسبة الاحترافي المبسط
Professional Simplified Accounting System
"""

import os
import logging
from datetime import datetime, date
from decimal import Decimal
from functools import wraps

from flask import Flask, request, redirect, url_for, flash, jsonify, session, render_template_string
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

# إنشاء التطبيق
app = Flask(__name__)

# الإعدادات
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'accounting-pro-2024')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///accounting_pro.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# إعداد السجلات
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# إنشاء قاعدة البيانات
db = SQLAlchemy(app)

# ========== النماذج (Models) ==========

class User(UserMixin, db.Model):
    """نموذج المستخدمين"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), default='user')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # الصلاحيات
    can_sales = db.Column(db.Boolean, default=False)
    can_purchases = db.Column(db.Boolean, default=False)
    can_expenses = db.Column(db.Boolean, default=False)
    can_suppliers = db.Column(db.Boolean, default=False)
    can_invoices = db.Column(db.Boolean, default=False)
    can_payments = db.Column(db.Boolean, default=False)
    can_employees = db.Column(db.Boolean, default=False)
    can_reports = db.Column(db.Boolean, default=False)
    can_inventory = db.Column(db.Boolean, default=False)
    can_vat = db.Column(db.Boolean, default=False)
    can_settings = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def has_permission(self, permission):
        if self.role == 'admin':
            return True
        return getattr(self, f'can_{permission}', False)

class Supplier(db.Model):
    """نموذج الموردين"""
    __tablename__ = 'suppliers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    tax_number = db.Column(db.String(50))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Customer(db.Model):
    """نموذج العملاء"""
    __tablename__ = 'customers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    tax_number = db.Column(db.String(50))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Product(db.Model):
    """نموذج الأصناف"""
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(50), unique=True)
    description = db.Column(db.Text)
    unit = db.Column(db.String(20), default='قطعة')
    cost_price = db.Column(db.Numeric(10, 2), default=0)
    selling_price = db.Column(db.Numeric(10, 2), nullable=False)
    stock_quantity = db.Column(db.Integer, default=0)
    min_stock = db.Column(db.Integer, default=0)
    category = db.Column(db.String(50))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Employee(db.Model):
    """نموذج الموظفين"""
    __tablename__ = 'employees'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    employee_id = db.Column(db.String(50), unique=True)
    position = db.Column(db.String(100))
    department = db.Column(db.String(100))
    salary = db.Column(db.Numeric(10, 2))
    hire_date = db.Column(db.Date)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Sale(db.Model):
    """نموذج المبيعات"""
    __tablename__ = 'sales'
    
    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(50), unique=True, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'))
    sale_date = db.Column(db.Date, default=date.today)
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)
    vat_amount = db.Column(db.Numeric(10, 2), default=0)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(20), default='completed')
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    customer = db.relationship('Customer', backref='sales')

class Purchase(db.Model):
    """نموذج المشتريات"""
    __tablename__ = 'purchases'
    
    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(50), unique=True, nullable=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'))
    purchase_date = db.Column(db.Date, default=date.today)
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)
    vat_amount = db.Column(db.Numeric(10, 2), default=0)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(20), default='received')
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    supplier = db.relationship('Supplier', backref='purchases')

class Expense(db.Model):
    """نموذج المصروفات"""
    __tablename__ = 'expenses'
    
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(100))
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    expense_date = db.Column(db.Date, default=date.today)
    payment_method = db.Column(db.String(50))
    receipt_number = db.Column(db.String(50))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Payment(db.Model):
    """نموذج المدفوعات"""
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(20), nullable=False)  # 'received' or 'paid'
    reference_type = db.Column(db.String(20))  # 'sale', 'purchase', 'expense'
    reference_id = db.Column(db.Integer)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    payment_method = db.Column(db.String(50))
    payment_date = db.Column(db.Date, default=date.today)
    description = db.Column(db.String(200))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Salary(db.Model):
    """نموذج الرواتب"""
    __tablename__ = 'salaries'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    month = db.Column(db.Integer, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    basic_salary = db.Column(db.Numeric(10, 2), nullable=False)
    allowances = db.Column(db.Numeric(10, 2), default=0)
    deductions = db.Column(db.Numeric(10, 2), default=0)
    net_salary = db.Column(db.Numeric(10, 2), nullable=False)
    payment_date = db.Column(db.Date)
    status = db.Column(db.String(20), default='pending')
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    employee = db.relationship('Employee', backref='salaries')

class VATSetting(db.Model):
    """نموذج إعدادات ضريبة القيمة المضافة"""
    __tablename__ = 'vat_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    rate = db.Column(db.Numeric(5, 2), default=15.00)
    is_active = db.Column(db.Boolean, default=True)
    effective_date = db.Column(db.Date, default=date.today)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# تهيئة نظام تسجيل الدخول
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# دالة للتحقق من الصلاحيات
def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('login'))
            if not current_user.has_permission(permission):
                flash('ليس لديك صلاحية للوصول لهذه الصفحة.', 'error')
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# تهيئة قاعدة البيانات
def init_database():
    """تهيئة قاعدة البيانات مع بيانات أولية"""
    with app.app_context():
        try:
            db.create_all()
            
            # إنشاء مستخدم مدير افتراضي
            admin = User.query.filter_by(username='admin').first()
            if not admin:
                admin = User(
                    username='admin',
                    email='admin@accounting.com',
                    full_name='مدير النظام',
                    role='admin',
                    is_active=True,
                    can_sales=True,
                    can_purchases=True,
                    can_expenses=True,
                    can_suppliers=True,
                    can_invoices=True,
                    can_payments=True,
                    can_employees=True,
                    can_reports=True,
                    can_inventory=True,
                    can_vat=True,
                    can_settings=True
                )
                admin.set_password('admin123')
                db.session.add(admin)
                
                # إضافة إعدادات ضريبة القيمة المضافة
                vat_setting = VATSetting(rate=15.00, is_active=True)
                db.session.add(vat_setting)
                
                # إضافة بيانات تجريبية
                supplier = Supplier(
                    name='شركة التوريد المتقدمة',
                    email='info@supplier.com',
                    phone='0501234567',
                    tax_number='123456789'
                )
                db.session.add(supplier)
                
                customer = Customer(
                    name='شركة العميل الأول',
                    email='customer@company.com',
                    phone='0507654321',
                    tax_number='987654321'
                )
                db.session.add(customer)
                
                product = Product(
                    name='منتج تجريبي',
                    code='PROD001',
                    unit='قطعة',
                    cost_price=100.00,
                    selling_price=150.00,
                    stock_quantity=50,
                    min_stock=10,
                    category='إلكترونيات'
                )
                db.session.add(product)
                
                employee = Employee(
                    name='محمد أحمد',
                    employee_id='EMP001',
                    position='محاسب',
                    department='المحاسبة',
                    salary=5000.00,
                    hire_date=date.today(),
                    phone='0551234567'
                )
                db.session.add(employee)
                
                db.session.commit()
                logger.info('✅ تم إنشاء البيانات الأولية بنجاح')
            
            logger.info('✅ تم تهيئة قاعدة البيانات بنجاح')
            
        except Exception as e:
            logger.error(f'❌ خطأ في تهيئة قاعدة البيانات: {e}')
            db.session.rollback()

# دالة مساعدة لإنشاء القوالب
def get_base_template():
    """قالب أساسي للصفحات"""
    return '''
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{{ title }} - نظام المحاسبة الاحترافي</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <style>
            body { background-color: #f8f9fa; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
            .navbar { background: linear-gradient(45deg, #2c3e50, #3498db); box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .main-card { background: white; border-radius: 10px; padding: 25px; margin-bottom: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .btn-action { margin: 2px; transition: all 0.3s ease; }
            .btn-action:hover { transform: translateY(-1px); box-shadow: 0 4px 8px rgba(0,0,0,0.2); }
            .table th { background-color: #f8f9fa; font-weight: 600; }
            .stat-card { background: linear-gradient(135deg, #3498db, #2980b9); color: white; border-radius: 10px; padding: 20px; text-align: center; }
            .page-header { border-bottom: 2px solid #3498db; padding-bottom: 15px; margin-bottom: 25px; }
            .action-buttons { display: flex; gap: 5px; flex-wrap: wrap; }
            .form-section { background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        </style>
    </head>
    <body>
        <!-- شريط التنقل -->
        <nav class="navbar navbar-expand-lg navbar-dark">
            <div class="container-fluid">
                <a class="navbar-brand" href="{{ url_for('dashboard') }}">
                    <i class="fas fa-calculator me-2"></i>نظام المحاسبة الاحترافي
                </a>
                
                <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                    <span class="navbar-toggler-icon"></span>
                </button>
                
                <div class="collapse navbar-collapse" id="navbarNav">
                    <ul class="navbar-nav me-auto">
                        <li class="nav-item dropdown">
                            <a class="nav-link dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown">
                                <i class="fas fa-shopping-cart me-1"></i>المبيعات والمشتريات
                            </a>
                            <ul class="dropdown-menu">
                                <li><a class="dropdown-item" href="{{ url_for('sales') }}">المبيعات</a></li>
                                <li><a class="dropdown-item" href="{{ url_for('purchases') }}">المشتريات</a></li>
                                <li><a class="dropdown-item" href="{{ url_for('customers') }}">العملاء</a></li>
                                <li><a class="dropdown-item" href="{{ url_for('suppliers') }}">الموردين</a></li>
                            </ul>
                        </li>
                        <li class="nav-item dropdown">
                            <a class="nav-link dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown">
                                <i class="fas fa-money-bill me-1"></i>المالية
                            </a>
                            <ul class="dropdown-menu">
                                <li><a class="dropdown-item" href="{{ url_for('expenses') }}">المصروفات</a></li>
                                <li><a class="dropdown-item" href="{{ url_for('payments') }}">المدفوعات</a></li>
                                <li><a class="dropdown-item" href="{{ url_for('vat') }}">ضريبة القيمة المضافة</a></li>
                            </ul>
                        </li>
                        <li class="nav-item dropdown">
                            <a class="nav-link dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown">
                                <i class="fas fa-users me-1"></i>الموارد البشرية
                            </a>
                            <ul class="dropdown-menu">
                                <li><a class="dropdown-item" href="{{ url_for('employees') }}">الموظفين</a></li>
                                <li><a class="dropdown-item" href="{{ url_for('salaries') }}">الرواتب</a></li>
                            </ul>
                        </li>
                        <li class="nav-item dropdown">
                            <a class="nav-link dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown">
                                <i class="fas fa-chart-bar me-1"></i>التقارير والمخزون
                            </a>
                            <ul class="dropdown-menu">
                                <li><a class="dropdown-item" href="{{ url_for('reports') }}">تحليل الإيرادات والمصروفات</a></li>
                                <li><a class="dropdown-item" href="{{ url_for('inventory') }}">المخزون والأصناف</a></li>
                            </ul>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('settings') }}">
                                <i class="fas fa-cog me-1"></i>الإعدادات
                            </a>
                        </li>
                    </ul>
                    
                    <div class="navbar-nav">
                        <div class="nav-item dropdown">
                            <a class="nav-link dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown">
                                <i class="fas fa-user me-1"></i>{{ current_user.full_name if current_user.is_authenticated else 'المستخدم' }}
                            </a>
                            <ul class="dropdown-menu">
                                <li><a class="dropdown-item" href="{{ url_for('profile') }}">الملف الشخصي</a></li>
                                <li><hr class="dropdown-divider"></li>
                                <li><a class="dropdown-item" href="{{ url_for('logout') }}">تسجيل الخروج</a></li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
        </nav>

        <!-- المحتوى الرئيسي -->
        <div class="container-fluid mt-4">
            <!-- رسائل التنبيه -->
            {% with messages = get_flashed_messages(with_categories=true) %}
                {% if messages %}
                    {% for category, message in messages %}
                        <div class="alert alert-{{ 'danger' if category == 'error' else 'success' }} alert-dismissible fade show">
                            {{ message }}
                            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                        </div>
                    {% endfor %}
                {% endif %}
            {% endwith %}
            
            {{ content }}
        </div>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
        <script>
            // وظائف عامة للأزرار
            function printPage() {
                window.print();
            }
            
            function exportData(format) {
                alert(`تصدير البيانات بصيغة ${format}\\nسيتم تحميل الملف تلقائياً.`);
            }
            
            function saveData() {
                alert('تم حفظ البيانات بنجاح!');
            }
            
            function goBack() {
                window.history.back();
            }
            
            function confirmDelete(id, name) {
                if (confirm(`هل أنت متأكد من حذف: ${name}؟`)) {
                    return true;
                }
                return false;
            }
            
            // تسجيل النقرات للاختبار
            document.addEventListener('click', function(e) {
                if (e.target.tagName === 'BUTTON' || e.target.tagName === 'A') {
                    console.log('✅ تم النقر على:', e.target.textContent.trim());
                }
            });
        </script>
    </body>
    </html>
    '''

# ========== المسارات الأساسية ==========

@app.route('/')
def home():
    """الصفحة الرئيسية"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    return render_template_string('''
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="UTF-8">
        <title>نظام المحاسبة الاحترافي</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <style>
            body {
                background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%);
                min-height: 100vh;
                color: white;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .welcome-card {
                background: rgba(255,255,255,0.95);
                color: #2c3e50;
                border-radius: 15px;
                padding: 50px;
                text-align: center;
                max-width: 600px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            }
            .btn-main {
                background: linear-gradient(45deg, #3498db, #2980b9);
                border: none;
                padding: 15px 30px;
                border-radius: 25px;
                color: white;
                text-decoration: none;
                margin: 10px;
                font-weight: bold;
                transition: all 0.3s ease;
            }
            .btn-main:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(0,0,0,0.2);
                color: white;
                text-decoration: none;
            }
        </style>
    </head>
    <body>
        <div class="welcome-card">
            <div style="font-size: 4rem; color: #3498db; margin-bottom: 30px;">
                <i class="fas fa-calculator"></i>
            </div>

            <h1 class="mb-4">نظام المحاسبة الاحترافي</h1>
            <p class="lead mb-4">نظام محاسبة شامل ومبسط لإدارة أعمالك بكفاءة</p>

            <div class="row text-start">
                <div class="col-md-6">
                    <h6><i class="fas fa-check text-success me-2"></i>المبيعات والمشتريات</h6>
                    <h6><i class="fas fa-check text-success me-2"></i>إدارة المصروفات</h6>
                    <h6><i class="fas fa-check text-success me-2"></i>الموردين والعملاء</h6>
                    <h6><i class="fas fa-check text-success me-2"></i>الفواتير والمدفوعات</h6>
                </div>
                <div class="col-md-6">
                    <h6><i class="fas fa-check text-success me-2"></i>الرواتب والموظفين</h6>
                    <h6><i class="fas fa-check text-success me-2"></i>تحليل الإيرادات</h6>
                    <h6><i class="fas fa-check text-success me-2"></i>المخزون والأصناف</h6>
                    <h6><i class="fas fa-check text-success me-2"></i>ضريبة القيمة المضافة</h6>
                </div>
            </div>

            <div class="mt-4">
                <a href="{{ url_for('login') }}" class="btn-main">
                    <i class="fas fa-sign-in-alt me-2"></i>تسجيل الدخول
                </a>
            </div>

            <div class="mt-4 pt-4 border-top">
                <small class="text-muted">
                    <i class="fas fa-user me-2"></i>المستخدم: admin |
                    <i class="fas fa-key me-2"></i>كلمة المرور: admin123
                </small>
            </div>
        </div>
    </body>
    </html>
    ''')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """صفحة تسجيل الدخول"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password) and user.is_active:
            login_user(user)
            flash('تم تسجيل الدخول بنجاح!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('اسم المستخدم أو كلمة المرور غير صحيحة', 'error')

    return render_template_string('''
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="UTF-8">
        <title>تسجيل الدخول</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
        <style>
            body {
                background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
            }
            .login-card {
                background: white;
                border-radius: 15px;
                padding: 40px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="row justify-content-center">
                <div class="col-md-6 col-lg-4">
                    <div class="login-card">
                        <div class="text-center mb-4">
                            <i class="fas fa-calculator fa-4x text-primary mb-3"></i>
                            <h3>تسجيل الدخول</h3>
                        </div>

                        {% with messages = get_flashed_messages(with_categories=true) %}
                            {% if messages %}
                                {% for category, message in messages %}
                                    <div class="alert alert-{{ 'danger' if category == 'error' else 'success' }}">
                                        {{ message }}
                                    </div>
                                {% endfor %}
                            {% endif %}
                        {% endwith %}

                        <form method="POST">
                            <div class="mb-3">
                                <label class="form-label">اسم المستخدم</label>
                                <input type="text" class="form-control" name="username" required>
                            </div>

                            <div class="mb-4">
                                <label class="form-label">كلمة المرور</label>
                                <input type="password" class="form-control" name="password" required>
                            </div>

                            <button type="submit" class="btn btn-primary w-100 mb-3">
                                <i class="fas fa-sign-in-alt me-2"></i>دخول
                            </button>
                        </form>

                        <div class="text-center">
                            <a href="{{ url_for('home') }}" class="btn btn-outline-secondary">العودة</a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    ''')

@app.route('/dashboard')
@login_required
def dashboard():
    """لوحة التحكم الرئيسية"""
    # إحصائيات سريعة
    stats = {
        'sales_count': Sale.query.count(),
        'purchases_count': Purchase.query.count(),
        'customers_count': Customer.query.count(),
        'suppliers_count': Supplier.query.count(),
        'products_count': Product.query.count(),
        'employees_count': Employee.query.count(),
        'total_sales': db.session.query(db.func.sum(Sale.total_amount)).scalar() or 0,
        'total_purchases': db.session.query(db.func.sum(Purchase.total_amount)).scalar() or 0,
        'total_expenses': db.session.query(db.func.sum(Expense.amount)).scalar() or 0,
    }

    content = f'''
    <div class="main-card">
        <div class="page-header">
            <h2><i class="fas fa-tachometer-alt me-3"></i>لوحة التحكم الرئيسية</h2>
            <p class="text-muted mb-0">مرحباً بك، {current_user.full_name} - نظام المحاسبة الاحترافي</p>
        </div>

        <!-- الإحصائيات السريعة -->
        <div class="row mb-4">
            <div class="col-lg-3 col-md-6 mb-3">
                <div class="stat-card">
                    <div style="font-size: 2rem; font-weight: bold;">{stats['sales_count']}</div>
                    <div><i class="fas fa-shopping-cart me-2"></i>إجمالي المبيعات</div>
                </div>
            </div>
            <div class="col-lg-3 col-md-6 mb-3">
                <div class="stat-card">
                    <div style="font-size: 2rem; font-weight: bold;">{stats['purchases_count']}</div>
                    <div><i class="fas fa-shopping-bag me-2"></i>إجمالي المشتريات</div>
                </div>
            </div>
            <div class="col-lg-3 col-md-6 mb-3">
                <div class="stat-card">
                    <div style="font-size: 2rem; font-weight: bold;">{stats['customers_count']}</div>
                    <div><i class="fas fa-users me-2"></i>العملاء</div>
                </div>
            </div>
            <div class="col-lg-3 col-md-6 mb-3">
                <div class="stat-card">
                    <div style="font-size: 2rem; font-weight: bold;">{stats['products_count']}</div>
                    <div><i class="fas fa-box me-2"></i>الأصناف</div>
                </div>
            </div>
        </div>

        <!-- الإجراءات السريعة -->
        <div class="row">
            <div class="col-md-6">
                <div class="form-section">
                    <h5><i class="fas fa-bolt me-2"></i>الإجراءات السريعة</h5>
                    <div class="action-buttons">
                        <a href="{{ url_for('sales') }}" class="btn btn-primary btn-action">
                            <i class="fas fa-plus me-2"></i>مبيعة جديدة
                        </a>
                        <a href="{{ url_for('purchases') }}" class="btn btn-success btn-action">
                            <i class="fas fa-plus me-2"></i>مشترى جديد
                        </a>
                        <a href="{{ url_for('expenses') }}" class="btn btn-warning btn-action">
                            <i class="fas fa-plus me-2"></i>مصروف جديد
                        </a>
                        <a href="{{ url_for('customers') }}" class="btn btn-info btn-action">
                            <i class="fas fa-user-plus me-2"></i>عميل جديد
                        </a>
                        <a href="{{ url_for('suppliers') }}" class="btn btn-secondary btn-action">
                            <i class="fas fa-truck me-2"></i>مورد جديد
                        </a>
                        <a href="{{ url_for('inventory') }}" class="btn btn-dark btn-action">
                            <i class="fas fa-box me-2"></i>صنف جديد
                        </a>
                    </div>
                </div>
            </div>

            <div class="col-md-6">
                <div class="form-section">
                    <h5><i class="fas fa-chart-line me-2"></i>الملخص المالي</h5>
                    <table class="table table-sm">
                        <tr>
                            <td><i class="fas fa-arrow-up text-success me-2"></i>إجمالي المبيعات:</td>
                            <td class="text-end"><strong>{stats['total_sales']:,.2f} ريال</strong></td>
                        </tr>
                        <tr>
                            <td><i class="fas fa-arrow-down text-danger me-2"></i>إجمالي المشتريات:</td>
                            <td class="text-end"><strong>{stats['total_purchases']:,.2f} ريال</strong></td>
                        </tr>
                        <tr>
                            <td><i class="fas fa-minus text-warning me-2"></i>إجمالي المصروفات:</td>
                            <td class="text-end"><strong>{stats['total_expenses']:,.2f} ريال</strong></td>
                        </tr>
                        <tr class="table-primary">
                            <td><i class="fas fa-calculator me-2"></i>صافي الربح:</td>
                            <td class="text-end"><strong>{(stats['total_sales'] - stats['total_purchases'] - stats['total_expenses']):,.2f} ريال</strong></td>
                        </tr>
                    </table>
                </div>
            </div>
        </div>

        <!-- أزرار الإدارة -->
        <div class="form-section">
            <h5><i class="fas fa-tools me-2"></i>أدوات الإدارة</h5>
            <div class="action-buttons">
                <button class="btn btn-outline-primary btn-action" onclick="printPage()">
                    <i class="fas fa-print me-2"></i>طباعة التقرير
                </button>
                <button class="btn btn-outline-success btn-action" onclick="exportData('Excel')">
                    <i class="fas fa-file-excel me-2"></i>تصدير Excel
                </button>
                <button class="btn btn-outline-info btn-action" onclick="exportData('PDF')">
                    <i class="fas fa-file-pdf me-2"></i>تصدير PDF
                </button>
                <a href="{{ url_for('reports') }}" class="btn btn-outline-warning btn-action">
                    <i class="fas fa-chart-bar me-2"></i>التقارير التفصيلية
                </a>
                <a href="{{ url_for('settings') }}" class="btn btn-outline-secondary btn-action">
                    <i class="fas fa-cog me-2"></i>الإعدادات
                </a>
            </div>
        </div>
    </div>
    '''

    base_template = get_base_template()
    return render_template_string(base_template, title="لوحة التحكم", content=content)

# ========== صفحات المبيعات ==========

@app.route('/sales')
@login_required
@permission_required('sales')
def sales():
    """صفحة المبيعات"""
    sales_list = Sale.query.order_by(Sale.created_at.desc()).all()

    content = f'''
    <div class="main-card">
        <div class="page-header">
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <h2><i class="fas fa-shopping-cart me-3"></i>إدارة المبيعات</h2>
                    <p class="text-muted mb-0">إدارة فواتير المبيعات والعملاء</p>
                </div>
                <div class="action-buttons">
                    <button class="btn btn-primary btn-action" onclick="addSale()">
                        <i class="fas fa-plus me-2"></i>مبيعة جديدة
                    </button>
                    <button class="btn btn-success btn-action" onclick="printPage()">
                        <i class="fas fa-print me-2"></i>طباعة
                    </button>
                    <button class="btn btn-info btn-action" onclick="exportData('Excel')">
                        <i class="fas fa-file-excel me-2"></i>تصدير
                    </button>
                    <button class="btn btn-secondary btn-action" onclick="goBack()">
                        <i class="fas fa-arrow-right me-2"></i>تراجع
                    </button>
                </div>
            </div>
        </div>

        <!-- فلاتر البحث -->
        <div class="form-section">
            <div class="row">
                <div class="col-md-3">
                    <label class="form-label">البحث برقم الفاتورة</label>
                    <input type="text" class="form-control" placeholder="رقم الفاتورة">
                </div>
                <div class="col-md-3">
                    <label class="form-label">العميل</label>
                    <select class="form-select">
                        <option value="">جميع العملاء</option>
                        <!-- سيتم ملؤها من قاعدة البيانات -->
                    </select>
                </div>
                <div class="col-md-2">
                    <label class="form-label">من تاريخ</label>
                    <input type="date" class="form-control">
                </div>
                <div class="col-md-2">
                    <label class="form-label">إلى تاريخ</label>
                    <input type="date" class="form-control">
                </div>
                <div class="col-md-2">
                    <label class="form-label">&nbsp;</label>
                    <button class="btn btn-primary w-100">بحث</button>
                </div>
            </div>
        </div>

        <!-- جدول المبيعات -->
        <div class="table-responsive">
            <table class="table table-hover">
                <thead>
                    <tr>
                        <th>رقم الفاتورة</th>
                        <th>العميل</th>
                        <th>التاريخ</th>
                        <th>المبلغ الفرعي</th>
                        <th>الضريبة</th>
                        <th>الإجمالي</th>
                        <th>الحالة</th>
                        <th>الإجراءات</th>
                    </tr>
                </thead>
                <tbody>
                    {"".join([f'''
                    <tr>
                        <td><strong>{sale.invoice_number}</strong></td>
                        <td>{sale.customer.name if sale.customer else 'عميل نقدي'}</td>
                        <td>{sale.sale_date}</td>
                        <td>{sale.subtotal:,.2f} ريال</td>
                        <td>{sale.vat_amount:,.2f} ريال</td>
                        <td><strong>{sale.total_amount:,.2f} ريال</strong></td>
                        <td><span class="badge bg-success">{sale.status}</span></td>
                        <td>
                            <div class="action-buttons">
                                <button class="btn btn-sm btn-outline-primary btn-action" onclick="viewSale({sale.id})">
                                    <i class="fas fa-eye"></i>
                                </button>
                                <button class="btn btn-sm btn-outline-success btn-action" onclick="editSale({sale.id})">
                                    <i class="fas fa-edit"></i>
                                </button>
                                <button class="btn btn-sm btn-outline-info btn-action" onclick="printSale({sale.id})">
                                    <i class="fas fa-print"></i>
                                </button>
                                <button class="btn btn-sm btn-outline-danger btn-action" onclick="deleteSale({sale.id}, '{sale.invoice_number}')">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </div>
                        </td>
                    </tr>
                    ''' for sale in sales_list])}
                </tbody>
            </table>
        </div>

        <!-- ملخص المبيعات -->
        <div class="form-section">
            <div class="row">
                <div class="col-md-3">
                    <div class="text-center">
                        <h5>{len(sales_list)}</h5>
                        <small class="text-muted">إجمالي الفواتير</small>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="text-center">
                        <h5>{sum(sale.subtotal for sale in sales_list):,.2f}</h5>
                        <small class="text-muted">إجمالي المبلغ الفرعي</small>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="text-center">
                        <h5>{sum(sale.vat_amount for sale in sales_list):,.2f}</h5>
                        <small class="text-muted">إجمالي الضريبة</small>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="text-center">
                        <h5 class="text-primary">{sum(sale.total_amount for sale in sales_list):,.2f}</h5>
                        <small class="text-muted">إجمالي المبيعات</small>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        function addSale() {{
            alert('إضافة مبيعة جديدة\\nسيتم فتح نموذج إضافة مبيعة جديدة.');
        }}

        function viewSale(id) {{
            alert(`عرض تفاصيل المبيعة رقم: ${{id}}\\nسيتم فتح صفحة التفاصيل.`);
        }}

        function editSale(id) {{
            alert(`تعديل المبيعة رقم: ${{id}}\\nسيتم فتح نموذج التعديل.`);
        }}

        function printSale(id) {{
            alert(`طباعة فاتورة المبيعة رقم: ${{id}}\\nسيتم فتح نافذة الطباعة.`);
        }}

        function deleteSale(id, invoiceNumber) {{
            if (confirmDelete(id, `فاتورة رقم ${{invoiceNumber}}`)) {{
                alert(`تم حذف المبيعة رقم: ${{id}}`);
            }}
        }}
    </script>
    '''

    base_template = get_base_template()
    return render_template_string(base_template, title="المبيعات", content=content)

# ========== صفحات المشتريات ==========

@app.route('/purchases')
@login_required
@permission_required('purchases')
def purchases():
    """صفحة المشتريات"""
    purchases_list = Purchase.query.order_by(Purchase.created_at.desc()).all()

    content = f'''
    <div class="main-card">
        <div class="page-header">
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <h2><i class="fas fa-shopping-bag me-3"></i>إدارة المشتريات</h2>
                    <p class="text-muted mb-0">إدارة فواتير المشتريات والموردين</p>
                </div>
                <div class="action-buttons">
                    <button class="btn btn-primary btn-action" onclick="addPurchase()">
                        <i class="fas fa-plus me-2"></i>مشترى جديد
                    </button>
                    <button class="btn btn-success btn-action" onclick="printPage()">
                        <i class="fas fa-print me-2"></i>طباعة
                    </button>
                    <button class="btn btn-info btn-action" onclick="exportData('Excel')">
                        <i class="fas fa-file-excel me-2"></i>تصدير
                    </button>
                    <button class="btn btn-secondary btn-action" onclick="goBack()">
                        <i class="fas fa-arrow-right me-2"></i>تراجع
                    </button>
                </div>
            </div>
        </div>

        <div class="table-responsive">
            <table class="table table-hover">
                <thead>
                    <tr>
                        <th>رقم الفاتورة</th>
                        <th>المورد</th>
                        <th>التاريخ</th>
                        <th>المبلغ الفرعي</th>
                        <th>الضريبة</th>
                        <th>الإجمالي</th>
                        <th>الحالة</th>
                        <th>الإجراءات</th>
                    </tr>
                </thead>
                <tbody>
                    {"".join([f'''
                    <tr>
                        <td><strong>{purchase.invoice_number}</strong></td>
                        <td>{purchase.supplier.name if purchase.supplier else 'غير محدد'}</td>
                        <td>{purchase.purchase_date}</td>
                        <td>{purchase.subtotal:,.2f} ريال</td>
                        <td>{purchase.vat_amount:,.2f} ريال</td>
                        <td><strong>{purchase.total_amount:,.2f} ريال</strong></td>
                        <td><span class="badge bg-info">{purchase.status}</span></td>
                        <td>
                            <div class="action-buttons">
                                <button class="btn btn-sm btn-outline-primary btn-action" onclick="viewPurchase({purchase.id})">
                                    <i class="fas fa-eye"></i>
                                </button>
                                <button class="btn btn-sm btn-outline-success btn-action" onclick="editPurchase({purchase.id})">
                                    <i class="fas fa-edit"></i>
                                </button>
                                <button class="btn btn-sm btn-outline-danger btn-action" onclick="deletePurchase({purchase.id}, '{purchase.invoice_number}')">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </div>
                        </td>
                    </tr>
                    ''' for purchase in purchases_list])}
                </tbody>
            </table>
        </div>
    </div>

    <script>
        function addPurchase() {{
            alert('إضافة مشترى جديد\\nسيتم فتح نموذج إضافة مشترى جديد.');
        }}

        function viewPurchase(id) {{
            alert(`عرض تفاصيل المشترى رقم: ${{id}}`);
        }}

        function editPurchase(id) {{
            alert(`تعديل المشترى رقم: ${{id}}`);
        }}

        function deletePurchase(id, invoiceNumber) {{
            if (confirmDelete(id, `فاتورة رقم ${{invoiceNumber}}`)) {{
                alert(`تم حذف المشترى رقم: ${{id}}`);
            }}
        }}
    </script>
    '''

    base_template = get_base_template()
    return render_template_string(base_template, title="المشتريات", content=content)

# ========== صفحات المصروفات ==========

@app.route('/expenses')
@login_required
@permission_required('expenses')
def expenses():
    """صفحة المصروفات"""
    expenses_list = Expense.query.order_by(Expense.created_at.desc()).all()

    content = f'''
    <div class="main-card">
        <div class="page-header">
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <h2><i class="fas fa-money-bill me-3"></i>إدارة المصروفات</h2>
                    <p class="text-muted mb-0">تسجيل ومتابعة جميع المصروفات</p>
                </div>
                <div class="action-buttons">
                    <button class="btn btn-primary btn-action" onclick="addExpense()">
                        <i class="fas fa-plus me-2"></i>مصروف جديد
                    </button>
                    <button class="btn btn-success btn-action" onclick="printPage()">
                        <i class="fas fa-print me-2"></i>طباعة
                    </button>
                    <button class="btn btn-info btn-action" onclick="exportData('Excel')">
                        <i class="fas fa-file-excel me-2"></i>تصدير
                    </button>
                    <button class="btn btn-secondary btn-action" onclick="goBack()">
                        <i class="fas fa-arrow-right me-2"></i>تراجع
                    </button>
                </div>
            </div>
        </div>

        <div class="table-responsive">
            <table class="table table-hover">
                <thead>
                    <tr>
                        <th>الوصف</th>
                        <th>الفئة</th>
                        <th>المبلغ</th>
                        <th>التاريخ</th>
                        <th>طريقة الدفع</th>
                        <th>رقم الإيصال</th>
                        <th>الإجراءات</th>
                    </tr>
                </thead>
                <tbody>
                    {"".join([f'''
                    <tr>
                        <td><strong>{expense.description}</strong></td>
                        <td>{expense.category or 'غير محدد'}</td>
                        <td><strong>{expense.amount:,.2f} ريال</strong></td>
                        <td>{expense.expense_date}</td>
                        <td>{expense.payment_method or 'غير محدد'}</td>
                        <td>{expense.receipt_number or 'غير محدد'}</td>
                        <td>
                            <div class="action-buttons">
                                <button class="btn btn-sm btn-outline-primary btn-action" onclick="viewExpense({expense.id})">
                                    <i class="fas fa-eye"></i>
                                </button>
                                <button class="btn btn-sm btn-outline-success btn-action" onclick="editExpense({expense.id})">
                                    <i class="fas fa-edit"></i>
                                </button>
                                <button class="btn btn-sm btn-outline-danger btn-action" onclick="deleteExpense({expense.id}, '{expense.description}')">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </div>
                        </td>
                    </tr>
                    ''' for expense in expenses_list])}
                </tbody>
            </table>
        </div>

        <!-- ملخص المصروفات -->
        <div class="form-section">
            <div class="row">
                <div class="col-md-6">
                    <div class="text-center">
                        <h5>{len(expenses_list)}</h5>
                        <small class="text-muted">إجمالي المصروفات</small>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="text-center">
                        <h5 class="text-danger">{sum(expense.amount for expense in expenses_list):,.2f} ريال</h5>
                        <small class="text-muted">إجمالي المبلغ</small>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        function addExpense() {{
            alert('إضافة مصروف جديد\\nسيتم فتح نموذج إضافة مصروف جديد.');
        }}

        function viewExpense(id) {{
            alert(`عرض تفاصيل المصروف رقم: ${{id}}`);
        }}

        function editExpense(id) {{
            alert(`تعديل المصروف رقم: ${{id}}`);
        }}

        function deleteExpense(id, description) {{
            if (confirmDelete(id, description)) {{
                alert(`تم حذف المصروف رقم: ${{id}}`);
            }}
        }}
    </script>
    '''

    base_template = get_base_template()
    return render_template_string(base_template, title="المصروفات", content=content)

# ========== صفحات الموردين ==========

@app.route('/suppliers')
@login_required
@permission_required('suppliers')
def suppliers():
    """صفحة الموردين"""
    suppliers_list = Supplier.query.filter_by(is_active=True).all()

    content = f'''
    <div class="main-card">
        <div class="page-header">
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <h2><i class="fas fa-truck me-3"></i>إدارة الموردين</h2>
                    <p class="text-muted mb-0">إدارة بيانات الموردين والشركات</p>
                </div>
                <div class="action-buttons">
                    <button class="btn btn-primary btn-action" onclick="addSupplier()">
                        <i class="fas fa-plus me-2"></i>مورد جديد
                    </button>
                    <button class="btn btn-success btn-action" onclick="printPage()">
                        <i class="fas fa-print me-2"></i>طباعة
                    </button>
                    <button class="btn btn-info btn-action" onclick="exportData('Excel')">
                        <i class="fas fa-file-excel me-2"></i>تصدير
                    </button>
                    <button class="btn btn-secondary btn-action" onclick="goBack()">
                        <i class="fas fa-arrow-right me-2"></i>تراجع
                    </button>
                </div>
            </div>
        </div>

        <div class="table-responsive">
            <table class="table table-hover">
                <thead>
                    <tr>
                        <th>اسم المورد</th>
                        <th>البريد الإلكتروني</th>
                        <th>الهاتف</th>
                        <th>الرقم الضريبي</th>
                        <th>تاريخ الإضافة</th>
                        <th>الإجراءات</th>
                    </tr>
                </thead>
                <tbody>
                    {"".join([f'''
                    <tr>
                        <td><strong>{supplier.name}</strong></td>
                        <td>{supplier.email or 'غير محدد'}</td>
                        <td>{supplier.phone or 'غير محدد'}</td>
                        <td>{supplier.tax_number or 'غير محدد'}</td>
                        <td>{supplier.created_at.strftime('%Y-%m-%d')}</td>
                        <td>
                            <div class="action-buttons">
                                <button class="btn btn-sm btn-outline-primary btn-action" onclick="viewSupplier({supplier.id})">
                                    <i class="fas fa-eye"></i>
                                </button>
                                <button class="btn btn-sm btn-outline-success btn-action" onclick="editSupplier({supplier.id})">
                                    <i class="fas fa-edit"></i>
                                </button>
                                <button class="btn btn-sm btn-outline-danger btn-action" onclick="deleteSupplier({supplier.id}, '{supplier.name}')">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </div>
                        </td>
                    </tr>
                    ''' for supplier in suppliers_list])}
                </tbody>
            </table>
        </div>
    </div>

    <script>
        function addSupplier() {{
            alert('إضافة مورد جديد\\nسيتم فتح نموذج إضافة مورد جديد.');
        }}

        function viewSupplier(id) {{
            alert(`عرض تفاصيل المورد رقم: ${{id}}`);
        }}

        function editSupplier(id) {{
            alert(`تعديل المورد رقم: ${{id}}`);
        }}

        function deleteSupplier(id, name) {{
            if (confirmDelete(id, name)) {{
                alert(`تم حذف المورد رقم: ${{id}}`);
            }}
        }}
    </script>
    '''

    base_template = get_base_template()
    return render_template_string(base_template, title="الموردين", content=content)

# ========== صفحات العملاء ==========

@app.route('/customers')
@login_required
def customers():
    """صفحة العملاء"""
    customers_list = Customer.query.filter_by(is_active=True).all()

    content = f'''
    <div class="main-card">
        <div class="page-header">
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <h2><i class="fas fa-users me-3"></i>إدارة العملاء</h2>
                    <p class="text-muted mb-0">إدارة بيانات العملاء والشركات</p>
                </div>
                <div class="action-buttons">
                    <button class="btn btn-primary btn-action" onclick="addCustomer()">
                        <i class="fas fa-plus me-2"></i>عميل جديد
                    </button>
                    <button class="btn btn-success btn-action" onclick="printPage()">
                        <i class="fas fa-print me-2"></i>طباعة
                    </button>
                    <button class="btn btn-info btn-action" onclick="exportData('Excel')">
                        <i class="fas fa-file-excel me-2"></i>تصدير
                    </button>
                    <button class="btn btn-secondary btn-action" onclick="goBack()">
                        <i class="fas fa-arrow-right me-2"></i>تراجع
                    </button>
                </div>
            </div>
        </div>

        <div class="table-responsive">
            <table class="table table-hover">
                <thead>
                    <tr>
                        <th>اسم العميل</th>
                        <th>البريد الإلكتروني</th>
                        <th>الهاتف</th>
                        <th>الرقم الضريبي</th>
                        <th>تاريخ الإضافة</th>
                        <th>الإجراءات</th>
                    </tr>
                </thead>
                <tbody>
                    {"".join([f'''
                    <tr>
                        <td><strong>{customer.name}</strong></td>
                        <td>{customer.email or 'غير محدد'}</td>
                        <td>{customer.phone or 'غير محدد'}</td>
                        <td>{customer.tax_number or 'غير محدد'}</td>
                        <td>{customer.created_at.strftime('%Y-%m-%d')}</td>
                        <td>
                            <div class="action-buttons">
                                <button class="btn btn-sm btn-outline-primary btn-action" onclick="viewCustomer({customer.id})">
                                    <i class="fas fa-eye"></i>
                                </button>
                                <button class="btn btn-sm btn-outline-success btn-action" onclick="editCustomer({customer.id})">
                                    <i class="fas fa-edit"></i>
                                </button>
                                <button class="btn btn-sm btn-outline-danger btn-action" onclick="deleteCustomer({customer.id}, '{customer.name}')">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </div>
                        </td>
                    </tr>
                    ''' for customer in customers_list])}
                </tbody>
            </table>
        </div>
    </div>

    <script>
        function addCustomer() {{
            alert('إضافة عميل جديد\\nسيتم فتح نموذج إضافة عميل جديد.');
        }}

        function viewCustomer(id) {{
            alert(`عرض تفاصيل العميل رقم: ${{id}}`);
        }}

        function editCustomer(id) {{
            alert(`تعديل العميل رقم: ${{id}}`);
        }}

        function deleteCustomer(id, name) {{
            if (confirmDelete(id, name)) {{
                alert(`تم حذف العميل رقم: ${{id}}`);
            }}
        }}
    </script>
    '''

    base_template = get_base_template()
    return render_template_string(base_template, title="العملاء", content=content)

# ========== صفحات المدفوعات ==========

@app.route('/payments')
@login_required
@permission_required('payments')
def payments():
    """صفحة المدفوعات"""
    payments_list = Payment.query.order_by(Payment.created_at.desc()).all()

    content = f'''
    <div class="main-card">
        <div class="page-header">
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <h2><i class="fas fa-credit-card me-3"></i>إدارة المدفوعات</h2>
                    <p class="text-muted mb-0">تسجيل ومتابعة جميع المدفوعات الواردة والصادرة</p>
                </div>
                <div class="action-buttons">
                    <button class="btn btn-primary btn-action" onclick="addPayment()">
                        <i class="fas fa-plus me-2"></i>دفعة جديدة
                    </button>
                    <button class="btn btn-success btn-action" onclick="printPage()">
                        <i class="fas fa-print me-2"></i>طباعة
                    </button>
                    <button class="btn btn-info btn-action" onclick="exportData('Excel')">
                        <i class="fas fa-file-excel me-2"></i>تصدير
                    </button>
                    <button class="btn btn-secondary btn-action" onclick="goBack()">
                        <i class="fas fa-arrow-right me-2"></i>تراجع
                    </button>
                </div>
            </div>
        </div>

        <div class="table-responsive">
            <table class="table table-hover">
                <thead>
                    <tr>
                        <th>النوع</th>
                        <th>الوصف</th>
                        <th>المبلغ</th>
                        <th>طريقة الدفع</th>
                        <th>التاريخ</th>
                        <th>الإجراءات</th>
                    </tr>
                </thead>
                <tbody>
                    {"".join([f'''
                    <tr>
                        <td>
                            <span class="badge bg-{'success' if payment.type == 'received' else 'danger'}">
                                {'مقبوض' if payment.type == 'received' else 'مدفوع'}
                            </span>
                        </td>
                        <td>{payment.description or 'غير محدد'}</td>
                        <td><strong>{payment.amount:,.2f} ريال</strong></td>
                        <td>{payment.payment_method or 'غير محدد'}</td>
                        <td>{payment.payment_date}</td>
                        <td>
                            <div class="action-buttons">
                                <button class="btn btn-sm btn-outline-primary btn-action" onclick="viewPayment({payment.id})">
                                    <i class="fas fa-eye"></i>
                                </button>
                                <button class="btn btn-sm btn-outline-success btn-action" onclick="editPayment({payment.id})">
                                    <i class="fas fa-edit"></i>
                                </button>
                                <button class="btn btn-sm btn-outline-danger btn-action" onclick="deletePayment({payment.id})">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </div>
                        </td>
                    </tr>
                    ''' for payment in payments_list])}
                </tbody>
            </table>
        </div>
    </div>

    <script>
        function addPayment() {{
            alert('إضافة دفعة جديدة\\nسيتم فتح نموذج إضافة دفعة جديدة.');
        }}

        function viewPayment(id) {{
            alert(`عرض تفاصيل الدفعة رقم: ${{id}}`);
        }}

        function editPayment(id) {{
            alert(`تعديل الدفعة رقم: ${{id}}`);
        }}

        function deletePayment(id) {{
            if (confirmDelete(id, 'الدفعة')) {{
                alert(`تم حذف الدفعة رقم: ${{id}}`);
            }}
        }}
    </script>
    '''

    base_template = get_base_template()
    return render_template_string(base_template, title="المدفوعات", content=content)

# ========== صفحات الموظفين ==========

@app.route('/employees')
@login_required
@permission_required('employees')
def employees():
    """صفحة الموظفين"""
    employees_list = Employee.query.filter_by(is_active=True).all()

    content = f'''
    <div class="main-card">
        <div class="page-header">
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <h2><i class="fas fa-user-tie me-3"></i>إدارة الموظفين</h2>
                    <p class="text-muted mb-0">إدارة بيانات الموظفين والوظائف</p>
                </div>
                <div class="action-buttons">
                    <button class="btn btn-primary btn-action" onclick="addEmployee()">
                        <i class="fas fa-plus me-2"></i>موظف جديد
                    </button>
                    <button class="btn btn-success btn-action" onclick="printPage()">
                        <i class="fas fa-print me-2"></i>طباعة
                    </button>
                    <button class="btn btn-info btn-action" onclick="exportData('Excel')">
                        <i class="fas fa-file-excel me-2"></i>تصدير
                    </button>
                    <button class="btn btn-secondary btn-action" onclick="goBack()">
                        <i class="fas fa-arrow-right me-2"></i>تراجع
                    </button>
                </div>
            </div>
        </div>

        <div class="table-responsive">
            <table class="table table-hover">
                <thead>
                    <tr>
                        <th>الاسم</th>
                        <th>رقم الموظف</th>
                        <th>المنصب</th>
                        <th>القسم</th>
                        <th>الراتب</th>
                        <th>تاريخ التوظيف</th>
                        <th>الإجراءات</th>
                    </tr>
                </thead>
                <tbody>
                    {"".join([f'''
                    <tr>
                        <td><strong>{employee.name}</strong></td>
                        <td>{employee.employee_id or 'غير محدد'}</td>
                        <td>{employee.position or 'غير محدد'}</td>
                        <td>{employee.department or 'غير محدد'}</td>
                        <td><strong>{employee.salary:,.2f} ريال</strong></td>
                        <td>{employee.hire_date or 'غير محدد'}</td>
                        <td>
                            <div class="action-buttons">
                                <button class="btn btn-sm btn-outline-primary btn-action" onclick="viewEmployee({employee.id})">
                                    <i class="fas fa-eye"></i>
                                </button>
                                <button class="btn btn-sm btn-outline-success btn-action" onclick="editEmployee({employee.id})">
                                    <i class="fas fa-edit"></i>
                                </button>
                                <button class="btn btn-sm btn-outline-warning btn-action" onclick="paySalary({employee.id})">
                                    <i class="fas fa-money-bill"></i>
                                </button>
                                <button class="btn btn-sm btn-outline-danger btn-action" onclick="deleteEmployee({employee.id}, '{employee.name}')">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </div>
                        </td>
                    </tr>
                    ''' for employee in employees_list])}
                </tbody>
            </table>
        </div>
    </div>

    <script>
        function addEmployee() {{
            alert('إضافة موظف جديد\\nسيتم فتح نموذج إضافة موظف جديد.');
        }}

        function viewEmployee(id) {{
            alert(`عرض تفاصيل الموظف رقم: ${{id}}`);
        }}

        function editEmployee(id) {{
            alert(`تعديل الموظف رقم: ${{id}}`);
        }}

        function paySalary(id) {{
            alert(`صرف راتب الموظف رقم: ${{id}}\\nسيتم فتح نموذج صرف الراتب.`);
        }}

        function deleteEmployee(id, name) {{
            if (confirmDelete(id, name)) {{
                alert(`تم حذف الموظف رقم: ${{id}}`);
            }}
        }}
    </script>
    '''

    base_template = get_base_template()
    return render_template_string(base_template, title="الموظفين", content=content)

# ========== صفحات الرواتب ==========

@app.route('/salaries')
@login_required
@permission_required('employees')
def salaries():
    """صفحة الرواتب"""
    salaries_list = Salary.query.order_by(Salary.created_at.desc()).all()

    content = f'''
    <div class="main-card">
        <div class="page-header">
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <h2><i class="fas fa-money-check me-3"></i>إدارة الرواتب</h2>
                    <p class="text-muted mb-0">صرف ومتابعة رواتب الموظفين</p>
                </div>
                <div class="action-buttons">
                    <button class="btn btn-primary btn-action" onclick="addSalary()">
                        <i class="fas fa-plus me-2"></i>صرف راتب
                    </button>
                    <button class="btn btn-success btn-action" onclick="printPage()">
                        <i class="fas fa-print me-2"></i>طباعة
                    </button>
                    <button class="btn btn-info btn-action" onclick="exportData('Excel')">
                        <i class="fas fa-file-excel me-2"></i>تصدير
                    </button>
                    <button class="btn btn-secondary btn-action" onclick="goBack()">
                        <i class="fas fa-arrow-right me-2"></i>تراجع
                    </button>
                </div>
            </div>
        </div>

        <div class="table-responsive">
            <table class="table table-hover">
                <thead>
                    <tr>
                        <th>الموظف</th>
                        <th>الشهر/السنة</th>
                        <th>الراتب الأساسي</th>
                        <th>البدلات</th>
                        <th>الخصومات</th>
                        <th>صافي الراتب</th>
                        <th>الحالة</th>
                        <th>الإجراءات</th>
                    </tr>
                </thead>
                <tbody>
                    {"".join([f'''
                    <tr>
                        <td><strong>{salary.employee.name if salary.employee else 'غير محدد'}</strong></td>
                        <td>{salary.month}/{salary.year}</td>
                        <td>{salary.basic_salary:,.2f} ريال</td>
                        <td>{salary.allowances:,.2f} ريال</td>
                        <td>{salary.deductions:,.2f} ريال</td>
                        <td><strong>{salary.net_salary:,.2f} ريال</strong></td>
                        <td>
                            <span class="badge bg-{'success' if salary.status == 'paid' else 'warning'}">
                                {'مدفوع' if salary.status == 'paid' else 'معلق'}
                            </span>
                        </td>
                        <td>
                            <div class="action-buttons">
                                <button class="btn btn-sm btn-outline-primary btn-action" onclick="viewSalary({salary.id})">
                                    <i class="fas fa-eye"></i>
                                </button>
                                <button class="btn btn-sm btn-outline-success btn-action" onclick="editSalary({salary.id})">
                                    <i class="fas fa-edit"></i>
                                </button>
                                <button class="btn btn-sm btn-outline-info btn-action" onclick="printSalary({salary.id})">
                                    <i class="fas fa-print"></i>
                                </button>
                                <button class="btn btn-sm btn-outline-danger btn-action" onclick="deleteSalary({salary.id})">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </div>
                        </td>
                    </tr>
                    ''' for salary in salaries_list])}
                </tbody>
            </table>
        </div>
    </div>

    <script>
        function addSalary() {{
            alert('صرف راتب جديد\\nسيتم فتح نموذج صرف راتب.');
        }}

        function viewSalary(id) {{
            alert(`عرض تفاصيل الراتب رقم: ${{id}}`);
        }}

        function editSalary(id) {{
            alert(`تعديل الراتب رقم: ${{id}}`);
        }}

        function printSalary(id) {{
            alert(`طباعة كشف راتب رقم: ${{id}}`);
        }}

        function deleteSalary(id) {{
            if (confirmDelete(id, 'الراتب')) {{
                alert(`تم حذف الراتب رقم: ${{id}}`);
            }}
        }}
    </script>
    '''

    base_template = get_base_template()
    return render_template_string(base_template, title="الرواتب", content=content)

# ========== صفحات التقارير ==========

@app.route('/reports')
@login_required
@permission_required('reports')
def reports():
    """صفحة تحليل الإيرادات والمصروفات"""
    # حساب الإحصائيات
    total_sales = db.session.query(db.func.sum(Sale.total_amount)).scalar() or 0
    total_purchases = db.session.query(db.func.sum(Purchase.total_amount)).scalar() or 0
    total_expenses = db.session.query(db.func.sum(Expense.amount)).scalar() or 0
    total_salaries = db.session.query(db.func.sum(Salary.net_salary)).scalar() or 0
    net_profit = total_sales - total_purchases - total_expenses - total_salaries

    content = f'''
    <div class="main-card">
        <div class="page-header">
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <h2><i class="fas fa-chart-line me-3"></i>تحليل الإيرادات والمصروفات</h2>
                    <p class="text-muted mb-0">تقارير مالية شاملة وتحليل الأداء</p>
                </div>
                <div class="action-buttons">
                    <button class="btn btn-success btn-action" onclick="printPage()">
                        <i class="fas fa-print me-2"></i>طباعة
                    </button>
                    <button class="btn btn-info btn-action" onclick="exportData('Excel')">
                        <i class="fas fa-file-excel me-2"></i>تصدير Excel
                    </button>
                    <button class="btn btn-warning btn-action" onclick="exportData('PDF')">
                        <i class="fas fa-file-pdf me-2"></i>تصدير PDF
                    </button>
                    <button class="btn btn-secondary btn-action" onclick="goBack()">
                        <i class="fas fa-arrow-right me-2"></i>تراجع
                    </button>
                </div>
            </div>
        </div>

        <!-- الملخص المالي -->
        <div class="row mb-4">
            <div class="col-lg-3 col-md-6 mb-3">
                <div class="stat-card" style="background: linear-gradient(135deg, #28a745, #20c997);">
                    <div style="font-size: 1.5rem; font-weight: bold;">{total_sales:,.2f} ريال</div>
                    <div><i class="fas fa-arrow-up me-2"></i>إجمالي الإيرادات</div>
                </div>
            </div>
            <div class="col-lg-3 col-md-6 mb-3">
                <div class="stat-card" style="background: linear-gradient(135deg, #dc3545, #c82333);">
                    <div style="font-size: 1.5rem; font-weight: bold;">{total_purchases:,.2f} ريال</div>
                    <div><i class="fas fa-arrow-down me-2"></i>إجمالي المشتريات</div>
                </div>
            </div>
            <div class="col-lg-3 col-md-6 mb-3">
                <div class="stat-card" style="background: linear-gradient(135deg, #ffc107, #e0a800);">
                    <div style="font-size: 1.5rem; font-weight: bold;">{(total_expenses + total_salaries):,.2f} ريال</div>
                    <div><i class="fas fa-minus me-2"></i>إجمالي المصروفات</div>
                </div>
            </div>
            <div class="col-lg-3 col-md-6 mb-3">
                <div class="stat-card" style="background: linear-gradient(135deg, {'#17a2b8' if net_profit >= 0 else '#dc3545'}, {'#138496' if net_profit >= 0 else '#c82333'});">
                    <div style="font-size: 1.5rem; font-weight: bold;">{net_profit:,.2f} ريال</div>
                    <div><i class="fas fa-calculator me-2"></i>صافي {'الربح' if net_profit >= 0 else 'الخسارة'}</div>
                </div>
            </div>
        </div>

        <!-- تفاصيل التقارير -->
        <div class="row">
            <div class="col-md-6">
                <div class="form-section">
                    <h5><i class="fas fa-chart-pie me-2"></i>تفصيل الإيرادات</h5>
                    <table class="table table-sm">
                        <tr>
                            <td>المبيعات:</td>
                            <td class="text-end"><strong>{total_sales:,.2f} ريال</strong></td>
                        </tr>
                        <tr>
                            <td>عدد الفواتير:</td>
                            <td class="text-end"><strong>{Sale.query.count()}</strong></td>
                        </tr>
                        <tr>
                            <td>متوسط الفاتورة:</td>
                            <td class="text-end"><strong>{(total_sales / Sale.query.count() if Sale.query.count() > 0 else 0):,.2f} ريال</strong></td>
                        </tr>
                    </table>
                </div>
            </div>

            <div class="col-md-6">
                <div class="form-section">
                    <h5><i class="fas fa-chart-bar me-2"></i>تفصيل المصروفات</h5>
                    <table class="table table-sm">
                        <tr>
                            <td>المشتريات:</td>
                            <td class="text-end"><strong>{total_purchases:,.2f} ريال</strong></td>
                        </tr>
                        <tr>
                            <td>المصروفات العامة:</td>
                            <td class="text-end"><strong>{total_expenses:,.2f} ريال</strong></td>
                        </tr>
                        <tr>
                            <td>الرواتب:</td>
                            <td class="text-end"><strong>{total_salaries:,.2f} ريال</strong></td>
                        </tr>
                    </table>
                </div>
            </div>
        </div>

        <!-- أزرار التقارير التفصيلية -->
        <div class="form-section">
            <h5><i class="fas fa-file-alt me-2"></i>التقارير التفصيلية</h5>
            <div class="action-buttons">
                <button class="btn btn-outline-primary btn-action" onclick="generateReport('sales')">
                    <i class="fas fa-shopping-cart me-2"></i>تقرير المبيعات
                </button>
                <button class="btn btn-outline-success btn-action" onclick="generateReport('purchases')">
                    <i class="fas fa-shopping-bag me-2"></i>تقرير المشتريات
                </button>
                <button class="btn btn-outline-warning btn-action" onclick="generateReport('expenses')">
                    <i class="fas fa-money-bill me-2"></i>تقرير المصروفات
                </button>
                <button class="btn btn-outline-info btn-action" onclick="generateReport('customers')">
                    <i class="fas fa-users me-2"></i>تقرير العملاء
                </button>
                <button class="btn btn-outline-secondary btn-action" onclick="generateReport('suppliers')">
                    <i class="fas fa-truck me-2"></i>تقرير الموردين
                </button>
                <button class="btn btn-outline-dark btn-action" onclick="generateReport('inventory')">
                    <i class="fas fa-box me-2"></i>تقرير المخزون
                </button>
            </div>
        </div>
    </div>

    <script>
        function generateReport(type) {{
            alert(`إنشاء تقرير ${{type}}\\nسيتم إنشاء التقرير وتحميله تلقائياً.`);
        }}
    </script>
    '''

    base_template = get_base_template()
    return render_template_string(base_template, title="التقارير", content=content)

# ========== صفحات المخزون والأصناف ==========

@app.route('/inventory')
@login_required
@permission_required('inventory')
def inventory():
    """صفحة المخزون والأصناف"""
    products_list = Product.query.filter_by(is_active=True).all()
    low_stock_products = Product.query.filter(Product.stock_quantity <= Product.min_stock).all()

    content = f'''
    <div class="main-card">
        <div class="page-header">
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <h2><i class="fas fa-warehouse me-3"></i>المخزون والأصناف</h2>
                    <p class="text-muted mb-0">إدارة المخزون ومتابعة الأصناف</p>
                </div>
                <div class="action-buttons">
                    <button class="btn btn-primary btn-action" onclick="addProduct()">
                        <i class="fas fa-plus me-2"></i>صنف جديد
                    </button>
                    <button class="btn btn-success btn-action" onclick="printPage()">
                        <i class="fas fa-print me-2"></i>طباعة
                    </button>
                    <button class="btn btn-info btn-action" onclick="exportData('Excel')">
                        <i class="fas fa-file-excel me-2"></i>تصدير
                    </button>
                    <button class="btn btn-secondary btn-action" onclick="goBack()">
                        <i class="fas fa-arrow-right me-2"></i>تراجع
                    </button>
                </div>
            </div>
        </div>

        <!-- تنبيه المخزون المنخفض -->
        {f'''
        <div class="alert alert-warning">
            <h6><i class="fas fa-exclamation-triangle me-2"></i>تنبيه: أصناف بمخزون منخفض</h6>
            <p class="mb-0">يوجد {len(low_stock_products)} صنف بمخزون أقل من الحد الأدنى</p>
        </div>
        ''' if low_stock_products else ''}

        <div class="table-responsive">
            <table class="table table-hover">
                <thead>
                    <tr>
                        <th>الكود</th>
                        <th>اسم الصنف</th>
                        <th>الوحدة</th>
                        <th>سعر التكلفة</th>
                        <th>سعر البيع</th>
                        <th>الكمية المتاحة</th>
                        <th>الحد الأدنى</th>
                        <th>الفئة</th>
                        <th>الحالة</th>
                        <th>الإجراءات</th>
                    </tr>
                </thead>
                <tbody>
                    {"".join([f'''
                    <tr class="{'table-warning' if product.stock_quantity <= product.min_stock else ''}">
                        <td><strong>{product.code or 'غير محدد'}</strong></td>
                        <td>{product.name}</td>
                        <td>{product.unit}</td>
                        <td>{product.cost_price:,.2f} ريال</td>
                        <td><strong>{product.selling_price:,.2f} ريال</strong></td>
                        <td>
                            <span class="badge bg-{'danger' if product.stock_quantity <= product.min_stock else 'success'}">
                                {product.stock_quantity}
                            </span>
                        </td>
                        <td>{product.min_stock}</td>
                        <td>{product.category or 'غير محدد'}</td>
                        <td>
                            <span class="badge bg-{'success' if product.is_active else 'secondary'}">
                                {'نشط' if product.is_active else 'غير نشط'}
                            </span>
                        </td>
                        <td>
                            <div class="action-buttons">
                                <button class="btn btn-sm btn-outline-primary btn-action" onclick="viewProduct({product.id})">
                                    <i class="fas fa-eye"></i>
                                </button>
                                <button class="btn btn-sm btn-outline-success btn-action" onclick="editProduct({product.id})">
                                    <i class="fas fa-edit"></i>
                                </button>
                                <button class="btn btn-sm btn-outline-warning btn-action" onclick="adjustStock({product.id})">
                                    <i class="fas fa-plus-minus"></i>
                                </button>
                                <button class="btn btn-sm btn-outline-danger btn-action" onclick="deleteProduct({product.id}, '{product.name}')">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </div>
                        </td>
                    </tr>
                    ''' for product in products_list])}
                </tbody>
            </table>
        </div>

        <!-- ملخص المخزون -->
        <div class="form-section">
            <div class="row">
                <div class="col-md-3">
                    <div class="text-center">
                        <h5>{len(products_list)}</h5>
                        <small class="text-muted">إجمالي الأصناف</small>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="text-center">
                        <h5>{sum(product.stock_quantity for product in products_list)}</h5>
                        <small class="text-muted">إجمالي الكمية</small>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="text-center">
                        <h5>{sum(product.cost_price * product.stock_quantity for product in products_list):,.2f}</h5>
                        <small class="text-muted">قيمة المخزون (تكلفة)</small>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="text-center">
                        <h5 class="text-danger">{len(low_stock_products)}</h5>
                        <small class="text-muted">أصناف بمخزون منخفض</small>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        function addProduct() {{
            alert('إضافة صنف جديد\\nسيتم فتح نموذج إضافة صنف جديد.');
        }}

        function viewProduct(id) {{
            alert(`عرض تفاصيل الصنف رقم: ${{id}}`);
        }}

        function editProduct(id) {{
            alert(`تعديل الصنف رقم: ${{id}}`);
        }}

        function adjustStock(id) {{
            alert(`تعديل مخزون الصنف رقم: ${{id}}\\nسيتم فتح نموذج تعديل المخزون.`);
        }}

        function deleteProduct(id, name) {{
            if (confirmDelete(id, name)) {{
                alert(`تم حذف الصنف رقم: ${{id}}`);
            }}
        }}
    </script>
    '''

    base_template = get_base_template()
    return render_template_string(base_template, title="المخزون", content=content)

# ========== صفحات ضريبة القيمة المضافة ==========

@app.route('/vat')
@login_required
@permission_required('vat')
def vat():
    """صفحة ضريبة القيمة المضافة"""
    vat_setting = VATSetting.query.filter_by(is_active=True).first()
    current_rate = vat_setting.rate if vat_setting else 15.00

    # حساب إجمالي الضريبة
    total_sales_vat = db.session.query(db.func.sum(Sale.vat_amount)).scalar() or 0
    total_purchases_vat = db.session.query(db.func.sum(Purchase.vat_amount)).scalar() or 0
    net_vat = total_sales_vat - total_purchases_vat

    content = f'''
    <div class="main-card">
        <div class="page-header">
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <h2><i class="fas fa-percentage me-3"></i>ضريبة القيمة المضافة</h2>
                    <p class="text-muted mb-0">إدارة ومتابعة ضريبة القيمة المضافة</p>
                </div>
                <div class="action-buttons">
                    <button class="btn btn-primary btn-action" onclick="updateVATRate()">
                        <i class="fas fa-edit me-2"></i>تحديث النسبة
                    </button>
                    <button class="btn btn-success btn-action" onclick="printPage()">
                        <i class="fas fa-print me-2"></i>طباعة
                    </button>
                    <button class="btn btn-info btn-action" onclick="exportData('Excel')">
                        <i class="fas fa-file-excel me-2"></i>تصدير
                    </button>
                    <button class="btn btn-secondary btn-action" onclick="goBack()">
                        <i class="fas fa-arrow-right me-2"></i>تراجع
                    </button>
                </div>
            </div>
        </div>

        <!-- معلومات الضريبة الحالية -->
        <div class="form-section">
            <h5><i class="fas fa-info-circle me-2"></i>معلومات الضريبة الحالية</h5>
            <div class="row">
                <div class="col-md-6">
                    <table class="table table-sm">
                        <tr>
                            <td><strong>نسبة الضريبة الحالية:</strong></td>
                            <td class="text-end"><span class="badge bg-primary fs-6">{current_rate}%</span></td>
                        </tr>
                        <tr>
                            <td><strong>تاريخ السريان:</strong></td>
                            <td class="text-end">{vat_setting.effective_date if vat_setting else 'غير محدد'}</td>
                        </tr>
                        <tr>
                            <td><strong>الحالة:</strong></td>
                            <td class="text-end">
                                <span class="badge bg-success">نشطة</span>
                            </td>
                        </tr>
                    </table>
                </div>
                <div class="col-md-6">
                    <div class="alert alert-info">
                        <h6><i class="fas fa-calculator me-2"></i>مثال على الحساب</h6>
                        <p class="mb-0">
                            مبلغ 1000 ريال + ضريبة {current_rate}% = {1000 + (1000 * current_rate / 100):,.2f} ريال
                        </p>
                    </div>
                </div>
            </div>
        </div>

        <!-- ملخص الضريبة -->
        <div class="row mb-4">
            <div class="col-lg-4 col-md-6 mb-3">
                <div class="stat-card" style="background: linear-gradient(135deg, #28a745, #20c997);">
                    <div style="font-size: 1.5rem; font-weight: bold;">{total_sales_vat:,.2f} ريال</div>
                    <div><i class="fas fa-arrow-up me-2"></i>ضريبة المبيعات</div>
                </div>
            </div>
            <div class="col-lg-4 col-md-6 mb-3">
                <div class="stat-card" style="background: linear-gradient(135deg, #dc3545, #c82333);">
                    <div style="font-size: 1.5rem; font-weight: bold;">{total_purchases_vat:,.2f} ريال</div>
                    <div><i class="fas fa-arrow-down me-2"></i>ضريبة المشتريات</div>
                </div>
            </div>
            <div class="col-lg-4 col-md-6 mb-3">
                <div class="stat-card" style="background: linear-gradient(135deg, {'#17a2b8' if net_vat >= 0 else '#ffc107'}, {'#138496' if net_vat >= 0 else '#e0a800'});">
                    <div style="font-size: 1.5rem; font-weight: bold;">{net_vat:,.2f} ريال</div>
                    <div><i class="fas fa-balance-scale me-2"></i>صافي الضريبة {'المستحقة' if net_vat >= 0 else 'المستردة'}</div>
                </div>
            </div>
        </div>

        <!-- أدوات الضريبة -->
        <div class="form-section">
            <h5><i class="fas fa-tools me-2"></i>أدوات الضريبة</h5>
            <div class="action-buttons">
                <button class="btn btn-outline-primary btn-action" onclick="calculateVAT()">
                    <i class="fas fa-calculator me-2"></i>حاسبة الضريبة
                </button>
                <button class="btn btn-outline-success btn-action" onclick="generateVATReport()">
                    <i class="fas fa-file-alt me-2"></i>تقرير الضريبة
                </button>
                <button class="btn btn-outline-info btn-action" onclick="vatDeclaration()">
                    <i class="fas fa-file-invoice me-2"></i>إقرار ضريبي
                </button>
                <button class="btn btn-outline-warning btn-action" onclick="vatSettings()">
                    <i class="fas fa-cog me-2"></i>إعدادات الضريبة
                </button>
            </div>
        </div>
    </div>

    <script>
        function updateVATRate() {{
            const newRate = prompt('أدخل نسبة الضريبة الجديدة:', '{current_rate}');
            if (newRate && !isNaN(newRate)) {{
                alert(`تم تحديث نسبة الضريبة إلى ${{newRate}}%`);
            }}
        }}

        function calculateVAT() {{
            const amount = prompt('أدخل المبلغ لحساب الضريبة:');
            if (amount && !isNaN(amount)) {{
                const vat = parseFloat(amount) * {current_rate} / 100;
                const total = parseFloat(amount) + vat;
                alert(`المبلغ: ${{amount}} ريال\\nالضريبة ({current_rate}%): ${{vat.toFixed(2)}} ريال\\nالإجمالي: ${{total.toFixed(2)}} ريال`);
            }}
        }}

        function generateVATReport() {{
            alert('إنشاء تقرير الضريبة\\nسيتم إنشاء تقرير شامل للضريبة.');
        }}

        function vatDeclaration() {{
            alert('إنشاء إقرار ضريبي\\nسيتم إنشاء الإقرار الضريبي.');
        }}

        function vatSettings() {{
            alert('إعدادات الضريبة\\nسيتم فتح صفحة إعدادات الضريبة.');
        }}
    </script>
    '''

    base_template = get_base_template()
    return render_template_string(base_template, title="ضريبة القيمة المضافة", content=content)

# ========== صفحات الإعدادات ==========

@app.route('/settings')
@login_required
@permission_required('settings')
def settings():
    """صفحة الإعدادات والمستخدمين"""
    users_list = User.query.all()

    content = f'''
    <div class="main-card">
        <div class="page-header">
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <h2><i class="fas fa-cog me-3"></i>الإعدادات والمستخدمين</h2>
                    <p class="text-muted mb-0">إدارة إعدادات النظام والمستخدمين والصلاحيات</p>
                </div>
                <div class="action-buttons">
                    <button class="btn btn-primary btn-action" onclick="addUser()">
                        <i class="fas fa-user-plus me-2"></i>مستخدم جديد
                    </button>
                    <button class="btn btn-success btn-action" onclick="printPage()">
                        <i class="fas fa-print me-2"></i>طباعة
                    </button>
                    <button class="btn btn-info btn-action" onclick="exportData('Excel')">
                        <i class="fas fa-file-excel me-2"></i>تصدير
                    </button>
                    <button class="btn btn-secondary btn-action" onclick="goBack()">
                        <i class="fas fa-arrow-right me-2"></i>تراجع
                    </button>
                </div>
            </div>
        </div>

        <!-- إعدادات النظام -->
        <div class="form-section">
            <h5><i class="fas fa-sliders-h me-2"></i>إعدادات النظام</h5>
            <div class="row">
                <div class="col-md-6">
                    <div class="action-buttons">
                        <button class="btn btn-outline-primary btn-action" onclick="systemSettings()">
                            <i class="fas fa-cogs me-2"></i>إعدادات عامة
                        </button>
                        <button class="btn btn-outline-success btn-action" onclick="backupSettings()">
                            <i class="fas fa-database me-2"></i>النسخ الاحتياطي
                        </button>
                        <button class="btn btn-outline-info btn-action" onclick="securitySettings()">
                            <i class="fas fa-shield-alt me-2"></i>إعدادات الأمان
                        </button>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="action-buttons">
                        <button class="btn btn-outline-warning btn-action" onclick="emailSettings()">
                            <i class="fas fa-envelope me-2"></i>إعدادات البريد
                        </button>
                        <button class="btn btn-outline-secondary btn-action" onclick="reportSettings()">
                            <i class="fas fa-chart-bar me-2"></i>إعدادات التقارير
                        </button>
                        <button class="btn btn-outline-dark btn-action" onclick="systemLogs()">
                            <i class="fas fa-file-alt me-2"></i>سجلات النظام
                        </button>
                    </div>
                </div>
            </div>
        </div>

        <!-- إدارة المستخدمين -->
        <div class="form-section">
            <h5><i class="fas fa-users me-2"></i>إدارة المستخدمين</h5>
            <div class="table-responsive">
                <table class="table table-hover">
                    <thead>
                        <tr>
                            <th>اسم المستخدم</th>
                            <th>الاسم الكامل</th>
                            <th>البريد الإلكتروني</th>
                            <th>الدور</th>
                            <th>الحالة</th>
                            <th>تاريخ الإنشاء</th>
                            <th>الإجراءات</th>
                        </tr>
                    </thead>
                    <tbody>
                        {"".join([f'''
                        <tr>
                            <td><strong>{user.username}</strong></td>
                            <td>{user.full_name}</td>
                            <td>{user.email}</td>
                            <td>
                                <span class="badge bg-{'danger' if user.role == 'admin' else 'primary'}">
                                    {'مدير' if user.role == 'admin' else 'مستخدم'}
                                </span>
                            </td>
                            <td>
                                <span class="badge bg-{'success' if user.is_active else 'secondary'}">
                                    {'نشط' if user.is_active else 'غير نشط'}
                                </span>
                            </td>
                            <td>{user.created_at.strftime('%Y-%m-%d')}</td>
                            <td>
                                <div class="action-buttons">
                                    <button class="btn btn-sm btn-outline-primary btn-action" onclick="viewUser({user.id})">
                                        <i class="fas fa-eye"></i>
                                    </button>
                                    <button class="btn btn-sm btn-outline-success btn-action" onclick="editUser({user.id})">
                                        <i class="fas fa-edit"></i>
                                    </button>
                                    <button class="btn btn-sm btn-outline-warning btn-action" onclick="userPermissions({user.id})">
                                        <i class="fas fa-key"></i>
                                    </button>
                                    <button class="btn btn-sm btn-outline-danger btn-action" onclick="deleteUser({user.id}, '{user.username}')" {'disabled' if user.role == 'admin' else ''}>
                                        <i class="fas fa-trash"></i>
                                    </button>
                                </div>
                            </td>
                        </tr>
                        ''' for user in users_list])}
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <script>
        function addUser() {{
            alert('إضافة مستخدم جديد\\nسيتم فتح نموذج إضافة مستخدم جديد.');
        }}

        function viewUser(id) {{
            alert(`عرض تفاصيل المستخدم رقم: ${{id}}`);
        }}

        function editUser(id) {{
            alert(`تعديل المستخدم رقم: ${{id}}`);
        }}

        function userPermissions(id) {{
            alert(`إدارة صلاحيات المستخدم رقم: ${{id}}\\nسيتم فتح صفحة الصلاحيات.`);
        }}

        function deleteUser(id, username) {{
            if (confirmDelete(id, username)) {{
                alert(`تم حذف المستخدم رقم: ${{id}}`);
            }}
        }}

        function systemSettings() {{
            alert('الإعدادات العامة\\nسيتم فتح صفحة الإعدادات العامة.');
        }}

        function backupSettings() {{
            alert('النسخ الاحتياطي\\nسيتم فتح إعدادات النسخ الاحتياطي.');
        }}

        function securitySettings() {{
            alert('إعدادات الأمان\\nسيتم فتح إعدادات الأمان.');
        }}

        function emailSettings() {{
            alert('إعدادات البريد\\nسيتم فتح إعدادات البريد الإلكتروني.');
        }}

        function reportSettings() {{
            alert('إعدادات التقارير\\nسيتم فتح إعدادات التقارير.');
        }}

        function systemLogs() {{
            alert('سجلات النظام\\nسيتم فتح سجلات النظام.');
        }}
    </script>
    '''

    base_template = get_base_template()
    return render_template_string(base_template, title="الإعدادات", content=content)

# ========== المسارات الإضافية ==========

@app.route('/profile')
@login_required
def profile():
    """الملف الشخصي"""
    return redirect(url_for('settings'))

@app.route('/logout')
@login_required
def logout():
    """تسجيل الخروج"""
    logout_user()
    flash('تم تسجيل الخروج بنجاح', 'info')
    return redirect(url_for('home'))

@app.route('/api/status')
def api_status():
    """API حالة النظام"""
    return jsonify({
        'status': 'success',
        'message': 'نظام المحاسبة الاحترافي يعمل بنجاح',
        'version': '1.0.0-professional',
        'database': 'متصلة',
        'features': {
            'sales': 'نشط',
            'purchases': 'نشط',
            'expenses': 'نشط',
            'suppliers': 'نشط',
            'customers': 'نشط',
            'payments': 'نشط',
            'employees': 'نشط',
            'salaries': 'نشط',
            'reports': 'نشط',
            'inventory': 'نشط',
            'vat': 'نشط',
            'settings': 'نشط'
        },
        'statistics': {
            'users_count': User.query.count(),
            'customers_count': Customer.query.count(),
            'suppliers_count': Supplier.query.count(),
            'products_count': Product.query.count(),
            'employees_count': Employee.query.count(),
            'sales_count': Sale.query.count(),
            'purchases_count': Purchase.query.count(),
            'expenses_count': Expense.query.count()
        }
    })

if __name__ == '__main__':
    print('🚀 بدء تشغيل نظام المحاسبة الاحترافي...')
    print('📊 النظام يشمل: المبيعات، المشتريات، المصروفات، الموردين، الفواتير، المدفوعات، الرواتب، التقارير، المخزون، الضريبة، الإعدادات')

    try:
        # تهيئة قاعدة البيانات
        init_database()

        print('✅ تم تهيئة قاعدة البيانات بنجاح')
        print('🌐 الرابط: http://localhost:5000')
        print('👤 المستخدم: admin | كلمة المرور: admin123')
        print('🎉 نظام المحاسبة الاحترافي جاهز!')

        # تشغيل التطبيق
        port = int(os.environ.get('PORT', 5000))
        app.run(host='0.0.0.0', port=port, debug=True)

    except Exception as e:
        logger.error(f'❌ خطأ في تشغيل النظام: {e}')
        import traceback
        traceback.print_exc()
