#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
تهيئة التطبيق الاحترافي
Professional Application Initialization
"""

import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, request, session, g
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_babel import Babel, get_locale, lazy_gettext as _l, gettext as _
from flask_wtf.csrf import CSRFProtect
from flask_compress import Compress
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# إنشاء الكائنات العامة
db = SQLAlchemy()
login_manager = LoginManager()
babel = Babel()
csrf = CSRFProtect()
compress = Compress()
cache = Cache()
limiter = Limiter(key_func=get_remote_address)

def create_app(config_class=None):
    """إنشاء وتكوين التطبيق"""
    
    app = Flask(__name__)
    
    # تحميل الإعدادات
    if config_class:
        app.config.from_object(config_class)
    else:
        from config import config
        config_name = os.environ.get('FLASK_ENV') or 'development'
        app.config.from_object(config[config_name])
    
    # تهيئة الإضافات
    init_extensions(app)
    
    # تسجيل المسارات
    register_blueprints(app)
    
    # إعداد معالجات الأخطاء
    register_error_handlers(app)
    
    # إعداد السياق العام
    register_context_processors(app)
    
    # إعداد المرشحات المخصصة
    register_template_filters(app)
    
    # إعداد الأمان
    setup_security(app)
    
    # إعداد السجلات
    setup_logging(app)
    
    # تهيئة قاعدة البيانات
    init_database(app)
    
    return app

def init_extensions(app):
    """تهيئة جميع الإضافات"""
    
    # قاعدة البيانات
    db.init_app(app)
    
    # نظام تسجيل الدخول
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'يرجى تسجيل الدخول للوصول إلى هذه الصفحة.'
    login_manager.login_message_category = 'info'
    
    # نظام اللغات
    babel.init_app(app)
    
    # حماية CSRF
    csrf.init_app(app)
    
    # ضغط المحتوى
    compress.init_app(app)
    
    # التخزين المؤقت
    cache.init_app(app)
    
    # تحديد معدل الطلبات
    limiter.init_app(app)
    
    @login_manager.user_loader
    def load_user(user_id):
        from app.models.user_enhanced import User
        return User.query.get(int(user_id))
    
    @babel.localeselector
    def get_locale():
        # 1. فحص معامل URL للغة
        requested_language = request.args.get('lang')
        if requested_language and requested_language in app.config['LANGUAGES']:
            session['language'] = requested_language
            return requested_language

        # 2. إذا كان المستخدم مسجل دخول، استخدم لغته المفضلة
        if current_user.is_authenticated and hasattr(current_user, 'preferred_language'):
            if current_user.preferred_language in app.config['LANGUAGES']:
                return current_user.preferred_language

        # 3. إذا كانت اللغة محفوظة في الجلسة
        if 'language' in session:
            if session['language'] in app.config['LANGUAGES']:
                return session['language']

        # 4. استخدم أفضل لغة من المتصفح
        return request.accept_languages.best_match(app.config['LANGUAGES']) or app.config['BABEL_DEFAULT_LOCALE']

def register_blueprints(app):
    """تسجيل جميع المسارات"""
    
    # المسارات الرئيسية
    from app.views.main import bp as main_bp
    app.register_blueprint(main_bp)
    
    # نظام المصادقة المتقدم
    from app.auth import auth_bp
    app.register_blueprint(auth_bp)

    # نظام الإدارة المتقدم
    from app.admin import admin_bp
    app.register_blueprint(admin_bp)

    # نظام اللغات المتعددة
    from app.language import language_bp
    app.register_blueprint(language_bp)

    # نظام السجلات والمراقبة
    from app.logging import logging_bp
    app.register_blueprint(logging_bp)

    # تهيئة نظام السجلات المتقدم
    from app.logging.logger import logger_manager
    logger_manager.init_app(app)
    
    # مسارات العملاء
    from app.views.customers import bp as customers_bp
    app.register_blueprint(customers_bp, url_prefix='/customers')
    
    # مسارات الفواتير
    from app.views.invoices import bp as invoices_bp
    app.register_blueprint(invoices_bp, url_prefix='/invoices')
    
    # مسارات المنتجات
    from app.views.products import bp as products_bp
    app.register_blueprint(products_bp, url_prefix='/products')
    
    # مسارات الموظفين
    from app.views.employees import bp as employees_bp
    app.register_blueprint(employees_bp, url_prefix='/employees')
    
    # مسارات المدفوعات
    from app.views.payments import bp as payments_bp
    app.register_blueprint(payments_bp, url_prefix='/payments')
    
    # مسارات التقارير
    from app.views.reports import bp as reports_bp
    app.register_blueprint(reports_bp, url_prefix='/reports')
    
    # مسارات الإعدادات
    from app.views.settings import bp as settings_bp
    app.register_blueprint(settings_bp, url_prefix='/settings')
    
    # مسارات API
    from app.views.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api/v1')

def register_error_handlers(app):
    """تسجيل معالجات الأخطاء"""
    
    @app.errorhandler(400)
    def bad_request(error):
        from flask import render_template
        return render_template('errors/400.html'), 400
    
    @app.errorhandler(403)
    def forbidden(error):
        from flask import render_template
        return render_template('errors/403.html'), 403
    
    @app.errorhandler(404)
    def not_found(error):
        from flask import render_template
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        from flask import render_template
        db.session.rollback()
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(429)
    def ratelimit_handler(e):
        from flask import render_template, jsonify
        if request.is_json:
            return jsonify({'error': 'تم تجاوز الحد المسموح من الطلبات'}), 429
        return render_template('errors/429.html'), 429

def register_context_processors(app):
    """تسجيل معالجات السياق العام"""
    
    @app.context_processor
    def inject_global_vars():
        """حقن متغيرات عامة في جميع القوالب"""
        return {
            'app_name': 'نظام المحاسبة الاحترافي',
            'app_version': '2.0.0',
            'current_year': 2025,
            'supported_languages': app.config['LANGUAGES'],
            'current_language': get_locale()
        }
    
    @app.before_request
    def before_request():
        """تنفيذ قبل كل طلب"""
        g.locale = str(get_locale())
        
        # تسجيل الطلب للمراقبة
        if current_user.is_authenticated:
            from app.models.audit_log import AuditLog
            # تسجيل النشاط (يمكن تحسينه لاحقاً)
            pass

def register_template_filters(app):
    """تسجيل المرشحات المخصصة للقوالب"""
    
    @app.template_filter('currency')
    def currency_filter(amount):
        """تنسيق العملة"""
        if amount is None:
            return '0.00 ر.س'
        return f'{amount:,.2f} ر.س'
    
    @app.template_filter('percentage')
    def percentage_filter(value):
        """تنسيق النسبة المئوية"""
        if value is None:
            return '0%'
        return f'{value:.1f}%'
    
    @app.template_filter('datetime_format')
    def datetime_format(datetime_obj, format='%Y-%m-%d %H:%M'):
        """تنسيق التاريخ والوقت"""
        if datetime_obj is None:
            return ''
        return datetime_obj.strftime(format)

def setup_security(app):
    """إعداد الأمان"""
    
    @app.after_request
    def set_security_headers(response):
        """إضافة رؤوس الأمان"""
        from config import SECURITY_HEADERS
        
        for header, value in SECURITY_HEADERS.items():
            response.headers[header] = value
        
        return response
    
    # إعداد CSRF للطلبات AJAX
    @app.before_request
    def csrf_protect():
        if request.method == "POST":
            token = session.get('_csrf_token', None)
            if not token or token != request.form.get('_csrf_token'):
                if not request.is_json:  # السماح لطلبات API JSON
                    from flask_wtf.csrf import validate_csrf
                    try:
                        validate_csrf(request.form.get('csrf_token'))
                    except:
                        pass  # سيتم التعامل معها بواسطة Flask-WTF

def setup_logging(app):
    """إعداد نظام السجلات"""
    
    if not app.debug and not app.testing:
        # إنشاء مجلد السجلات إذا لم يكن موجوداً
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        # إعداد سجل الملفات
        file_handler = RotatingFileHandler(
            app.config.get('LOG_FILE', 'logs/app.log'),
            maxBytes=app.config.get('LOG_MAX_SIZE', 10240000),
            backupCount=app.config.get('LOG_BACKUP_COUNT', 10)
        )
        
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        
        log_level = getattr(logging, app.config.get('LOG_LEVEL', 'INFO'))
        file_handler.setLevel(log_level)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(log_level)
        
        app.logger.info('تم تشغيل نظام المحاسبة الاحترافي')

def init_database(app):
    """تهيئة قاعدة البيانات"""
    
    @app.before_first_request
    def create_tables():
        """إنشاء الجداول عند أول طلب"""
        db.create_all()
        
        # إنشاء المجلدات المطلوبة
        folders = ['uploads', 'backups', 'logs']
        for folder in folders:
            if not os.path.exists(folder):
                os.makedirs(folder)
        
        # إنشاء مستخدم افتراضي إذا لم يكن موجوداً
        from app.models.user import User
        if not User.query.first():
            create_default_admin()

def create_default_admin():
    """إنشاء مستخدم مدير افتراضي"""
    from app.models.user import User
    
    admin = User(
        username='admin',
        email='admin@company.com',
        full_name='مدير النظام',
        role='super_admin',
        department='إدارة',
        is_active=True,
        can_view_reports=True,
        can_manage_invoices=True,
        can_manage_customers=True,
        can_manage_products=True,
        can_manage_employees=True,
        can_manage_payroll=True,
        can_manage_settings=True,
        can_manage_users=True
    )
    admin.set_password('admin123')  # يجب تغييرها في الإنتاج
    
    db.session.add(admin)
    db.session.commit()
    
    print("✅ تم إنشاء المستخدم الافتراضي: admin / admin123")
