#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نظام المحاسبة الاحترافي - نسخة محسنة للنشر على Render
Professional Accounting System - Render Deployment Version
"""

import os
import logging
from datetime import datetime, timezone
from functools import wraps

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

# إنشاء التطبيق
app = Flask(__name__)

# الإعدادات للإنتاج
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'fallback-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///accounting_system.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# إعداد السجلات
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# إنشاء قاعدة البيانات
db = SQLAlchemy(app)

# نموذج المستخدم
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), default='user')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # صلاحيات المستخدم
    can_view_reports = db.Column(db.Boolean, default=False)
    can_manage_invoices = db.Column(db.Boolean, default=False)
    can_manage_customers = db.Column(db.Boolean, default=False)
    can_manage_products = db.Column(db.Boolean, default=False)
    can_manage_employees = db.Column(db.Boolean, default=False)
    can_manage_settings = db.Column(db.Boolean, default=False)
    can_manage_users = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def has_permission(self, permission):
        """التحقق من الصلاحيات"""
        if self.role == 'admin':
            return True
        return getattr(self, f'can_{permission}', False)

# نماذج البيانات الأساسية
class Customer(db.Model):
    __tablename__ = 'customers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

class Invoice(db.Model):
    __tablename__ = 'invoices'
    
    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(50), unique=True, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    tax_amount = db.Column(db.Float, default=0)
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='draft')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    due_date = db.Column(db.DateTime)
    
    customer = db.relationship('Customer', backref='invoices')

class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    cost = db.Column(db.Float, default=0)
    stock_quantity = db.Column(db.Integer, default=0)
    category = db.Column(db.String(50))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# تهيئة نظام تسجيل الدخول
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'يرجى تسجيل الدخول للوصول لهذه الصفحة.'

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
                return redirect(url_for('home'))
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
                    email='admin@system.com',
                    full_name='مدير النظام',
                    role='admin',
                    is_active=True,
                    can_view_reports=True,
                    can_manage_invoices=True,
                    can_manage_customers=True,
                    can_manage_products=True,
                    can_manage_employees=True,
                    can_manage_settings=True,
                    can_manage_users=True
                )
                admin.set_password('admin123')
                db.session.add(admin)
                
                # إضافة بيانات تجريبية
                sample_customer = Customer(
                    name='شركة الأمل للتجارة',
                    email='info@alamal.com',
                    phone='0501234567',
                    address='الرياض، المملكة العربية السعودية'
                )
                db.session.add(sample_customer)
                
                sample_product = Product(
                    name='لابتوب Dell',
                    description='لابتوب Dell Inspiron 15',
                    price=3500.00,
                    cost=2800.00,
                    stock_quantity=10,
                    category='إلكترونيات'
                )
                db.session.add(sample_product)
                
                db.session.commit()
                logger.info('تم إنشاء البيانات الأولية بنجاح')
            
            logger.info('تم تهيئة قاعدة البيانات بنجاح')
            
        except Exception as e:
            logger.error(f'خطأ في تهيئة قاعدة البيانات: {e}')
            db.session.rollback()

# إضافة datetime إلى سياق القوالب
@app.context_processor
def inject_datetime():
    return {'datetime': datetime}

# المسارات الأساسية
@app.route('/')
def home():
    """الصفحة الرئيسية"""
    return render_template_string('''
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🎉 نظام المحاسبة الاحترافي</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <style>
            body {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: white;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .main-card {
                background: rgba(255,255,255,0.95);
                color: #2c3e50;
                border-radius: 20px;
                padding: 50px;
                text-align: center;
                max-width: 800px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            }
            .btn-main {
                background: linear-gradient(45deg, #28a745, #20c997);
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
        <div class="main-card">
            <div style="font-size: 4rem; color: #28a745; margin-bottom: 30px;">
                <i class="fas fa-check-circle"></i>
            </div>
            
            <h1 class="mb-4">🎉 نظام المحاسبة الاحترافي</h1>
            <p class="lead mb-4">نظام محاسبة متكامل يعمل على Render بنجاح!</p>
            
            <div class="alert alert-success">
                <h5><i class="fas fa-cloud me-2"></i>مرحوب على Render!</h5>
                <p class="mb-0">النظام يعمل بنجاح على منصة Render السحابية</p>
            </div>
            
            <div class="mt-4">
                <a href="{{ url_for('login') }}" class="btn-main">
                    <i class="fas fa-sign-in-alt me-2"></i>تسجيل الدخول
                </a>
                <a href="{{ url_for('api_status') }}" class="btn-main">
                    <i class="fas fa-info-circle me-2"></i>حالة النظام
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
        
        if user and user.check_password(password):
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
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                min-height: 100vh; 
                display: flex; 
                align-items: center; 
            }
            .login-card { 
                background: white; 
                border-radius: 20px; 
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
                        <h3 class="text-center mb-4">تسجيل الدخول</h3>
                        
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
                            
                            <button type="submit" class="btn btn-primary w-100">دخول</button>
                        </form>
                        
                        <div class="text-center mt-3">
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
    """لوحة التحكم"""
    return render_template_string(f'''
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="UTF-8">
        <title>لوحة التحكم</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <style>
            body {{ background-color: #f8f9fa; }}
            .navbar {{ background: linear-gradient(45deg, #667eea, #764ba2); }}
            .stat-card {{
                background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
                color: white;
                border-radius: 15px;
                padding: 25px;
                margin-bottom: 20px;
                text-align: center;
            }}
        </style>
    </head>
    <body>
        <nav class="navbar navbar-expand-lg navbar-dark">
            <div class="container">
                <a class="navbar-brand" href="{{ url_for('dashboard') }}">نظام المحاسبة</a>
                <div class="navbar-nav ms-auto">
                    <a class="nav-link" href="{{ url_for('logout') }}">خروج</a>
                </div>
            </div>
        </nav>

        <div class="container mt-4">
            <div class="alert alert-success text-center">
                <h2>🎉 مرحباً {{{{ current_user.full_name }}}}!</h2>
                <p>النظام يعمل بنجاح على Render</p>
            </div>

            <div class="row">
                <div class="col-lg-3 col-md-6">
                    <div class="stat-card">
                        <h3>{{{{ Customer.query.count() }}}}</h3>
                        <p><i class="fas fa-users me-2"></i>العملاء</p>
                    </div>
                </div>
                <div class="col-lg-3 col-md-6">
                    <div class="stat-card">
                        <h3>{{{{ Invoice.query.count() }}}}</h3>
                        <p><i class="fas fa-file-invoice me-2"></i>الفواتير</p>
                    </div>
                </div>
                <div class="col-lg-3 col-md-6">
                    <div class="stat-card">
                        <h3>{{{{ Product.query.count() }}}}</h3>
                        <p><i class="fas fa-box me-2"></i>المنتجات</p>
                    </div>
                </div>
                <div class="col-lg-3 col-md-6">
                    <div class="stat-card">
                        <h3>{{{{ User.query.count() }}}}</h3>
                        <p><i class="fas fa-user-tie me-2"></i>المستخدمين</p>
                    </div>
                </div>
            </div>

            <div class="card">
                <div class="card-body">
                    <h4>🚀 النظام يعمل على Render بنجاح!</h4>
                    <p>تم نشر النظام بنجاح على منصة Render السحابية.</p>
                </div>
            </div>
        </div>
    </body>
    </html>
    ''')

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
        'message': 'النظام يعمل بنجاح على Render',
        'version': '1.0.0-render',
        'database': 'متصلة',
        'users_count': User.query.count(),
        'customers_count': Customer.query.count(),
        'invoices_count': Invoice.query.count(),
        'products_count': Product.query.count(),
        'deployment': 'Render Cloud Platform'
    })

if __name__ == '__main__':
    # تهيئة قاعدة البيانات
    init_database()

    # تشغيل التطبيق
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
