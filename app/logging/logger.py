#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نظام السجلات المتقدم
Advanced Logging System
"""

import os
import logging
import logging.handlers
from datetime import datetime, timedelta
from flask import current_app, request, g
from flask_login import current_user
import json
import traceback
from functools import wraps
from app import db

class CustomFormatter(logging.Formatter):
    """منسق السجلات المخصص"""
    
    def __init__(self):
        super().__init__()
        
        # ألوان للمستويات المختلفة
        self.colors = {
            'DEBUG': '\033[36m',    # سماوي
            'INFO': '\033[32m',     # أخضر
            'WARNING': '\033[33m',  # أصفر
            'ERROR': '\033[31m',    # أحمر
            'CRITICAL': '\033[35m', # بنفسجي
            'RESET': '\033[0m'      # إعادة تعيين
        }
    
    def format(self, record):
        # إضافة معلومات السياق
        if hasattr(g, 'request_id'):
            record.request_id = g.request_id
        else:
            record.request_id = 'N/A'
        
        # معلومات المستخدم
        if current_user and current_user.is_authenticated:
            record.user_id = current_user.id
            record.username = current_user.username
        else:
            record.user_id = 'N/A'
            record.username = 'Anonymous'
        
        # معلومات الطلب
        if request:
            record.ip_address = request.environ.get('HTTP_X_FORWARDED_FOR', 
                                                  request.environ.get('REMOTE_ADDR', 'N/A'))
            record.user_agent = request.headers.get('User-Agent', 'N/A')
            record.method = request.method
            record.url = request.url
        else:
            record.ip_address = 'N/A'
            record.user_agent = 'N/A'
            record.method = 'N/A'
            record.url = 'N/A'
        
        # تنسيق الرسالة
        log_format = (
            f"{self.colors.get(record.levelname, '')}"
            f"[{record.asctime}] "
            f"{record.levelname:8} "
            f"[{record.request_id}] "
            f"[{record.username}@{record.ip_address}] "
            f"{record.name}: {record.getMessage()}"
            f"{self.colors['RESET']}"
        )
        
        # إضافة معلومات الاستثناء إذا وجدت
        if record.exc_info:
            log_format += f"\n{self.formatException(record.exc_info)}"
        
        return log_format

class DatabaseHandler(logging.Handler):
    """معالج قاعدة البيانات للسجلات"""
    
    def emit(self, record):
        try:
            from app.models.audit_log import SystemLog
            
            # إنشاء سجل في قاعدة البيانات
            log_entry = SystemLog(
                level=record.levelname,
                logger_name=record.name,
                message=record.getMessage(),
                module=record.module,
                function=record.funcName,
                line_number=record.lineno,
                request_id=getattr(record, 'request_id', None),
                user_id=getattr(record, 'user_id', None) if getattr(record, 'user_id', None) != 'N/A' else None,
                ip_address=getattr(record, 'ip_address', None),
                user_agent=getattr(record, 'user_agent', None),
                method=getattr(record, 'method', None),
                url=getattr(record, 'url', None),
                extra_data=self._get_extra_data(record)
            )
            
            # إضافة معلومات الاستثناء
            if record.exc_info:
                log_entry.exception_type = record.exc_info[0].__name__
                log_entry.exception_message = str(record.exc_info[1])
                log_entry.stack_trace = self.formatException(record.exc_info)
            
            db.session.add(log_entry)
            db.session.commit()
            
        except Exception as e:
            # تجنب الحلقة اللانهائية في حالة خطأ في السجلات
            print(f"Error logging to database: {e}")
    
    def _get_extra_data(self, record):
        """استخراج البيانات الإضافية من السجل"""
        extra_data = {}
        
        # إضافة أي بيانات إضافية
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 
                          'filename', 'module', 'lineno', 'funcName', 'created', 
                          'msecs', 'relativeCreated', 'thread', 'threadName', 
                          'processName', 'process', 'getMessage', 'exc_info', 'exc_text', 'stack_info']:
                try:
                    json.dumps(value)  # تحقق من إمكانية التسلسل
                    extra_data[key] = value
                except (TypeError, ValueError):
                    extra_data[key] = str(value)
        
        return extra_data if extra_data else None

class LoggerManager:
    """مدير السجلات"""
    
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """تهيئة نظام السجلات"""
        self.app = app
        
        # إنشاء مجلد السجلات
        logs_dir = os.path.join(app.root_path, '..', 'logs')
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)
        
        # إعداد السجلات
        self._setup_loggers(logs_dir)
        
        # إعداد معالجات الطلبات
        self._setup_request_handlers()
    
    def _setup_loggers(self, logs_dir):
        """إعداد أنواع السجلات المختلفة"""
        
        # إعداد المنسق المخصص
        formatter = CustomFormatter()
        
        # سجل التطبيق الرئيسي
        app_logger = logging.getLogger('accounting_system')
        app_logger.setLevel(logging.DEBUG if self.app.debug else logging.INFO)
        
        # معالج الملف الدوار
        file_handler = logging.handlers.RotatingFileHandler(
            os.path.join(logs_dir, 'app.log'),
            maxBytes=10*1024*1024,  # 10 ميجابايت
            backupCount=10
        )
        file_handler.setFormatter(formatter)
        app_logger.addHandler(file_handler)
        
        # معالج وحدة التحكم
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        app_logger.addHandler(console_handler)
        
        # معالج قاعدة البيانات
        db_handler = DatabaseHandler()
        db_handler.setLevel(logging.WARNING)  # فقط التحذيرات والأخطاء
        app_logger.addHandler(db_handler)
        
        # سجل الأمان
        security_logger = logging.getLogger('security')
        security_logger.setLevel(logging.INFO)
        
        security_handler = logging.handlers.RotatingFileHandler(
            os.path.join(logs_dir, 'security.log'),
            maxBytes=5*1024*1024,  # 5 ميجابايت
            backupCount=20
        )
        security_handler.setFormatter(formatter)
        security_logger.addHandler(security_handler)
        security_logger.addHandler(db_handler)
        
        # سجل الأداء
        performance_logger = logging.getLogger('performance')
        performance_logger.setLevel(logging.INFO)
        
        performance_handler = logging.handlers.RotatingFileHandler(
            os.path.join(logs_dir, 'performance.log'),
            maxBytes=5*1024*1024,  # 5 ميجابايت
            backupCount=10
        )
        performance_handler.setFormatter(formatter)
        performance_logger.addHandler(performance_handler)
        
        # سجل قاعدة البيانات
        db_logger = logging.getLogger('sqlalchemy.engine')
        if self.app.debug:
            db_logger.setLevel(logging.INFO)
            db_handler_file = logging.handlers.RotatingFileHandler(
                os.path.join(logs_dir, 'database.log'),
                maxBytes=5*1024*1024,
                backupCount=5
            )
            db_handler_file.setFormatter(formatter)
            db_logger.addHandler(db_handler_file)
        
        # سجل الأخطاء
        error_logger = logging.getLogger('errors')
        error_logger.setLevel(logging.ERROR)
        
        error_handler = logging.handlers.RotatingFileHandler(
            os.path.join(logs_dir, 'errors.log'),
            maxBytes=10*1024*1024,
            backupCount=20
        )
        error_handler.setFormatter(formatter)
        error_logger.addHandler(error_handler)
        error_logger.addHandler(db_handler)
        
        # تعيين السجلات للتطبيق
        self.app.logger = app_logger
    
    def _setup_request_handlers(self):
        """إعداد معالجات الطلبات"""
        
        @self.app.before_request
        def before_request():
            # إنشاء معرف فريد للطلب
            import uuid
            g.request_id = str(uuid.uuid4())[:8]
            g.start_time = datetime.utcnow()
            
            # تسجيل بداية الطلب
            self.app.logger.info(f"Request started: {request.method} {request.url}")
        
        @self.app.after_request
        def after_request(response):
            # حساب وقت الاستجابة
            if hasattr(g, 'start_time'):
                duration = (datetime.utcnow() - g.start_time).total_seconds()
                
                # تسجيل انتهاء الطلب
                performance_logger = logging.getLogger('performance')
                performance_logger.info(
                    f"Request completed: {request.method} {request.url} "
                    f"Status: {response.status_code} Duration: {duration:.3f}s"
                )
                
                # تحذير للطلبات البطيئة
                if duration > 2.0:  # أكثر من ثانيتين
                    self.app.logger.warning(f"Slow request detected: {duration:.3f}s")
            
            return response
        
        @self.app.errorhandler(Exception)
        def handle_exception(e):
            # تسجيل الأخطاء
            error_logger = logging.getLogger('errors')
            error_logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
            
            # إرسال تنبيه للمديرين
            self._send_error_alert(e)
            
            # إرجاع صفحة خطأ مناسبة
            if self.app.debug:
                raise e
            else:
                return "حدث خطأ في النظام. تم إرسال تقرير للمديرين.", 500
    
    def _send_error_alert(self, exception):
        """إرسال تنبيه خطأ للمديرين"""
        try:
            from app.notifications.email_service import send_error_notification
            send_error_notification(exception)
        except Exception as e:
            print(f"Failed to send error alert: {e}")

# دوال مساعدة للسجلات
def log_user_action(action, details=None, level='info'):
    """تسجيل إجراء المستخدم"""
    logger = logging.getLogger('accounting_system')
    
    log_data = {
        'action': action,
        'details': details or {},
        'timestamp': datetime.utcnow().isoformat()
    }
    
    message = f"User action: {action}"
    if details:
        message += f" - {details}"
    
    getattr(logger, level)(message, extra=log_data)

def log_security_event(event_type, details=None, level='warning'):
    """تسجيل حدث أمني"""
    logger = logging.getLogger('security')
    
    log_data = {
        'event_type': event_type,
        'details': details or {},
        'timestamp': datetime.utcnow().isoformat()
    }
    
    message = f"Security event: {event_type}"
    if details:
        message += f" - {details}"
    
    getattr(logger, level)(message, extra=log_data)

def log_performance_metric(metric_name, value, unit='ms'):
    """تسجيل مقياس الأداء"""
    logger = logging.getLogger('performance')
    
    log_data = {
        'metric_name': metric_name,
        'value': value,
        'unit': unit,
        'timestamp': datetime.utcnow().isoformat()
    }
    
    message = f"Performance metric: {metric_name} = {value} {unit}"
    logger.info(message, extra=log_data)

def log_database_operation(operation, table, details=None):
    """تسجيل عملية قاعدة البيانات"""
    logger = logging.getLogger('accounting_system')
    
    log_data = {
        'operation': operation,
        'table': table,
        'details': details or {},
        'timestamp': datetime.utcnow().isoformat()
    }
    
    message = f"Database operation: {operation} on {table}"
    if details:
        message += f" - {details}"
    
    logger.info(message, extra=log_data)

# ديكوريتر لتسجيل الوظائف
def log_function_call(logger_name='accounting_system', level='debug'):
    """ديكوريتر لتسجيل استدعاء الوظائف"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = logging.getLogger(logger_name)
            
            start_time = datetime.utcnow()
            
            # تسجيل بداية الوظيفة
            getattr(logger, level)(f"Function called: {func.__name__}")
            
            try:
                result = func(*args, **kwargs)
                
                # تسجيل نجاح الوظيفة
                duration = (datetime.utcnow() - start_time).total_seconds()
                getattr(logger, level)(f"Function completed: {func.__name__} ({duration:.3f}s)")
                
                return result
                
            except Exception as e:
                # تسجيل فشل الوظيفة
                duration = (datetime.utcnow() - start_time).total_seconds()
                logger.error(f"Function failed: {func.__name__} ({duration:.3f}s) - {str(e)}")
                raise
        
        return wrapper
    return decorator

# إنشاء مثيل مدير السجلات
logger_manager = LoggerManager()
