#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
أدوات المصادقة المساعدة
Authentication Utilities
"""

import re
from urllib.parse import urlparse, urljoin
from flask import request, current_app
from app import db
from app.models.roles_permissions import LoginHistory

def get_client_ip():
    """الحصول على عنوان IP الحقيقي للعميل"""
    # فحص الرؤوس المختلفة للحصول على IP الحقيقي
    if request.environ.get('HTTP_X_FORWARDED_FOR'):
        # في حالة وجود proxy
        ip = request.environ['HTTP_X_FORWARDED_FOR'].split(',')[0].strip()
    elif request.environ.get('HTTP_X_REAL_IP'):
        # في حالة nginx
        ip = request.environ['HTTP_X_REAL_IP']
    elif request.environ.get('HTTP_X_FORWARDED'):
        ip = request.environ['HTTP_X_FORWARDED']
    elif request.environ.get('HTTP_X_CLUSTER_CLIENT_IP'):
        ip = request.environ['HTTP_X_CLUSTER_CLIENT_IP']
    else:
        # العنوان المباشر
        ip = request.environ.get('REMOTE_ADDR', '127.0.0.1')
    
    return ip

def is_safe_url(target):
    """فحص إذا كان الرابط آمن للإعادة التوجيه"""
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc

def get_user_agent_info():
    """الحصول على معلومات متصفح المستخدم"""
    user_agent = request.headers.get('User-Agent', '')
    
    # تحديد نوع الجهاز
    device_type = 'desktop'
    if re.search(r'Mobile|Android|iPhone|iPad', user_agent, re.I):
        device_type = 'mobile'
    elif re.search(r'Tablet|iPad', user_agent, re.I):
        device_type = 'tablet'
    
    # تحديد المتصفح
    browser = 'unknown'
    if 'Chrome' in user_agent:
        browser = 'Chrome'
    elif 'Firefox' in user_agent:
        browser = 'Firefox'
    elif 'Safari' in user_agent:
        browser = 'Safari'
    elif 'Edge' in user_agent:
        browser = 'Edge'
    elif 'Opera' in user_agent:
        browser = 'Opera'
    
    # تحديد نظام التشغيل
    os = 'unknown'
    if 'Windows' in user_agent:
        os = 'Windows'
    elif 'Mac OS' in user_agent:
        os = 'macOS'
    elif 'Linux' in user_agent:
        os = 'Linux'
    elif 'Android' in user_agent:
        os = 'Android'
    elif 'iOS' in user_agent:
        os = 'iOS'
    
    return {
        'device_type': device_type,
        'browser': browser,
        'os': os,
        'user_agent': user_agent
    }

def create_login_history(user, ip_address, success=True, failure_reason=None):
    """إنشاء سجل تسجيل دخول"""
    user_agent_info = get_user_agent_info()
    
    # الحصول على الموقع الجغرافي (يمكن تطبيقه لاحقاً)
    location = get_location_from_ip(ip_address)
    
    login_record = LoginHistory(
        user_id=user.id if user else None,
        ip_address=ip_address,
        user_agent=user_agent_info['user_agent'],
        success=success,
        failure_reason=failure_reason,
        device_type=user_agent_info['device_type'],
        location=location
    )
    
    if user and success:
        login_record.session_id = user.current_session_id
    
    db.session.add(login_record)
    db.session.commit()
    
    return login_record

def update_logout_time(user):
    """تحديث وقت تسجيل الخروج"""
    if user.current_session_id:
        login_record = LoginHistory.query.filter_by(
            user_id=user.id,
            session_id=user.current_session_id,
            success=True
        ).order_by(LoginHistory.login_at.desc()).first()
        
        if login_record:
            from datetime import datetime
            login_record.logout_at = datetime.utcnow()
            db.session.commit()

def get_location_from_ip(ip_address):
    """الحصول على الموقع الجغرافي من عنوان IP"""
    # يمكن استخدام خدمات مثل GeoIP أو MaxMind
    # هنا نعيد قيمة افتراضية
    
    # فحص إذا كان IP محلي
    if ip_address in ['127.0.0.1', 'localhost', '::1']:
        return 'محلي'
    
    # يمكن تطبيق خدمة GeoIP هنا
    try:
        # مثال باستخدام مكتبة geoip2 (يحتاج تثبيت)
        # import geoip2.database
        # reader = geoip2.database.Reader('GeoLite2-City.mmdb')
        # response = reader.city(ip_address)
        # return f"{response.city.name}, {response.country.name}"
        pass
    except:
        pass
    
    return 'غير معروف'

def check_password_policy(password):
    """فحص سياسة كلمة المرور"""
    policy = {
        'min_length': current_app.config.get('PASSWORD_MIN_LENGTH', 8),
        'require_uppercase': current_app.config.get('PASSWORD_REQUIRE_UPPERCASE', True),
        'require_lowercase': current_app.config.get('PASSWORD_REQUIRE_LOWERCASE', True),
        'require_numbers': current_app.config.get('PASSWORD_REQUIRE_NUMBERS', True),
        'require_symbols': current_app.config.get('PASSWORD_REQUIRE_SYMBOLS', True),
    }
    
    errors = []
    
    if len(password) < policy['min_length']:
        errors.append(f'كلمة المرور يجب أن تكون {policy["min_length"]} أحرف على الأقل')
    
    if policy['require_uppercase'] and not re.search(r'[A-Z]', password):
        errors.append('كلمة المرور يجب أن تحتوي على حرف كبير واحد على الأقل')
    
    if policy['require_lowercase'] and not re.search(r'[a-z]', password):
        errors.append('كلمة المرور يجب أن تحتوي على حرف صغير واحد على الأقل')
    
    if policy['require_numbers'] and not re.search(r'\d', password):
        errors.append('كلمة المرور يجب أن تحتوي على رقم واحد على الأقل')
    
    if policy['require_symbols'] and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        errors.append('كلمة المرور يجب أن تحتوي على رمز خاص واحد على الأقل')
    
    return {
        'is_valid': len(errors) == 0,
        'errors': errors
    }

def generate_secure_filename(filename):
    """إنشاء اسم ملف آمن"""
    import os
    import secrets
    
    # الحصول على امتداد الملف
    name, ext = os.path.splitext(filename)
    
    # تنظيف اسم الملف
    safe_name = re.sub(r'[^a-zA-Z0-9_-]', '', name)
    
    # إضافة رمز عشوائي
    random_suffix = secrets.token_hex(8)
    
    return f"{safe_name}_{random_suffix}{ext}"

def validate_file_upload(file, allowed_extensions=None, max_size=None):
    """التحقق من صحة الملف المرفوع"""
    if not file or not file.filename:
        return {'is_valid': False, 'error': 'لم يتم اختيار ملف'}
    
    # فحص الامتداد
    if allowed_extensions:
        file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
        if file_ext not in allowed_extensions:
            return {
                'is_valid': False,
                'error': f'امتداد الملف غير مدعوم. الامتدادات المسموحة: {", ".join(allowed_extensions)}'
            }
    
    # فحص الحجم
    if max_size:
        file.seek(0, 2)  # الانتقال لنهاية الملف
        file_size = file.tell()
        file.seek(0)  # العودة للبداية
        
        if file_size > max_size:
            return {
                'is_valid': False,
                'error': f'حجم الملف كبير جداً. الحد الأقصى: {max_size / 1024 / 1024:.1f} ميجابايت'
            }
    
    return {'is_valid': True}

def send_verification_email(user, token):
    """إرسال بريد تأكيد البريد الإلكتروني"""
    # سيتم تطبيق هذه الوظيفة لاحقاً مع نظام البريد الإلكتروني
    pass

def send_reset_email(user, token):
    """إرسال بريد إعادة تعيين كلمة المرور"""
    # سيتم تطبيق هذه الوظيفة لاحقاً مع نظام البريد الإلكتروني
    pass

def send_security_alert(user, event_type, details=None):
    """إرسال تنبيه أمني"""
    # سيتم تطبيق هذه الوظيفة لاحقاً مع نظام الإشعارات
    pass

def check_suspicious_activity(user, ip_address):
    """فحص النشاط المشبوه"""
    from datetime import datetime, timedelta
    
    # فحص محاولات الدخول من IPs مختلفة
    recent_logins = LoginHistory.query.filter(
        LoginHistory.user_id == user.id,
        LoginHistory.login_at > datetime.utcnow() - timedelta(hours=1),
        LoginHistory.success == True
    ).all()
    
    different_ips = set(login.ip_address for login in recent_logins)
    
    if len(different_ips) > 3:  # أكثر من 3 IPs مختلفة في ساعة واحدة
        return {
            'is_suspicious': True,
            'reason': 'multiple_ips',
            'details': f'تسجيل دخول من {len(different_ips)} عناوين IP مختلفة'
        }
    
    # فحص محاولات الدخول الفاشلة
    failed_attempts = LoginHistory.query.filter(
        LoginHistory.user_id == user.id,
        LoginHistory.login_at > datetime.utcnow() - timedelta(minutes=30),
        LoginHistory.success == False
    ).count()
    
    if failed_attempts > 5:  # أكثر من 5 محاولات فاشلة في 30 دقيقة
        return {
            'is_suspicious': True,
            'reason': 'multiple_failures',
            'details': f'{failed_attempts} محاولة دخول فاشلة'
        }
    
    return {'is_suspicious': False}

def cleanup_expired_tokens():
    """تنظيف الرموز المنتهية الصلاحية"""
    from datetime import datetime
    from app.models.user_enhanced import User
    
    # تنظيف رموز إعادة التعيين المنتهية الصلاحية
    expired_users = User.query.filter(
        User.reset_token_expires < datetime.utcnow()
    ).all()
    
    for user in expired_users:
        user.reset_token = None
        user.reset_token_expires = None
    
    db.session.commit()
    
    return len(expired_users)

def get_user_permissions_tree(user):
    """الحصول على شجرة صلاحيات المستخدم"""
    permissions = user.get_permissions()
    
    # تجميع الصلاحيات حسب الفئة
    permissions_tree = {}
    
    for permission in permissions:
        category = permission.category
        if category not in permissions_tree:
            permissions_tree[category] = {
                'name': permission.get_category_display(),
                'permissions': []
            }
        
        permissions_tree[category]['permissions'].append({
            'name': permission.name,
            'display_name': permission.display_name,
            'description': permission.description
        })
    
    return permissions_tree

def check_user_session_validity(user, session_id):
    """فحص صحة جلسة المستخدم"""
    if not user.is_session_valid(session_id):
        return False
    
    # فحص إضافي للنشاط المشبوه
    suspicious = check_suspicious_activity(user, get_client_ip())
    if suspicious['is_suspicious']:
        # إرسال تنبيه أمني
        send_security_alert(user, 'suspicious_activity', suspicious)
        return False
    
    return True

def log_security_event(event_type, user=None, details=None):
    """تسجيل حدث أمني"""
    from app.models.audit_log import AuditLog
    
    AuditLog.log_security_event(
        event_type=event_type,
        user_id=user.id if user else None,
        ip_address=get_client_ip(),
        user_agent=get_user_agent_info()['user_agent'],
        details=details or {}
    )

def rate_limit_key(endpoint, user_id=None):
    """إنشاء مفتاح تحديد معدل الطلبات"""
    if user_id:
        return f"rate_limit:{user_id}:{endpoint}"
    else:
        return f"rate_limit:{get_client_ip()}:{endpoint}"

def check_rate_limit(key, max_requests, window):
    """فحص تحديد معدل الطلبات"""
    from app import cache
    
    current_requests = cache.get(key) or 0
    
    if current_requests >= max_requests:
        return False
    
    # زيادة العداد
    cache.set(key, current_requests + 1, timeout=window)
    return True
