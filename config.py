#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
إعدادات التطبيق الاحترافية
Professional Application Configuration
"""

import os
from datetime import timedelta

class Config:
    """الإعدادات الأساسية للتطبيق"""
    
    # إعدادات أساسية
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # إعدادات قاعدة البيانات
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///instance/accounting_system_pro.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'connect_args': {
            'check_same_thread': False,
            'timeout': 30
        }
    }
    
    # إعدادات الأمان
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600  # ساعة واحدة
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    
    # إعدادات التطبيق
    LANGUAGES = ['ar', 'en']
    BABEL_DEFAULT_LOCALE = 'ar'
    BABEL_DEFAULT_TIMEZONE = 'Asia/Riyadh'
    
    # إعدادات الملفات
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'xlsx', 'csv'}
    
    # إعدادات التخزين المؤقت
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 300
    
    # إعدادات البريد الإلكتروني
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'localhost'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    # إعدادات السجلات
    LOG_LEVEL = os.environ.get('LOG_LEVEL') or 'INFO'
    LOG_FILE = 'logs/app.log'
    LOG_MAX_SIZE = 10 * 1024 * 1024  # 10MB
    LOG_BACKUP_COUNT = 5
    
    # إعدادات النسخ الاحتياطي
    BACKUP_FOLDER = 'backups'
    BACKUP_RETENTION_DAYS = 30
    AUTO_BACKUP_ENABLED = True
    BACKUP_SCHEDULE = '0 2 * * *'  # يومياً في الساعة 2 صباحاً
    
    # إعدادات الأداء
    ENABLE_COMPRESSION = True
    COMPRESSION_LEVEL = 6
    MINIFY_HTML = True
    
    # إعدادات الأمان المتقدمة
    SECURITY_PASSWORD_SALT = os.environ.get('SECURITY_PASSWORD_SALT') or 'password-salt-change-in-production'
    SECURITY_REGISTERABLE = False
    SECURITY_RECOVERABLE = True
    SECURITY_TRACKABLE = True
    SECURITY_CHANGEABLE = True
    SECURITY_CONFIRMABLE = False
    
    # إعدادات المصادقة الثنائية
    TWO_FACTOR_ENABLED = False
    TWO_FACTOR_ISSUER = 'Accounting System Pro'
    
    # إعدادات API
    API_RATE_LIMIT = '100 per hour'
    API_VERSION = 'v1'

    # إعدادات اللغة والترجمة المتقدمة
    LANGUAGES = {
        'ar': 'العربية',
        'en': 'English'
    }
    DEFAULT_LANGUAGE = 'ar'
    BABEL_DEFAULT_LOCALE = 'ar'
    BABEL_DEFAULT_TIMEZONE = 'Asia/Riyadh'

    # مجلدات الترجمة
    BABEL_TRANSLATION_DIRECTORIES = 'translations'

    # إعدادات التاريخ والوقت
    TIMEZONE = 'Asia/Riyadh'
    DATE_FORMAT = '%Y-%m-%d'
    TIME_FORMAT = '%H:%M:%S'
    DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
    
    @staticmethod
    def init_app(app):
        """تهيئة التطبيق مع الإعدادات"""
        pass

class DevelopmentConfig(Config):
    """إعدادات بيئة التطوير"""
    DEBUG = True
    TESTING = False
    
    # إعدادات قاعدة البيانات للتطوير
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///instance/accounting_system_dev.db'
    
    # إعدادات الأمان للتطوير
    SESSION_COOKIE_SECURE = False
    WTF_CSRF_ENABLED = False  # تعطيل CSRF في التطوير للسهولة
    
    # إعدادات السجلات للتطوير
    LOG_LEVEL = 'DEBUG'
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        
        # إعداد سجلات التطوير
        import logging
        from logging.handlers import RotatingFileHandler
        
        if not app.debug and not app.testing:
            if not os.path.exists('logs'):
                os.mkdir('logs')
            
            file_handler = RotatingFileHandler(
                'logs/accounting_dev.log',
                maxBytes=10240,
                backupCount=10
            )
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
            ))
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)
            app.logger.setLevel(logging.INFO)
            app.logger.info('Accounting System startup')

class TestingConfig(Config):
    """إعدادات بيئة الاختبار"""
    TESTING = True
    DEBUG = False
    
    # إعدادات قاعدة البيانات للاختبار
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
    # إعدادات الأمان للاختبار
    WTF_CSRF_ENABLED = False
    SESSION_COOKIE_SECURE = False
    
    # تعطيل النسخ الاحتياطي في الاختبار
    AUTO_BACKUP_ENABLED = False

class ProductionConfig(Config):
    """إعدادات بيئة الإنتاج"""
    DEBUG = False
    TESTING = False
    
    # إعدادات قاعدة البيانات للإنتاج
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///instance/accounting_system_prod.db'
    
    # إعدادات الأمان للإنتاج
    SESSION_COOKIE_SECURE = True
    WTF_CSRF_ENABLED = True
    
    # تفعيل المصادقة الثنائية في الإنتاج
    TWO_FACTOR_ENABLED = True
    
    # إعدادات السجلات للإنتاج
    LOG_LEVEL = 'WARNING'
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        
        # إعداد سجلات الإنتاج
        import logging
        from logging.handlers import RotatingFileHandler, SMTPHandler
        
        # سجلات الملفات
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        file_handler = RotatingFileHandler(
            'logs/accounting_prod.log',
            maxBytes=cls.LOG_MAX_SIZE,
            backupCount=cls.LOG_BACKUP_COUNT
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
        # إرسال الأخطاء الحرجة بالبريد الإلكتروني
        if cls.MAIL_SERVER:
            auth = None
            if cls.MAIL_USERNAME or cls.MAIL_PASSWORD:
                auth = (cls.MAIL_USERNAME, cls.MAIL_PASSWORD)
            
            secure = None
            if cls.MAIL_USE_TLS:
                secure = ()
            
            mail_handler = SMTPHandler(
                mailhost=(cls.MAIL_SERVER, cls.MAIL_PORT),
                fromaddr='no-reply@' + cls.MAIL_SERVER,
                toaddrs=['admin@company.com'],
                subject='Accounting System Error',
                credentials=auth,
                secure=secure
            )
            mail_handler.setLevel(logging.ERROR)
            app.logger.addHandler(mail_handler)
        
        app.logger.setLevel(logging.INFO)
        app.logger.info('Accounting System Production startup')

class DockerConfig(ProductionConfig):
    """إعدادات Docker"""
    
    @classmethod
    def init_app(cls, app):
        ProductionConfig.init_app(app)
        
        # إعداد سجلات Docker
        import logging
        app.logger.setLevel(logging.INFO)
        
        # إرسال السجلات إلى stdout في Docker
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.INFO)
        app.logger.addHandler(stream_handler)

# خريطة الإعدادات
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'docker': DockerConfig,
    'default': DevelopmentConfig
}

# إعدادات إضافية للأمان
SECURITY_HEADERS = {
    'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
    'X-Content-Type-Options': 'nosniff',
    'X-Frame-Options': 'DENY',
    'X-XSS-Protection': '1; mode=block',
    'Content-Security-Policy': (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
        "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
        "font-src 'self' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
        "img-src 'self' data: https:; "
        "connect-src 'self';"
    )
}

# إعدادات قاعدة البيانات المتقدمة
DATABASE_SETTINGS = {
    'sqlite': {
        'pragmas': {
            'journal_mode': 'WAL',
            'synchronous': 'NORMAL',
            'cache_size': -64000,  # 64MB
            'temp_store': 'MEMORY',
            'mmap_size': 268435456,  # 256MB
            'foreign_keys': 'ON'
        }
    },
    'postgresql': {
        'pool_size': 10,
        'max_overflow': 20,
        'pool_pre_ping': True,
        'pool_recycle': 3600
    },
    'mysql': {
        'pool_size': 10,
        'max_overflow': 20,
        'pool_pre_ping': True,
        'pool_recycle': 3600,
        'charset': 'utf8mb4'
    }
}

# إعدادات التخزين المؤقت المتقدمة
CACHE_SETTINGS = {
    'redis': {
        'CACHE_TYPE': 'redis',
        'CACHE_REDIS_URL': os.environ.get('REDIS_URL') or 'redis://localhost:6379/0',
        'CACHE_DEFAULT_TIMEOUT': 300,
        'CACHE_KEY_PREFIX': 'accounting_'
    },
    'memcached': {
        'CACHE_TYPE': 'memcached',
        'CACHE_MEMCACHED_SERVERS': ['127.0.0.1:11211'],
        'CACHE_DEFAULT_TIMEOUT': 300,
        'CACHE_KEY_PREFIX': 'accounting_'
    }
}

# إعدادات المراقبة والتحليل
MONITORING_SETTINGS = {
    'enable_metrics': True,
    'metrics_endpoint': '/metrics',
    'health_check_endpoint': '/health',
    'performance_monitoring': True,
    'error_tracking': True,
    'user_analytics': True
}
