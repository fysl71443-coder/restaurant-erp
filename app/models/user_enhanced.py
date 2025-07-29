#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نموذج المستخدم المحسن مع نظام مصادقة متقدم
Enhanced User Model with Advanced Authentication System
"""

import secrets
import pyotp
import qrcode
from io import BytesIO
import base64
from datetime import datetime, timedelta
from flask import current_app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Index, event, func
from sqlalchemy.ext.hybrid import hybrid_property
from app import db
from app.models.base import BaseModel, AuditMixin, EncryptedMixin

class User(UserMixin, BaseModel, AuditMixin, EncryptedMixin):
    """نموذج المستخدم مع نظام مصادقة متقدم"""
    
    __tablename__ = 'users'
    
    # المعلومات الأساسية
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    _password_hash = db.Column('password_hash', db.String(255), nullable=False)
    
    # المعلومات الشخصية
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20), nullable=True, index=True)
    avatar_url = db.Column(db.String(255), nullable=True)
    
    # حالة الحساب
    is_active = db.Column(db.Boolean, default=True, nullable=False, index=True)
    is_verified = db.Column(db.Boolean, default=False, nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    
    # معلومات تسجيل الدخول
    last_login_at = db.Column(db.DateTime, nullable=True)
    last_login_ip = db.Column(db.String(45), nullable=True)  # IPv6 support
    login_count = db.Column(db.Integer, default=0, nullable=False)
    failed_login_attempts = db.Column(db.Integer, default=0, nullable=False)
    locked_until = db.Column(db.DateTime, nullable=True)
    
    # المصادقة الثنائية (2FA)
    two_factor_enabled = db.Column(db.Boolean, default=False, nullable=False)
    _two_factor_secret = db.Column('two_factor_secret', db.Text, nullable=True)  # مشفر
    backup_codes = db.Column(db.JSON, nullable=True)  # رموز احتياطية
    
    # إعادة تعيين كلمة المرور
    reset_token = db.Column(db.String(100), nullable=True, index=True)
    reset_token_expires = db.Column(db.DateTime, nullable=True)
    
    # تأكيد البريد الإلكتروني
    email_verification_token = db.Column(db.String(100), nullable=True)
    email_verified_at = db.Column(db.DateTime, nullable=True)
    
    # إعدادات المستخدم
    preferred_language = db.Column(db.String(5), default='ar', nullable=False)
    timezone = db.Column(db.String(50), default='Asia/Riyadh', nullable=False)
    theme = db.Column(db.String(20), default='light', nullable=False)
    
    # معلومات الجلسة
    current_session_id = db.Column(db.String(100), nullable=True)
    session_expires_at = db.Column(db.DateTime, nullable=True)
    
    # العلاقات
    roles = db.relationship('UserRole', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    login_history = db.relationship('LoginHistory', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    # فهارس محسنة
    __table_args__ = (
        Index('idx_user_username_email', 'username', 'email'),
        Index('idx_user_active_verified', 'is_active', 'is_verified'),
        Index('idx_user_login_info', 'last_login_at', 'login_count'),
        Index('idx_user_security', 'failed_login_attempts', 'locked_until'),
        Index('idx_user_tokens', 'reset_token', 'email_verification_token'),
        Index('idx_user_session', 'current_session_id', 'session_expires_at'),
    )
    
    # اللغات المدعومة
    SUPPORTED_LANGUAGES = {
        'ar': 'العربية',
        'en': 'English'
    }
    
    # المناطق الزمنية المدعومة
    SUPPORTED_TIMEZONES = {
        'Asia/Riyadh': 'الرياض',
        'Asia/Dubai': 'دبي',
        'Asia/Kuwait': 'الكويت',
        'UTC': 'التوقيت العالمي'
    }
    
    # المظاهر المدعومة
    SUPPORTED_THEMES = {
        'light': 'فاتح',
        'dark': 'داكن',
        'auto': 'تلقائي'
    }
    
    @hybrid_property
    def password(self):
        """منع قراءة كلمة المرور"""
        raise AttributeError('كلمة المرور غير قابلة للقراءة')
    
    @password.setter
    def password(self, password):
        """تعيين كلمة المرور مع التشفير"""
        self._password_hash = generate_password_hash(password)
        self.password_changed_at = datetime.utcnow()
    
    def set_password(self, password):
        """تعيين كلمة المرور"""
        self.password = password
    
    def check_password(self, password):
        """التحقق من كلمة المرور"""
        return check_password_hash(self._password_hash, password)
    
    @hybrid_property
    def two_factor_secret(self):
        """سر المصادقة الثنائية (مفكوك التشفير)"""
        if self._two_factor_secret:
            return self.decrypt_field(self._two_factor_secret)
        return None
    
    @two_factor_secret.setter
    def two_factor_secret(self, secret):
        """تعيين سر المصادقة الثنائية (مشفر)"""
        if secret:
            self._two_factor_secret = self.encrypt_field(secret)
        else:
            self._two_factor_secret = None
    
    @property
    def full_name(self):
        """الاسم الكامل"""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def display_name(self):
        """اسم العرض"""
        return self.full_name or self.username
    
    def is_locked(self):
        """فحص إذا كان الحساب مقفل"""
        if self.locked_until:
            return datetime.utcnow() < self.locked_until
        return False
    
    def lock_account(self, duration_minutes=30):
        """قفل الحساب لفترة محددة"""
        self.locked_until = datetime.utcnow() + timedelta(minutes=duration_minutes)
        self.failed_login_attempts = 0
        db.session.commit()
        
        # تسجيل قفل الحساب
        self.log_change('account_locked', {
            'locked_until': self.locked_until.isoformat(),
            'duration_minutes': duration_minutes
        })
    
    def unlock_account(self):
        """إلغاء قفل الحساب"""
        self.locked_until = None
        self.failed_login_attempts = 0
        db.session.commit()
        
        # تسجيل إلغاء القفل
        self.log_change('account_unlocked', {})
    
    def record_login_attempt(self, success=True, ip_address=None):
        """تسجيل محاولة تسجيل الدخول"""
        if success:
            self.last_login_at = datetime.utcnow()
            self.last_login_ip = ip_address
            self.login_count += 1
            self.failed_login_attempts = 0
            
            # إنشاء جلسة جديدة
            self.create_new_session()
            
            # تسجيل نجاح الدخول
            self.log_change('login_success', {
                'ip_address': ip_address,
                'login_count': self.login_count
            })
        else:
            self.failed_login_attempts += 1
            
            # قفل الحساب بعد 5 محاولات فاشلة
            max_attempts = current_app.config.get('MAX_LOGIN_ATTEMPTS', 5)
            if self.failed_login_attempts >= max_attempts:
                self.lock_account()
            
            # تسجيل فشل الدخول
            self.log_change('login_failed', {
                'ip_address': ip_address,
                'failed_attempts': self.failed_login_attempts
            })
        
        db.session.commit()
    
    def create_new_session(self):
        """إنشاء جلسة جديدة"""
        self.current_session_id = secrets.token_urlsafe(32)
        session_duration = current_app.config.get('SESSION_DURATION_HOURS', 24)
        self.session_expires_at = datetime.utcnow() + timedelta(hours=session_duration)
    
    def is_session_valid(self, session_id):
        """التحقق من صحة الجلسة"""
        if not self.current_session_id or not self.session_expires_at:
            return False
        
        if self.current_session_id != session_id:
            return False
        
        if datetime.utcnow() > self.session_expires_at:
            return False
        
        return True
    
    def invalidate_session(self):
        """إلغاء الجلسة الحالية"""
        self.current_session_id = None
        self.session_expires_at = None
        db.session.commit()
    
    def setup_two_factor(self):
        """إعداد المصادقة الثنائية"""
        if not self.two_factor_secret:
            # إنشاء سر جديد
            secret = pyotp.random_base32()
            self.two_factor_secret = secret
            
            # إنشاء رموز احتياطية
            backup_codes = [secrets.token_hex(4).upper() for _ in range(10)]
            self.backup_codes = backup_codes
            
            db.session.commit()
            
            # تسجيل إعداد المصادقة الثنائية
            self.log_change('two_factor_setup', {})
            
            return secret, backup_codes
        
        return self.two_factor_secret, self.backup_codes
    
    def enable_two_factor(self):
        """تفعيل المصادقة الثنائية"""
        self.two_factor_enabled = True
        db.session.commit()
        
        # تسجيل تفعيل المصادقة الثنائية
        self.log_change('two_factor_enabled', {})
    
    def disable_two_factor(self):
        """إلغاء تفعيل المصادقة الثنائية"""
        self.two_factor_enabled = False
        self.two_factor_secret = None
        self.backup_codes = None
        db.session.commit()
        
        # تسجيل إلغاء المصادقة الثنائية
        self.log_change('two_factor_disabled', {})
    
    def verify_two_factor_token(self, token):
        """التحقق من رمز المصادقة الثنائية"""
        if not self.two_factor_enabled or not self.two_factor_secret:
            return False
        
        # التحقق من الرمز المؤقت
        totp = pyotp.TOTP(self.two_factor_secret)
        if totp.verify(token, valid_window=1):
            return True
        
        # التحقق من الرموز الاحتياطية
        if self.backup_codes and token.upper() in self.backup_codes:
            # إزالة الرمز المستخدم
            self.backup_codes.remove(token.upper())
            db.session.commit()
            return True
        
        return False
    
    def get_two_factor_qr_code(self):
        """الحصول على QR Code للمصادقة الثنائية"""
        if not self.two_factor_secret:
            return None
        
        # إنشاء URI للمصادقة
        app_name = current_app.config.get('APP_NAME', 'نظام المحاسبة')
        totp_uri = pyotp.totp.TOTP(self.two_factor_secret).provisioning_uri(
            name=self.email,
            issuer_name=app_name
        )
        
        # إنشاء QR Code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(totp_uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # تحويل إلى base64
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        qr_code_data = base64.b64encode(buffer.getvalue()).decode()
        return f"data:image/png;base64,{qr_code_data}"
    
    def generate_reset_token(self):
        """إنشاء رمز إعادة تعيين كلمة المرور"""
        self.reset_token = secrets.token_urlsafe(32)
        self.reset_token_expires = datetime.utcnow() + timedelta(hours=1)
        db.session.commit()
        
        # تسجيل طلب إعادة التعيين
        self.log_change('password_reset_requested', {})
        
        return self.reset_token
    
    def verify_reset_token(self, token):
        """التحقق من رمز إعادة التعيين"""
        if not self.reset_token or not self.reset_token_expires:
            return False
        
        if self.reset_token != token:
            return False
        
        if datetime.utcnow() > self.reset_token_expires:
            return False
        
        return True
    
    def reset_password(self, new_password):
        """إعادة تعيين كلمة المرور"""
        self.password = new_password
        self.reset_token = None
        self.reset_token_expires = None
        
        # إلغاء جميع الجلسات
        self.invalidate_session()
        
        db.session.commit()
        
        # تسجيل إعادة تعيين كلمة المرور
        self.log_change('password_reset_completed', {})
    
    def generate_email_verification_token(self):
        """إنشاء رمز تأكيد البريد الإلكتروني"""
        self.email_verification_token = secrets.token_urlsafe(32)
        db.session.commit()
        
        return self.email_verification_token
    
    def verify_email(self, token):
        """تأكيد البريد الإلكتروني"""
        if self.email_verification_token == token:
            self.is_verified = True
            self.email_verified_at = datetime.utcnow()
            self.email_verification_token = None
            db.session.commit()
            
            # تسجيل تأكيد البريد
            self.log_change('email_verified', {})
            
            return True
        
        return False
    
    def has_role(self, role_name):
        """فحص إذا كان المستخدم لديه دور معين"""
        return self.roles.join(Role).filter(Role.name == role_name).first() is not None
    
    def has_permission(self, permission_name):
        """فحص إذا كان المستخدم لديه صلاحية معينة"""
        # المدير لديه جميع الصلاحيات
        if self.is_admin:
            return True
        
        # البحث في صلاحيات الأدوار
        return db.session.query(Permission).join(RolePermission).join(Role).join(UserRole).filter(
            UserRole.user_id == self.id,
            Permission.name == permission_name
        ).first() is not None
    
    def get_roles(self):
        """الحصول على جميع أدوار المستخدم"""
        return [user_role.role for user_role in self.roles]
    
    def get_permissions(self):
        """الحصول على جميع صلاحيات المستخدم"""
        if self.is_admin:
            return Permission.query.all()
        
        return db.session.query(Permission).join(RolePermission).join(Role).join(UserRole).filter(
            UserRole.user_id == self.id
        ).distinct().all()
    
    def to_dict(self, include_sensitive=False):
        """تحويل إلى قاموس مع إخفاء البيانات الحساسة"""
        data = super().to_dict()
        
        # إضافة البيانات المحسوبة
        data['full_name'] = self.full_name
        data['display_name'] = self.display_name
        data['is_locked'] = self.is_locked()
        data['roles'] = [role.name for role in self.get_roles()]
        data['permissions'] = [perm.name for perm in self.get_permissions()]
        
        # إخفاء البيانات الحساسة
        data.pop('_password_hash', None)
        data.pop('_two_factor_secret', None)
        data.pop('reset_token', None)
        data.pop('email_verification_token', None)
        data.pop('current_session_id', None)
        
        if include_sensitive:
            data['backup_codes'] = self.backup_codes
        else:
            data.pop('backup_codes', None)
        
        return data
    
    def __repr__(self):
        return f'<User {self.username}>'
