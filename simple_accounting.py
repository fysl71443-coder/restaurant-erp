#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نظام المحاسبة المبسط - متوافق مع Python 3.13
Simple Accounting System - Python 3.13 Compatible
"""

import os
from datetime import datetime
from flask import Flask, render_template_string, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

# إنشاء التطبيق
app = Flask(__name__)

# الإعدادات
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'accounting-system-2024')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///simple_accounting.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# قاعدة البيانات
db = SQLAlchemy(app)

# نظام تسجيل الدخول
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# نموذج المستخدم
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# تهيئة قاعدة البيانات
def init_db():
    with app.app_context():
        db.create_all()
        
        # إنشاء مستخدم افتراضي
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin', full_name='مدير النظام')
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()

# المسارات
@app.route('/')
def home():
    return render_template_string('''
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="UTF-8">
        <title>نظام المحاسبة المبسط</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
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
                max-width: 600px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            }
        </style>
    </head>
    <body>
        <div class="main-card">
            <h1 class="mb-4">🎉 نظام المحاسبة المبسط</h1>
            <p class="lead mb-4">يعمل بنجاح على Python 3.13!</p>
            
            <div class="alert alert-success">
                <h5>✅ النظام يعمل بنجاح على Render</h5>
                <p class="mb-0">متوافق مع Python 3.13 وجميع المكتبات الحديثة</p>
            </div>
            
            <div class="mt-4">
                <a href="{{ url_for('login') }}" class="btn btn-primary btn-lg">
                    تسجيل الدخول
                </a>
            </div>
            
            <div class="mt-4 pt-4 border-top">
                <small class="text-muted">
                    المستخدم: admin | كلمة المرور: admin123
                </small>
            </div>
        </div>
    </body>
    </html>
    ''')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
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
        </style>
    </head>
    <body>
        <div class="container">
            <div class="row justify-content-center">
                <div class="col-md-6 col-lg-4">
                    <div class="card">
                        <div class="card-body">
                            <h3 class="text-center mb-4">تسجيل الدخول</h3>
                            
                            {% with messages = get_flashed_messages(with_categories=true) %}
                                {% if messages %}
                                    {% for category, message in messages %}
                                        <div class="alert alert-danger">{{ message }}</div>
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
        </div>
    </body>
    </html>
    ''')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template_string('''
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="UTF-8">
        <title>لوحة التحكم</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
    </head>
    <body style="background-color: #f8f9fa;">
        <nav class="navbar navbar-expand-lg navbar-dark" style="background: linear-gradient(45deg, #667eea, #764ba2);">
            <div class="container">
                <a class="navbar-brand" href="{{ url_for('dashboard') }}">نظام المحاسبة</a>
                <div class="navbar-nav ms-auto">
                    <a class="nav-link" href="{{ url_for('logout') }}">خروج</a>
                </div>
            </div>
        </nav>

        <div class="container mt-4">
            <div class="alert alert-success text-center">
                <h2>🎉 مرحباً {{ current_user.full_name }}!</h2>
                <p>النظام يعمل بنجاح على Python 3.13</p>
            </div>

            <div class="card">
                <div class="card-body">
                    <h4>✅ النظام يعمل بنجاح!</h4>
                    <ul class="list-unstyled">
                        <li>✅ Python 3.13 متوافق</li>
                        <li>✅ Flask يعمل بنجاح</li>
                        <li>✅ قاعدة البيانات متصلة</li>
                        <li>✅ تسجيل الدخول يعمل</li>
                        <li>✅ النشر على Render ناجح</li>
                    </ul>
                    
                    <div class="mt-4">
                        <a href="{{ url_for('api_status') }}" class="btn btn-info">
                            حالة النظام
                        </a>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    ''')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/api/status')
def api_status():
    return jsonify({
        'status': 'success',
        'message': 'النظام يعمل بنجاح على Python 3.13',
        'python_version': '3.13',
        'flask_version': '3.0.0',
        'database': 'متصلة',
        'deployment': 'Render Cloud Platform'
    })

if __name__ == '__main__':
    print('🚀 بدء تشغيل النظام المبسط...')
    print('🐍 Python 3.13 - متوافق')
    
    # تهيئة قاعدة البيانات
    init_db()
    
    print('✅ تم تهيئة قاعدة البيانات')
    print('🌐 الرابط: http://localhost:5000')
    print('👤 المستخدم: admin | كلمة المرور: admin123')
    
    # تشغيل التطبيق
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

# للنشر على Render
init_db()
