#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
مدققات الأمان والتحقق من صحة البيانات
Security Validators and Data Validation
"""

import re
import html
import bleach
from urllib.parse import urlparse
from app.models.audit_log import AuditLog

def validate_password_strength(password):
    """التحقق من قوة كلمة المرور"""
    errors = []
    
    if len(password) < 8:
        errors.append('كلمة المرور يجب أن تكون 8 أحرف على الأقل')
    
    if len(password) > 128:
        errors.append('كلمة المرور طويلة جداً (الحد الأقصى 128 حرف)')
    
    if not re.search(r'[A-Z]', password):
        errors.append('كلمة المرور يجب أن تحتوي على حرف كبير واحد على الأقل')
    
    if not re.search(r'[a-z]', password):
        errors.append('كلمة المرور يجب أن تحتوي على حرف صغير واحد على الأقل')
    
    if not re.search(r'\d', password):
        errors.append('كلمة المرور يجب أن تحتوي على رقم واحد على الأقل')
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        errors.append('كلمة المرور يجب أن تحتوي على رمز خاص واحد على الأقل')
    
    # فحص الكلمات الشائعة
    common_passwords = [
        'password', '123456', '123456789', 'qwerty', 'abc123',
        'password123', 'admin', 'letmein', 'welcome', 'monkey'
    ]
    
    if password.lower() in common_passwords:
        errors.append('كلمة المرور شائعة جداً، يرجى اختيار كلمة مرور أقوى')
    
    # فحص التكرار
    if len(set(password)) < len(password) * 0.6:
        errors.append('كلمة المرور تحتوي على تكرار كثير للأحرف')
    
    return {
        'is_valid': len(errors) == 0,
        'errors': errors,
        'strength_score': calculate_password_strength_score(password)
    }

def calculate_password_strength_score(password):
    """حساب نقاط قوة كلمة المرور"""
    score = 0
    
    # الطول
    if len(password) >= 8:
        score += 1
    if len(password) >= 12:
        score += 1
    if len(password) >= 16:
        score += 1
    
    # التنوع
    if re.search(r'[A-Z]', password):
        score += 1
    if re.search(r'[a-z]', password):
        score += 1
    if re.search(r'\d', password):
        score += 1
    if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        score += 1
    
    # التعقيد
    if len(set(password)) > len(password) * 0.7:
        score += 1
    
    return min(score, 8)  # الحد الأقصى 8 نقاط

def validate_email_format(email):
    """التحقق من صحة تنسيق البريد الإلكتروني"""
    if not email:
        return {'is_valid': False, 'error': 'البريد الإلكتروني مطلوب'}
    
    # تنظيف البريد الإلكتروني
    email = email.strip().lower()
    
    # التحقق من التنسيق الأساسي
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        return {'is_valid': False, 'error': 'تنسيق البريد الإلكتروني غير صحيح'}
    
    # التحقق من الطول
    if len(email) > 254:
        return {'is_valid': False, 'error': 'البريد الإلكتروني طويل جداً'}
    
    # التحقق من النطاق
    domain = email.split('@')[1]
    if len(domain) > 253:
        return {'is_valid': False, 'error': 'نطاق البريد الإلكتروني طويل جداً'}
    
    # فحص النطاقات المحظورة
    blocked_domains = [
        'tempmail.org', '10minutemail.com', 'guerrillamail.com',
        'mailinator.com', 'throwaway.email'
    ]
    
    if domain in blocked_domains:
        return {'is_valid': False, 'error': 'هذا النطاق غير مسموح'}
    
    return {'is_valid': True, 'email': email}

def validate_phone_number(phone, country_code='SA'):
    """التحقق من صحة رقم الهاتف"""
    if not phone:
        return {'is_valid': False, 'error': 'رقم الهاتف مطلوب'}
    
    # إزالة المسافات والرموز
    phone = re.sub(r'[^\d+]', '', phone)
    
    # أنماط الهواتف للسعودية
    if country_code == 'SA':
        # رقم سعودي: +966xxxxxxxxx أو 05xxxxxxxx
        patterns = [
            r'^\+9665\d{8}$',  # +966 5xxxxxxxx
            r'^9665\d{8}$',    # 966 5xxxxxxxx
            r'^05\d{8}$',      # 05xxxxxxxx
            r'^5\d{8}$'        # 5xxxxxxxx
        ]
        
        for pattern in patterns:
            if re.match(pattern, phone):
                # تنسيق موحد
                if phone.startswith('+966'):
                    formatted = phone
                elif phone.startswith('966'):
                    formatted = '+' + phone
                elif phone.startswith('05'):
                    formatted = '+966' + phone[1:]
                elif phone.startswith('5'):
                    formatted = '+966' + phone
                else:
                    formatted = phone
                
                return {'is_valid': True, 'phone': formatted}
    
    return {'is_valid': False, 'error': 'تنسيق رقم الهاتف غير صحيح'}

def sanitize_input(input_text, allow_html=False):
    """تنظيف المدخلات من المحتوى الضار"""
    if not input_text:
        return input_text
    
    # تحويل إلى نص
    if not isinstance(input_text, str):
        input_text = str(input_text)
    
    # إزالة المسافات الزائدة
    input_text = input_text.strip()
    
    if allow_html:
        # السماح ببعض علامات HTML الآمنة
        allowed_tags = ['b', 'i', 'u', 'em', 'strong', 'p', 'br', 'ul', 'ol', 'li']
        allowed_attributes = {}
        
        input_text = bleach.clean(
            input_text,
            tags=allowed_tags,
            attributes=allowed_attributes,
            strip=True
        )
    else:
        # إزالة جميع علامات HTML
        input_text = bleach.clean(input_text, tags=[], strip=True)
    
    # تشفير الأحرف الخاصة
    input_text = html.escape(input_text)
    
    return input_text

def check_sql_injection(input_text):
    """فحص محاولات حقن SQL"""
    if not input_text:
        return {'is_safe': True}
    
    # أنماط حقن SQL الشائعة
    sql_patterns = [
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION)\b)",
        r"(\b(OR|AND)\s+\d+\s*=\s*\d+)",
        r"(\b(OR|AND)\s+['\"]?\w+['\"]?\s*=\s*['\"]?\w+['\"]?)",
        r"(--|#|/\*|\*/)",
        r"(\bUNION\s+SELECT\b)",
        r"(\bINTO\s+OUTFILE\b)",
        r"(\bLOAD_FILE\b)",
        r"(\bCHAR\s*\(\s*\d+)",
        r"(\bCONCAT\s*\()",
        r"(\bSUBSTRING\s*\()",
        r"(\bASCII\s*\()",
        r"(\bBENCHMARK\s*\()",
        r"(\bSLEEP\s*\()",
        r"(\bWAITFOR\s+DELAY\b)"
    ]
    
    input_upper = input_text.upper()
    
    for pattern in sql_patterns:
        if re.search(pattern, input_upper, re.IGNORECASE):
            # تسجيل محاولة حقن SQL
            AuditLog.log_security_event(
                'sql_injection_attempt',
                details={
                    'input_text': input_text[:100],  # أول 100 حرف فقط
                    'pattern_matched': pattern
                },
                severity='critical'
            )
            
            return {
                'is_safe': False,
                'threat_type': 'sql_injection',
                'pattern': pattern
            }
    
    return {'is_safe': True}

def check_xss_attempt(input_text):
    """فحص محاولات XSS"""
    if not input_text:
        return {'is_safe': True}
    
    # أنماط XSS الشائعة
    xss_patterns = [
        r"<script[^>]*>.*?</script>",
        r"javascript:",
        r"vbscript:",
        r"onload\s*=",
        r"onerror\s*=",
        r"onclick\s*=",
        r"onmouseover\s*=",
        r"onfocus\s*=",
        r"onblur\s*=",
        r"onchange\s*=",
        r"onsubmit\s*=",
        r"<iframe[^>]*>",
        r"<object[^>]*>",
        r"<embed[^>]*>",
        r"<link[^>]*>",
        r"<meta[^>]*>",
        r"<style[^>]*>.*?</style>",
        r"expression\s*\(",
        r"url\s*\(",
        r"@import",
        r"<img[^>]*src\s*=\s*['\"]?javascript:",
        r"<svg[^>]*onload\s*="
    ]
    
    input_lower = input_text.lower()
    
    for pattern in xss_patterns:
        if re.search(pattern, input_lower, re.IGNORECASE | re.DOTALL):
            # تسجيل محاولة XSS
            AuditLog.log_security_event(
                'xss_attempt',
                details={
                    'input_text': input_text[:100],  # أول 100 حرف فقط
                    'pattern_matched': pattern
                },
                severity='critical'
            )
            
            return {
                'is_safe': False,
                'threat_type': 'xss',
                'pattern': pattern
            }
    
    return {'is_safe': True}

def validate_url(url):
    """التحقق من صحة وأمان الرابط"""
    if not url:
        return {'is_valid': False, 'error': 'الرابط مطلوب'}
    
    try:
        parsed = urlparse(url)
        
        # التحقق من البروتوكول
        if parsed.scheme not in ['http', 'https']:
            return {'is_valid': False, 'error': 'البروتوكول غير مدعوم'}
        
        # التحقق من وجود النطاق
        if not parsed.netloc:
            return {'is_valid': False, 'error': 'النطاق مطلوب'}
        
        # فحص النطاقات المحظورة
        blocked_domains = [
            'localhost', '127.0.0.1', '0.0.0.0', '::1',
            'malware.com', 'phishing.com'
        ]
        
        if parsed.netloc.lower() in blocked_domains:
            return {'is_valid': False, 'error': 'هذا النطاق محظور'}
        
        # فحص الشبكات الداخلية
        import ipaddress
        try:
            ip = ipaddress.ip_address(parsed.netloc)
            if ip.is_private or ip.is_loopback:
                return {'is_valid': False, 'error': 'الوصول للشبكات الداخلية غير مسموح'}
        except:
            pass  # ليس عنوان IP
        
        return {'is_valid': True, 'url': url}
        
    except Exception as e:
        return {'is_valid': False, 'error': 'تنسيق الرابط غير صحيح'}

def validate_file_upload(file, allowed_extensions=None, max_size=None):
    """التحقق من صحة وأمان الملف المرفوع"""
    if not file:
        return {'is_valid': False, 'error': 'الملف مطلوب'}
    
    if not file.filename:
        return {'is_valid': False, 'error': 'اسم الملف مطلوب'}
    
    # التحقق من الامتداد
    if allowed_extensions:
        file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
        if file_ext not in allowed_extensions:
            return {
                'is_valid': False,
                'error': f'امتداد الملف غير مدعوم. الامتدادات المسموحة: {", ".join(allowed_extensions)}'
            }
    
    # التحقق من الحجم
    if max_size:
        file.seek(0, 2)  # الانتقال لنهاية الملف
        file_size = file.tell()
        file.seek(0)  # العودة للبداية
        
        if file_size > max_size:
            return {
                'is_valid': False,
                'error': f'حجم الملف كبير جداً. الحد الأقصى: {max_size / 1024 / 1024:.1f} ميجابايت'
            }
    
    # فحص محتوى الملف للتأكد من عدم وجود محتوى ضار
    dangerous_signatures = [
        b'<?php',
        b'<script',
        b'javascript:',
        b'vbscript:',
        b'\x4d\x5a',  # PE executable
        b'\x7f\x45\x4c\x46',  # ELF executable
    ]
    
    file_content = file.read(1024)  # قراءة أول 1KB
    file.seek(0)  # العودة للبداية
    
    for signature in dangerous_signatures:
        if signature in file_content.lower():
            AuditLog.log_security_event(
                'malicious_file_upload_attempt',
                details={
                    'filename': file.filename,
                    'signature_found': signature.decode('utf-8', errors='ignore')
                },
                severity='critical'
            )
            
            return {
                'is_valid': False,
                'error': 'الملف يحتوي على محتوى ضار'
            }
    
    return {'is_valid': True}

def validate_json_input(json_data, required_fields=None, max_depth=10):
    """التحقق من صحة مدخلات JSON"""
    if not json_data:
        return {'is_valid': False, 'error': 'البيانات مطلوبة'}
    
    # فحص العمق لمنع JSON bomb
    def check_depth(obj, current_depth=0):
        if current_depth > max_depth:
            return False
        
        if isinstance(obj, dict):
            return all(check_depth(v, current_depth + 1) for v in obj.values())
        elif isinstance(obj, list):
            return all(check_depth(item, current_depth + 1) for item in obj)
        
        return True
    
    if not check_depth(json_data):
        return {'is_valid': False, 'error': 'البيانات معقدة جداً'}
    
    # فحص الحقول المطلوبة
    if required_fields:
        missing_fields = []
        for field in required_fields:
            if field not in json_data:
                missing_fields.append(field)
        
        if missing_fields:
            return {
                'is_valid': False,
                'error': f'الحقول المطلوبة مفقودة: {", ".join(missing_fields)}'
            }
    
    return {'is_valid': True}
