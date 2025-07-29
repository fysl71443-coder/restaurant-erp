#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نظام التشفير والحماية
Encryption and Protection System
"""

import os
import secrets
import hashlib
import base64
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from werkzeug.security import generate_password_hash, check_password_hash
import jwt

class EncryptionManager:
    """مدير التشفير المتقدم"""
    
    def __init__(self, app=None):
        self.app = app
        self._encryption_key = None
        self._salt = None
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """تهيئة مدير التشفير مع التطبيق"""
        self.app = app
        
        # الحصول على مفتاح التشفير من متغيرات البيئة أو إنشاء واحد جديد
        encryption_key = app.config.get('ENCRYPTION_KEY') or os.environ.get('ENCRYPTION_KEY')
        
        if not encryption_key:
            # إنشاء مفتاح جديد وحفظه
            encryption_key = Fernet.generate_key().decode()
            app.logger.warning(
                f'تم إنشاء مفتاح تشفير جديد: {encryption_key}\n'
                'يرجى حفظ هذا المفتاح في متغيرات البيئة: ENCRYPTION_KEY'
            )
        
        self._encryption_key = encryption_key.encode() if isinstance(encryption_key, str) else encryption_key
        
        # الحصول على الملح
        salt = app.config.get('SECURITY_PASSWORD_SALT') or os.environ.get('SECURITY_PASSWORD_SALT')
        if not salt:
            salt = secrets.token_hex(16)
            app.logger.warning(
                f'تم إنشاء ملح جديد: {salt}\n'
                'يرجى حفظ هذا الملح في متغيرات البيئة: SECURITY_PASSWORD_SALT'
            )
        
        self._salt = salt.encode() if isinstance(salt, str) else salt
    
    def get_fernet(self):
        """الحصول على كائن Fernet للتشفير"""
        return Fernet(self._encryption_key)
    
    def encrypt_data(self, data):
        """تشفير البيانات"""
        if not data:
            return data
        
        if isinstance(data, str):
            data = data.encode()
        
        fernet = self.get_fernet()
        encrypted_data = fernet.encrypt(data)
        return base64.urlsafe_b64encode(encrypted_data).decode()
    
    def decrypt_data(self, encrypted_data):
        """فك تشفير البيانات"""
        if not encrypted_data:
            return encrypted_data
        
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
            fernet = self.get_fernet()
            decrypted_data = fernet.decrypt(encrypted_bytes)
            return decrypted_data.decode()
        except Exception:
            return None
    
    def derive_key(self, password, salt=None):
        """اشتقاق مفتاح من كلمة مرور"""
        if salt is None:
            salt = self._salt
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key
    
    def hash_sensitive_data(self, data):
        """تشفير البيانات الحساسة بـ SHA-256"""
        if not data:
            return data
        
        return hashlib.sha256(data.encode()).hexdigest()

# إنشاء مثيل عام
encryption_manager = EncryptionManager()

def encrypt_sensitive_data(data):
    """تشفير البيانات الحساسة"""
    return encryption_manager.encrypt_data(data)

def decrypt_sensitive_data(encrypted_data):
    """فك تشفير البيانات الحساسة"""
    return encryption_manager.decrypt_data(encrypted_data)

def hash_password(password):
    """تشفير كلمة المرور"""
    return generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)

def verify_password(password, password_hash):
    """التحقق من كلمة المرور"""
    return check_password_hash(password_hash, password)

def generate_secure_token(length=32):
    """إنشاء رمز آمن عشوائي"""
    return secrets.token_urlsafe(length)

def generate_csrf_token():
    """إنشاء رمز CSRF"""
    return secrets.token_hex(16)

def generate_api_key():
    """إنشاء مفتاح API"""
    timestamp = str(int(datetime.now().timestamp()))
    random_part = secrets.token_hex(16)
    return f"ak_{timestamp}_{random_part}"

def generate_session_token():
    """إنشاء رمز جلسة"""
    return secrets.token_urlsafe(64)

class TokenManager:
    """مدير الرموز المميزة"""
    
    def __init__(self, secret_key, algorithm='HS256'):
        self.secret_key = secret_key
        self.algorithm = algorithm
    
    def generate_token(self, payload, expires_in=3600):
        """إنشاء رمز JWT"""
        payload['exp'] = datetime.utcnow() + timedelta(seconds=expires_in)
        payload['iat'] = datetime.utcnow()
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token):
        """التحقق من صحة الرمز"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return {'valid': True, 'payload': payload}
        except jwt.ExpiredSignatureError:
            return {'valid': False, 'error': 'انتهت صلاحية الرمز'}
        except jwt.InvalidTokenError:
            return {'valid': False, 'error': 'رمز غير صحيح'}
    
    def generate_reset_token(self, user_id, expires_in=1800):
        """إنشاء رمز إعادة تعيين كلمة المرور"""
        payload = {
            'user_id': user_id,
            'type': 'password_reset'
        }
        return self.generate_token(payload, expires_in)
    
    def generate_verification_token(self, user_id, email, expires_in=86400):
        """إنشاء رمز تأكيد البريد الإلكتروني"""
        payload = {
            'user_id': user_id,
            'email': email,
            'type': 'email_verification'
        }
        return self.generate_token(payload, expires_in)
    
    def generate_api_token(self, user_id, permissions=None, expires_in=None):
        """إنشاء رمز API"""
        payload = {
            'user_id': user_id,
            'type': 'api_access',
            'permissions': permissions or []
        }
        
        if expires_in:
            return self.generate_token(payload, expires_in)
        else:
            # رمز API بدون انتهاء صلاحية
            payload['exp'] = datetime.utcnow() + timedelta(days=365 * 10)  # 10 سنوات
            return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

