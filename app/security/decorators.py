#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
مزخرفات الأمان
Security Decorators
"""

import functools
import time
from datetime import datetime, timedelta
from flask import request, jsonify, abort, session, current_app, g
from flask_login import current_user
from app.models.audit_log import AuditLog

def permission_required(permission):
    """مزخرف للتحقق من الصلاحيات"""
    def decorator(f):
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                if request.is_json:
                    return jsonify({'error': 'يجب تسجيل الدخول أولاً'}), 401
                abort(401)
            
            if not current_user.has_permission(permission):
                # تسجيل محاولة الوصول غير المصرح بها
                AuditLog.log_security_event(
                    'unauthorized_access_attempt',
                    details={
                        'user_id': current_user.id,
                        'permission': permission,
                        'endpoint': request.endpoint,
                        'method': request.method
                    },
                    severity='warning'
                )
                
                if request.is_json:
                    return jsonify({'error': 'ليس لديك صلاحية للوصول إلى هذا المورد'}), 403
                abort(403)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def role_required(roles):
    """مزخرف للتحقق من الأدوار"""
    if isinstance(roles, str):
        roles = [roles]
    
    def decorator(f):
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                if request.is_json:
                    return jsonify({'error': 'يجب تسجيل الدخول أولاً'}), 401
                abort(401)
            
            if not current_user.has_role(roles):
                # تسجيل محاولة الوصول غير المصرح بها
                AuditLog.log_security_event(
                    'unauthorized_role_access',
                    details={
                        'user_id': current_user.id,
                        'user_role': current_user.role,
                        'required_roles': roles,
                        'endpoint': request.endpoint
                    },
                    severity='warning'
                )
                
                if request.is_json:
                    return jsonify({'error': 'ليس لديك الدور المطلوب للوصول إلى هذا المورد'}), 403
                abort(403)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def rate_limit(max_requests=100, window=3600, per_user=True):
    """مزخرف لتحديد معدل الطلبات"""
    def decorator(f):
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            from app import cache
            
            # تحديد المفتاح للتخزين المؤقت
            if per_user and current_user.is_authenticated:
                key = f"rate_limit:{current_user.id}:{request.endpoint}"
            else:
                key = f"rate_limit:{request.remote_addr}:{request.endpoint}"
            
            # الحصول على عدد الطلبات الحالي
            current_requests = cache.get(key) or 0
            
            if current_requests >= max_requests:
                # تسجيل تجاوز الحد المسموح
                AuditLog.log_security_event(
                    'rate_limit_exceeded',
                    details={
                        'key': key,
                        'max_requests': max_requests,
                        'window': window,
                        'endpoint': request.endpoint
                    },
                    severity='warning'
                )
                
                if request.is_json:
                    return jsonify({
                        'error': 'تم تجاوز الحد المسموح من الطلبات',
                        'retry_after': window
                    }), 429
                abort(429)
            
            # زيادة عداد الطلبات
            cache.set(key, current_requests + 1, timeout=window)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def audit_log(action=None, table_name=None, category=None):
    """مزخرف لتسجيل الأحداث في سجل المراجعة"""
    def decorator(f):
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            start_time = time.time()
            
            # تنفيذ الدالة
            try:
                result = f(*args, **kwargs)
                
                # تسجيل الحدث الناجح
                execution_time = time.time() - start_time
                
                AuditLog.log_action(
                    table_name=table_name or 'system',
                    record_id=kwargs.get('id'),
                    action=action or f.__name__,
                    details={
                        'endpoint': request.endpoint,
                        'method': request.method,
                        'execution_time': execution_time,
                        'args': str(args) if args else None,
                        'kwargs': {k: v for k, v in kwargs.items() if k != 'password'}
                    },
                    category=category or 'data_access'
                )
                
                return result
                
            except Exception as e:
                # تسجيل الحدث الفاشل
                execution_time = time.time() - start_time
                
                AuditLog.log_action(
                    table_name=table_name or 'system',
                    record_id=kwargs.get('id'),
                    action=f"{action or f.__name__}_failed",
                    details={
                        'endpoint': request.endpoint,
                        'method': request.method,
                        'execution_time': execution_time,
                        'error': str(e),
                        'args': str(args) if args else None,
                        'kwargs': {k: v for k, v in kwargs.items() if k != 'password'}
                    },
                    severity='error',
                    category=category or 'data_access'
                )
                
                raise
                
        return decorated_function
    return decorator

def csrf_protect(f):
    """مزخرف للحماية من CSRF"""
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method in ['POST', 'PUT', 'DELETE', 'PATCH']:
            # التحقق من رمز CSRF
            token = request.form.get('csrf_token') or request.headers.get('X-CSRFToken')
            
            if not token:
                AuditLog.log_security_event(
                    'csrf_token_missing',
                    details={'endpoint': request.endpoint},
                    severity='warning'
                )
                
                if request.is_json:
                    return jsonify({'error': 'رمز CSRF مفقود'}), 400
                abort(400)
            
            # التحقق من صحة الرمز
            from flask_wtf.csrf import validate_csrf
            try:
                validate_csrf(token)
            except:
                AuditLog.log_security_event(
                    'csrf_token_invalid',
                    details={'endpoint': request.endpoint},
                    severity='warning'
                )
                
                if request.is_json:
                    return jsonify({'error': 'رمز CSRF غير صحيح'}), 400
                abort(400)
        
        return f(*args, **kwargs)
    return decorated_function

def secure_headers(f):
    """مزخرف لإضافة رؤوس الأمان"""
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        response = f(*args, **kwargs)
        
        # إضافة رؤوس الأمان
        if hasattr(response, 'headers'):
            response.headers['X-Content-Type-Options'] = 'nosniff'
            response.headers['X-Frame-Options'] = 'DENY'
            response.headers['X-XSS-Protection'] = '1; mode=block'
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
            
            # Content Security Policy
            csp = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net; "
                "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
                "font-src 'self' https://cdn.jsdelivr.net; "
                "img-src 'self' data: https:; "
                "connect-src 'self';"
            )
            response.headers['Content-Security-Policy'] = csp
        
        return response
    return decorated_function

def ip_whitelist(allowed_ips):
    """مزخرف لتقييد الوصول بناءً على IP"""
    if isinstance(allowed_ips, str):
        allowed_ips = [allowed_ips]
    
    def decorator(f):
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            client_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
            
            if client_ip not in allowed_ips:
                AuditLog.log_security_event(
                    'ip_access_denied',
                    details={
                        'client_ip': client_ip,
                        'allowed_ips': allowed_ips,
                        'endpoint': request.endpoint
                    },
                    severity='warning'
                )
                
                if request.is_json:
                    return jsonify({'error': 'الوصول مرفوض من هذا العنوان'}), 403
                abort(403)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def time_based_access(start_hour=8, end_hour=18):
    """مزخرف لتقييد الوصول بناءً على الوقت"""
    def decorator(f):
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            current_hour = datetime.now().hour
            
            if not (start_hour <= current_hour <= end_hour):
                AuditLog.log_security_event(
                    'time_based_access_denied',
                    details={
                        'current_hour': current_hour,
                        'allowed_hours': f"{start_hour}-{end_hour}",
                        'endpoint': request.endpoint
                    },
                    severity='info'
                )
                
                if request.is_json:
                    return jsonify({
                        'error': f'الوصول مسموح فقط من الساعة {start_hour} إلى {end_hour}'
                    }), 403
                abort(403)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def require_two_factor(f):
    """مزخرف لطلب المصادقة الثنائية"""
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            if request.is_json:
                return jsonify({'error': 'يجب تسجيل الدخول أولاً'}), 401
            abort(401)
        
        # فحص إذا كانت المصادقة الثنائية مطلوبة ومفعلة
        if current_user.two_factor_enabled:
            # فحص إذا تم التحقق من المصادقة الثنائية في هذه الجلسة
            if not session.get('two_factor_verified'):
                if request.is_json:
                    return jsonify({
                        'error': 'المصادقة الثنائية مطلوبة',
                        'redirect': '/auth/two-factor'
                    }), 403
                
                from flask import redirect, url_for
                return redirect(url_for('auth.two_factor'))
        
        return f(*args, **kwargs)
    return decorated_function

def monitor_sensitive_operations(operation_type):
    """مزخرف لمراقبة العمليات الحساسة"""
    def decorator(f):
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            # تسجيل بداية العملية الحساسة
            AuditLog.log_security_event(
                f'sensitive_operation_start',
                details={
                    'operation_type': operation_type,
                    'endpoint': request.endpoint,
                    'user_id': current_user.id if current_user.is_authenticated else None
                },
                severity='info'
            )
            
            try:
                result = f(*args, **kwargs)
                
                # تسجيل نجاح العملية
                AuditLog.log_security_event(
                    f'sensitive_operation_success',
                    details={
                        'operation_type': operation_type,
                        'endpoint': request.endpoint
                    },
                    severity='info'
                )
                
                return result
                
            except Exception as e:
                # تسجيل فشل العملية
                AuditLog.log_security_event(
                    f'sensitive_operation_failed',
                    details={
                        'operation_type': operation_type,
                        'endpoint': request.endpoint,
                        'error': str(e)
                    },
                    severity='error'
                )
                raise
                
        return decorated_function
    return decorator
