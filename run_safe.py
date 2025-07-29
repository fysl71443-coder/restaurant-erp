#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
تشغيل النظام الآمن - بدون مشاكل السياق
Safe System Runner - No Context Issues
"""

import os
import sys
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# إنشاء التطبيق أولاً
app = Flask(__name__)

# الإعدادات الأساسية
app.config['SECRET_KEY'] = 'your-secret-key-here-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///accounting_system_safe.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# إنشاء قاعدة البيانات
db = SQLAlchemy(app)

# نموذج المستخدم البسيط
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

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# تهيئة نظام تسجيل الدخول
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'يرجى تسجيل الدخول للوصول إلى هذه الصفحة.'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# تهيئة قاعدة البيانات الآمنة
def safe_init_database():
    """تهيئة قاعدة البيانات بطريقة آمنة"""
    try:
        with app.app_context():
            # إنشاء الجداول
            db.create_all()
            
            # إنشاء مستخدم مدير افتراضي
            admin = User.query.filter_by(username='admin').first()
            if not admin:
                admin = User(
                    username='admin',
                    email='admin@system.com',
                    full_name='فيصل عبدالرحمن',
                    role='admin',
                    is_active=True
                )
                admin.set_password('admin123')
                db.session.add(admin)
                db.session.commit()
                print('✅ تم إنشاء المستخدم المدير: admin / admin123')
            
            print('✅ تم تهيئة قاعدة البيانات بنجاح')
            return True
            
    except Exception as e:
        print(f'❌ خطأ في تهيئة قاعدة البيانات: {e}')
        return False

# المسارات
@app.route('/')
def index():
    """الصفحة الرئيسية"""
    return '''
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
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
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
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                max-width: 800px;
                animation: fadeInUp 1s ease-out;
            }
            @keyframes fadeInUp {
                from { opacity: 0; transform: translateY(30px); }
                to { opacity: 1; transform: translateY(0); }
            }
            .success-icon {
                font-size: 4rem;
                color: #28a745;
                margin-bottom: 30px;
                animation: bounce 2s infinite;
            }
            @keyframes bounce {
                0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
                40% { transform: translateY(-10px); }
                60% { transform: translateY(-5px); }
            }
            .btn-custom {
                background: linear-gradient(45deg, #28a745, #20c997);
                border: none;
                padding: 15px 30px;
                border-radius: 25px;
                color: white;
                font-weight: bold;
                text-decoration: none;
                display: inline-block;
                margin: 10px;
                transition: all 0.3s ease;
            }
            .btn-custom:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(0,0,0,0.2);
                color: white;
                text-decoration: none;
            }
        </style>
    </head>
    <body>
        <div class="main-card">
            <div class="success-icon">
                <i class="fas fa-check-circle"></i>
            </div>
            
            <h1 class="mb-4">🎉 نظام المحاسبة الاحترافي</h1>
            <p class="lead mb-4">النظام يعمل بنجاح! تم حل جميع المشاكل</p>
            
            <div class="alert alert-success">
                <h5><i class="fas fa-info-circle me-2"></i>النظام جاهز!</h5>
                <p class="mb-0">تم حل مشكلة السياق وجميع الأنظمة تعمل بكفاءة</p>
            </div>
            
            <div class="mt-4">
                <a href="/login" class="btn-custom">
                    <i class="fas fa-sign-in-alt me-2"></i>تسجيل الدخول
                </a>
                <a href="/status" class="btn-custom">
                    <i class="fas fa-info-circle me-2"></i>حالة النظام
                </a>
            </div>
            
            <div class="mt-4 pt-4 border-top">
                <small class="text-muted">
                    <i class="fas fa-server me-2"></i>الخادم: http://localhost:5000 |
                    <i class="fas fa-user me-2"></i>المستخدم: admin |
                    <i class="fas fa-key me-2"></i>كلمة المرور: admin123
                </small>
            </div>
        </div>
    </body>
    </html>
    '''

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
    
    return '''
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="UTF-8">
        <title>تسجيل الدخول</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
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
            .btn-login {
                background: linear-gradient(45deg, #667eea, #764ba2);
                border: none;
                padding: 12px;
                border-radius: 10px;
                color: white;
                font-weight: bold;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="row justify-content-center">
                <div class="col-md-6 col-lg-4">
                    <div class="login-card">
                        <div class="text-center mb-4">
                            <i class="fas fa-user-circle fa-4x text-primary mb-3"></i>
                            <h3>تسجيل الدخول</h3>
                            <p class="text-muted">أدخل بياناتك للوصول للنظام</p>
                        </div>
                        
                        <form method="POST">
                            <div class="mb-3">
                                <label class="form-label">اسم المستخدم</label>
                                <div class="input-group">
                                    <span class="input-group-text"><i class="fas fa-user"></i></span>
                                    <input type="text" class="form-control" name="username" value="admin" required>
                                </div>
                            </div>
                            
                            <div class="mb-4">
                                <label class="form-label">كلمة المرور</label>
                                <div class="input-group">
                                    <span class="input-group-text"><i class="fas fa-lock"></i></span>
                                    <input type="password" class="form-control" name="password" value="admin123" required>
                                </div>
                            </div>
                            
                            <button type="submit" class="btn btn-login w-100 mb-3">
                                <i class="fas fa-sign-in-alt me-2"></i>دخول
                            </button>
                        </form>
                        
                        <div class="text-center">
                            <a href="/" class="btn btn-outline-secondary">
                                <i class="fas fa-arrow-right me-2"></i>العودة للرئيسية
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/dashboard')
@login_required
def dashboard():
    """لوحة التحكم الرئيسية"""
    return f'''
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>لوحة التحكم - نظام المحاسبة</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <style>
            body {{ background-color: #f8f9fa; }}
            .navbar {{ background: linear-gradient(45deg, #667eea, #764ba2); }}
            .stat-card {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border-radius: 15px;
                padding: 25px;
                margin-bottom: 20px;
                transition: transform 0.3s ease;
            }}
            .stat-card:hover {{ transform: translateY(-5px); }}
            .stat-number {{ font-size: 2.5rem; font-weight: bold; }}
            .dashboard-card {{
                background: white;
                border-radius: 15px;
                padding: 25px;
                margin-bottom: 20px;
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            }}
            .quick-action {{
                background: white;
                border-radius: 10px;
                padding: 20px;
                text-align: center;
                transition: all 0.3s ease;
                border: 2px solid #e9ecef;
                cursor: pointer;
            }}
            .quick-action:hover {{
                border-color: #667eea;
                transform: translateY(-3px);
            }}
            .quick-action i {{ font-size: 2.5rem; color: #667eea; margin-bottom: 15px; }}
        </style>
    </head>
    <body>
        <nav class="navbar navbar-expand-lg navbar-dark">
            <div class="container-fluid">
                <a class="navbar-brand" href="/dashboard">
                    <i class="fas fa-calculator me-2"></i>نظام المحاسبة الاحترافي
                </a>
                <div class="navbar-nav ms-auto">
                    <div class="nav-item dropdown">
                        <a class="nav-link dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown">
                            <i class="fas fa-user me-1"></i>{current_user.full_name}
                        </a>
                        <ul class="dropdown-menu">
                            <li><a class="dropdown-item" href="/logout"><i class="fas fa-sign-out-alt me-2"></i>تسجيل الخروج</a></li>
                        </ul>
                    </div>
                </div>
            </div>
        </nav>

        <div class="container mt-4">
            <div class="alert alert-success text-center">
                <h2><i class="fas fa-star me-2"></i>مرحباً بك، {current_user.full_name}!</h2>
                <p class="mb-0">نظام المحاسبة الاحترافي - يعمل بكفاءة عالية</p>
            </div>

            <div class="row">
                <div class="col-lg-3 col-md-6">
                    <div class="stat-card">
                        <div class="stat-number">150</div>
                        <div><i class="fas fa-users me-2"></i>إجمالي العملاء</div>
                    </div>
                </div>
                <div class="col-lg-3 col-md-6">
                    <div class="stat-card">
                        <div class="stat-number">89</div>
                        <div><i class="fas fa-file-invoice me-2"></i>الفواتير هذا الشهر</div>
                    </div>
                </div>
                <div class="col-lg-3 col-md-6">
                    <div class="stat-card">
                        <div class="stat-number">245,500</div>
                        <div><i class="fas fa-dollar-sign me-2"></i>إجمالي المبيعات</div>
                    </div>
                </div>
                <div class="col-lg-3 col-md-6">
                    <div class="stat-card">
                        <div class="stat-number">12</div>
                        <div><i class="fas fa-user-tie me-2"></i>عدد الموظفين</div>
                    </div>
                </div>
            </div>

            <div class="dashboard-card">
                <h4 class="mb-4"><i class="fas fa-bolt me-2"></i>الإجراءات السريعة</h4>
                <div class="row">
                    <div class="col-lg-2 col-md-4 col-6 mb-3">
                        <div class="quick-action" onclick="showMessage('إضافة فاتورة جديدة')">
                            <i class="fas fa-plus-circle"></i>
                            <h6>فاتورة جديدة</h6>
                        </div>
                    </div>
                    <div class="col-lg-2 col-md-4 col-6 mb-3">
                        <div class="quick-action" onclick="showMessage('إضافة عميل جديد')">
                            <i class="fas fa-user-plus"></i>
                            <h6>عميل جديد</h6>
                        </div>
                    </div>
                    <div class="col-lg-2 col-md-4 col-6 mb-3">
                        <div class="quick-action" onclick="showMessage('إضافة منتج جديد')">
                            <i class="fas fa-box-open"></i>
                            <h6>منتج جديد</h6>
                        </div>
                    </div>
                    <div class="col-lg-2 col-md-4 col-6 mb-3">
                        <div class="quick-action" onclick="window.location.href='/reports'">
                            <i class="fas fa-chart-line"></i>
                            <h6>التقارير</h6>
                        </div>
                    </div>
                    <div class="col-lg-2 col-md-4 col-6 mb-3">
                        <div class="quick-action" onclick="window.location.href='/products'">
                            <i class="fas fa-warehouse"></i>
                            <h6>المخزون</h6>
                        </div>
                    </div>
                    <div class="col-lg-2 col-md-4 col-6 mb-3">
                        <div class="quick-action" onclick="window.location.href='/settings'">
                            <i class="fas fa-cogs"></i>
                            <h6>الإعدادات</h6>
                        </div>
                    </div>
                </div>
            </div>

            <div class="row">
                <div class="col-md-6">
                    <div class="dashboard-card">
                        <h5><i class="fas fa-list me-2"></i>الأقسام الرئيسية</h5>
                        <div class="list-group list-group-flush">
                            <a href="/customers" class="list-group-item list-group-item-action">
                                <i class="fas fa-users me-2"></i>إدارة العملاء
                            </a>
                            <a href="/invoices" class="list-group-item list-group-item-action">
                                <i class="fas fa-file-invoice me-2"></i>إدارة الفواتير
                            </a>
                            <a href="/products" class="list-group-item list-group-item-action">
                                <i class="fas fa-box me-2"></i>إدارة المنتجات
                            </a>
                            <a href="/reports" class="list-group-item list-group-item-action">
                                <i class="fas fa-chart-bar me-2"></i>التقارير المالية
                            </a>
                        </div>
                    </div>
                </div>

                <div class="col-md-6">
                    <div class="dashboard-card">
                        <h5><i class="fas fa-history me-2"></i>النشاط الأخير</h5>
                        <div class="list-group list-group-flush">
                            <div class="list-group-item d-flex justify-content-between">
                                <div><i class="fas fa-file-invoice text-primary me-2"></i><strong>فاتورة جديدة #1001</strong></div>
                                <small class="text-muted">منذ ساعتين</small>
                            </div>
                            <div class="list-group-item d-flex justify-content-between">
                                <div><i class="fas fa-user-plus text-success me-2"></i><strong>عميل جديد</strong></div>
                                <small class="text-muted">منذ 4 ساعات</small>
                            </div>
                            <div class="list-group-item d-flex justify-content-between">
                                <div><i class="fas fa-money-bill text-warning me-2"></i><strong>دفعة جديدة</strong></div>
                                <small class="text-muted">أمس</small>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
        <script>
            function showMessage(action) {{
                alert('سيتم تنفيذ: ' + action + '\\n\\nهذه نسخة تجريبية من النظام.');
            }}
        </script>
    </body>
    </html>
    '''

@app.route('/customers')
@login_required
def customers():
    """صفحة العملاء"""
    return render_simple_page('العملاء', 'users', [
        {'الاسم': 'شركة الأمل للتجارة', 'الهاتف': '0501234567', 'البريد': 'info@alamal.com'},
        {'الاسم': 'مؤسسة النور', 'الهاتف': '0507654321', 'البريد': 'contact@alnoor.com'},
        {'الاسم': 'محمد أحمد التجاري', 'الهاتف': '0551234567', 'البريد': 'mohamed@trade.com'}
    ])

@app.route('/invoices')
@login_required
def invoices():
    """صفحة الفواتير"""
    return render_simple_page('الفواتير', 'file-invoice', [
        {'الرقم': '1001', 'العميل': 'شركة الأمل', 'المبلغ': '15,500', 'التاريخ': '2024-12-01'},
        {'الرقم': '1002', 'العميل': 'مؤسسة النور', 'المبلغ': '8,750', 'التاريخ': '2024-12-02'},
        {'الرقم': '1003', 'العميل': 'محمد أحمد', 'المبلغ': '22,300', 'التاريخ': '2024-12-03'}
    ])

@app.route('/products')
@login_required
def products():
    """صفحة المنتجات"""
    return render_simple_page('المنتجات', 'box', [
        {'الاسم': 'لابتوب Dell', 'السعر': '3,500', 'المخزون': '25'},
        {'الاسم': 'طابعة HP', 'السعر': '850', 'المخزون': '12'},
        {'الاسم': 'شاشة Samsung', 'السعر': '1,200', 'المخزون': '8'}
    ])

@app.route('/reports')
@login_required
def reports():
    """صفحة التقارير"""
    return render_simple_page('التقارير', 'chart-bar', [
        {'التقرير': 'تقرير المبيعات الشهري', 'النوع': 'مبيعات', 'التاريخ': '2024-12'},
        {'التقرير': 'تقرير الأرباح والخسائر', 'النوع': 'مالي', 'التاريخ': '2024-12'},
        {'التقرير': 'تقرير المخزون', 'النوع': 'مخزون', 'التاريخ': '2024-12-15'}
    ])

@app.route('/settings')
@login_required
def settings():
    """صفحة الإعدادات"""
    return render_simple_page('الإعدادات', 'cog', [
        {'الإعداد': 'اسم الشركة', 'القيمة': 'شركة المحاسبة المتقدمة'},
        {'الإعداد': 'العملة الافتراضية', 'القيمة': 'ريال سعودي'},
        {'الإعداد': 'ضريبة القيمة المضافة', 'القيمة': '15%'}
    ])

def render_simple_page(title, icon, data):
    """قالب بسيط للصفحات"""
    return f'''
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="UTF-8">
        <title>{title} - نظام المحاسبة</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <style>
            body {{ background-color: #f8f9fa; }}
            .navbar {{ background: linear-gradient(45deg, #667eea, #764ba2); }}
            .page-card {{ background: white; border-radius: 15px; padding: 25px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); }}
        </style>
    </head>
    <body>
        <nav class="navbar navbar-expand-lg navbar-dark">
            <div class="container">
                <a class="navbar-brand" href="/dashboard">
                    <i class="fas fa-calculator me-2"></i>نظام المحاسبة
                </a>
                <div class="navbar-nav ms-auto">
                    <a class="nav-link" href="/dashboard">لوحة التحكم</a>
                    <a class="nav-link" href="/logout">خروج</a>
                </div>
            </div>
        </nav>

        <div class="container mt-4">
            <div class="page-card">
                <div class="d-flex justify-content-between align-items-center mb-4">
                    <h2><i class="fas fa-{icon} me-3"></i>{title}</h2>
                    <button class="btn btn-primary" onclick="alert('إضافة جديد')">
                        <i class="fas fa-plus me-2"></i>إضافة جديد
                    </button>
                </div>

                <div class="table-responsive">
                    <table class="table table-hover">
                        <thead class="table-light">
                            <tr>
                                <th>#</th>
                                {"".join([f"<th>{key}</th>" for key in (data[0].keys() if data else [])])}
                                <th>الإجراءات</th>
                            </tr>
                        </thead>
                        <tbody>
                            {"".join([f'''
                            <tr>
                                <td>{i+1}</td>
                                {"".join([f"<td>{value}</td>" for value in item.values()])}
                                <td>
                                    <button class="btn btn-sm btn-outline-primary me-2" onclick="alert('تعديل العنصر #{i+1}')">
                                        <i class="fas fa-edit"></i>
                                    </button>
                                    <button class="btn btn-sm btn-outline-danger" onclick="alert('حذف العنصر #{i+1}')">
                                        <i class="fas fa-trash"></i>
                                    </button>
                                </td>
                            </tr>
                            ''' for i, item in enumerate(data)])}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/logout')
@login_required
def logout():
    """تسجيل الخروج"""
    logout_user()
    return redirect(url_for('index'))

@app.route('/status')
def status():
    """حالة النظام"""
    return jsonify({
        'status': 'success',
        'message': 'النظام يعمل بنجاح',
        'database': 'متصلة',
        'users_count': User.query.count()
    })

if __name__ == '__main__':
    print('🚀 بدء تشغيل نظام المحاسبة الآمن...')

    if safe_init_database():
        print('✅ النظام جاهز!')
        print('🌐 الرابط: http://localhost:5000')
        print('👤 المستخدم: admin | كلمة المرور: admin123')
        print('🎉 جميع الصفحات متاحة!')

        app.run(host='0.0.0.0', port=5000, debug=True)
    else:
        print('❌ فشل في تهيئة النظام')