class FieldEncryption:
    """تشفير الحقول في قاعدة البيانات"""
    
    @staticmethod
    def encrypt_field(value, field_name=None):
        """تشفير حقل معين"""
        if not value:
            return value
        
        # إضافة معرف الحقل للتشفير
        if field_name:
            value_with_field = f"{field_name}:{value}"
        else:
            value_with_field = value
        
        return encrypt_sensitive_data(value_with_field)
    
    @staticmethod
    def decrypt_field(encrypted_value, field_name=None):
        """فك تشفير حقل معين"""
        if not encrypted_value:
            return encrypted_value
        
        decrypted = decrypt_sensitive_data(encrypted_value)
        if not decrypted:
            return None
        
        # إزالة معرف الحقل إذا كان موجوداً
        if field_name and decrypted.startswith(f"{field_name}:"):
            return decrypted[len(field_name) + 1:]
        
        return decrypted

class SecureStorage:
    """تخزين آمن للبيانات الحساسة"""
    
    def __init__(self):
        self.storage = {}
    
    def store(self, key, value, encrypt=True):
        """تخزين قيمة بشكل آمن"""
        if encrypt:
            value = encrypt_sensitive_data(str(value))
        
        self.storage[key] = {
            'value': value,
            'encrypted': encrypt,
            'timestamp': datetime.now()
        }
    
    def retrieve(self, key):
        """استرجاع قيمة مخزنة"""
        if key not in self.storage:
            return None
        
        item = self.storage[key]
        value = item['value']
        
        if item['encrypted']:
            value = decrypt_sensitive_data(value)
        
        return value
    
    def delete(self, key):
        """حذف قيمة مخزنة"""
        if key in self.storage:
            del self.storage[key]
    
    def cleanup_expired(self, max_age_hours=24):
        """تنظيف البيانات المنتهية الصلاحية"""
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        expired_keys = [
            key for key, item in self.storage.items()
            if item['timestamp'] < cutoff_time
        ]
        
        for key in expired_keys:
            del self.storage[key]
        
        return len(expired_keys)

# إنشاء مثيل للتخزين الآمن
secure_storage = SecureStorage()

def mask_sensitive_data(data, mask_char='*', visible_chars=4):
    """إخفاء البيانات الحساسة للعرض"""
    if not data or len(data) <= visible_chars:
        return mask_char * len(data) if data else ''
    
    visible_start = data[:visible_chars//2] if visible_chars > 2 else ''
    visible_end = data[-(visible_chars//2):] if visible_chars > 2 else data[-1:]
    masked_middle = mask_char * (len(data) - visible_chars)
    
    return visible_start + masked_middle + visible_end

def generate_checksum(data):
    """إنشاء checksum للبيانات"""
    if isinstance(data, str):
        data = data.encode()
    
    return hashlib.md5(data).hexdigest()

def verify_checksum(data, expected_checksum):
    """التحقق من checksum"""
    actual_checksum = generate_checksum(data)
    return actual_checksum == expected_checksum

def secure_compare(a, b):
    """مقارنة آمنة للنصوص لمنع timing attacks"""
    return secrets.compare_digest(str(a), str(b))

def generate_backup_encryption_key():
    """إنشاء مفتاح تشفير للنسخ الاحتياطية"""
    return Fernet.generate_key()

def encrypt_backup_data(data, key):
    """تشفير بيانات النسخة الاحتياطية"""
    fernet = Fernet(key)
    
    if isinstance(data, str):
        data = data.encode()
    
    return fernet.encrypt(data)

def decrypt_backup_data(encrypted_data, key):
    """فك تشفير بيانات النسخة الاحتياطية"""
    fernet = Fernet(key)
    return fernet.decrypt(encrypted_data)
