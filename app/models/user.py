#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نموذج المستخدم المحسن
Enhanced User Model
"""

from datetime import datetime, timezone
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Index
from app import db
from app.models.base import BaseModel, AuditMixin, EncryptedMixin

class User(UserMixin, BaseModel, AuditMixin, EncryptedMixin):
    """نموذج المستخدم مع ميزات أمان متقدمة"""
    
    __tablename__ = 'users'
    
    # المعلومات الأساسية
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    
    # معلومات الدور والقسم
    role = db.Column(db.String(20), nullable=False, default='user', index=True)
    department = db.Column(db.String(50), nullable=True)
    position = db.Column(db.String(100), nullable=True)
    
    # معلومات الاتصال
    phone = db.Column(db.String(20), nullable=True)
    address = db.Column(db.Text, nullable=True)
    
    # حالة الحساب
    is_active = db.Column(db.Boolean, default=True, nullable=False, index=True)
    is_verified = db.Column(db.Boolean, default=False, nullable=False)
    email_verified_at = db.Column(db.DateTime, nullable=True)
    
    # معلومات تسجيل الدخول
    last_login = db.Column(db.DateTime, nullable=True)
    login_count = db.Column(db.Integer, default=0, nullable=False)
    failed_login_attempts = db.Column(db.Integer, default=0, nullable=False)
    locked_until = db.Column(db.DateTime, nullable=True)
    
    # إعدادات المستخدم
    preferred_language = db.Column(db.String(5), default='ar', nullable=False)
    timezone = db.Column(db.String(50), default='Asia/Riyadh', nullable=False)
    theme = db.Column(db.String(20), default='light', nullable=False)
    
    # المصادقة الثنائية
    two_factor_enabled = db.Column(db.Boolean, default=False, nullable=False)
    two_factor_secret = db.Column(db.String(32), nullable=True)
    backup_codes = db.Column(db.Text, nullable=True)  # مشفرة
    
    # الصلاحيات التفصيلية
    can_view_reports = db.Column(db.Boolean, default=True, nullable=False)
    can_manage_invoices = db.Column(db.Boolean, default=True, nullable=False)
    can_manage_customers = db.Column(db.Boolean, default=True, nullable=False)
    can_manage_products = db.Column(db.Boolean, default=True, nullable=False)
    can_manage_employees = db.Column(db.Boolean, default=False, nullable=False)
    can_manage_payroll = db.Column(db.Boolean, default=False, nullable=False)
    can_manage_settings = db.Column(db.Boolean, default=False, nullable=False)
    can_manage_users = db.Column(db.Boolean, default=False, nullable=False)
    can_manage_backups = db.Column(db.Boolean, default=False, nullable=False)
    can_view_audit_logs = db.Column(db.Boolean, default=False, nullable=False)
    
    # معلومات إضافية
    avatar_url = db.Column(db.String(255), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    
    # فهارس محسنة
    __table_args__ = (
        Index('idx_user_role_active', 'role', 'is_active'),
        Index('idx_user_department_role', 'department', 'role'),
        Index('idx_user_login_info', 'last_login', 'is_active'),
        Index('idx_user_email_verified', 'email', 'is_verified'),
    )
    
    # الأدوار المتاحة
    ROLES = {
        'super_admin': 'مدير عام',
        'admin': 'مدير',
        'manager': 'مشرف',
        'accountant': 'محاسب',
        'employee': 'موظف',
        'viewer': 'مشاهد'
    }
    
    # الثيمات المتاحة
    THEMES = {
        'light': 'فاتح',
        'dark': 'داكن',
        'auto': 'تلقائي'
    }
    
    def set_password(self, password):
        """تشفير وحفظ كلمة المرور"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """التحقق من كلمة المرور"""
        return check_password_hash(self.password_hash, password)
    
    def get_role_display(self):
        """الحصول على اسم الدور للعرض"""
        return self.ROLES.get(self.role, self.role)
    
    def has_permission(self, permission):
        """فحص صلاحية معينة"""
        # المدير العام له جميع الصلاحيات
        if self.role == 'super_admin':
            return True
        
        # فحص الصلاحية المحددة
        return getattr(self, f'can_{permission}', False)
    
    def has_role(self, role):
        """فحص الدور"""
        if isinstance(role, list):
            return self.role in role
        return self.role == role
    
    def is_admin(self):
        """فحص إذا كان المستخدم مدير"""
        return self.role in ['super_admin', 'admin']
    
    def is_manager(self):
        """فحص إذا كان المستخدم مشرف أو أعلى"""
        return self.role in ['super_admin', 'admin', 'manager']
    
    def can_access_user_management(self):
        """فحص إمكانية الوصول لإدارة المستخدمين"""
        return self.has_permission('manage_users')
    
    def can_access_system_settings(self):
        """فحص إمكانية الوصول لإعدادات النظام"""
        return self.has_permission('manage_settings')
    
    def record_login(self):
        """تسجيل عملية دخول ناجحة"""
        self.last_login = datetime.now(timezone.utc)
        self.login_count += 1
        self.failed_login_attempts = 0
        self.locked_until = None
        db.session.commit()
        
        # تسجيل في سجل المراجعة
        self.log_change('login', {'ip_address': self.get_current_ip()})
    
    def record_failed_login(self):
        """تسجيل محاولة دخول فاشلة"""
        self.failed_login_attempts += 1
        
        # قفل الحساب بعد 5 محاولات فاشلة
        if self.failed_login_attempts >= 5:
            from datetime import timedelta
            self.locked_until = datetime.now(timezone.utc) + timedelta(minutes=30)
        
        db.session.commit()
        
        # تسجيل في سجل المراجعة
        self.log_change('failed_login', {
            'attempts': self.failed_login_attempts,
            'ip_address': self.get_current_ip()
        })
    
    def is_locked(self):
        """فحص إذا كان الحساب مقفل"""
        if self.locked_until:
            return datetime.now(timezone.utc) < self.locked_until
        return False
    
    def unlock_account(self):
        """إلغاء قفل الحساب"""
        self.failed_login_attempts = 0
        self.locked_until = None
        db.session.commit()
    
    def enable_two_factor(self):
        """تفعيل المصادقة الثنائية"""
        import pyotp
        import secrets
        
        # إنشاء مفتاح سري
        secret = pyotp.random_base32()
        self.two_factor_secret = secret
        
        # إنشاء رموز احتياطية
        backup_codes = [secrets.token_hex(4) for _ in range(10)]
        self.backup_codes = self.encrypt_field(','.join(backup_codes))
        
        self.two_factor_enabled = True
        db.session.commit()
        
        return secret, backup_codes
    
    def disable_two_factor(self):
        """تعطيل المصادقة الثنائية"""
        self.two_factor_enabled = False
        self.two_factor_secret = None
        self.backup_codes = None
        db.session.commit()
    
    def verify_two_factor_token(self, token):
        """التحقق من رمز المصادقة الثنائية"""
        if not self.two_factor_enabled or not self.two_factor_secret:
            return False
        
        import pyotp
        totp = pyotp.TOTP(self.two_factor_secret)
        return totp.verify(token, valid_window=1)
    
    def verify_backup_code(self, code):
        """التحقق من الرمز الاحتياطي"""
        if not self.backup_codes:
            return False
        
        try:
            codes = self.decrypt_field(self.backup_codes).split(',')
            if code in codes:
                # إزالة الرمز المستخدم
                codes.remove(code)
                self.backup_codes = self.encrypt_field(','.join(codes))
                db.session.commit()
                return True
        except:
            pass
        
        return False
    
    def get_qr_code_url(self, app_name='Accounting System'):
        """الحصول على رابط QR للمصادقة الثنائية"""
        if not self.two_factor_secret:
            return None
        
        import pyotp
        totp = pyotp.TOTP(self.two_factor_secret)
        return totp.provisioning_uri(
            name=self.email,
            issuer_name=app_name
        )
    
    def get_current_ip(self):
        """الحصول على IP الحالي"""
        from flask import request
        return request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    
    def to_dict(self, include_sensitive=False):
        """تحويل إلى قاموس مع إخفاء البيانات الحساسة"""
        data = super().to_dict()
        
        # إزالة البيانات الحساسة
        if not include_sensitive:
            sensitive_fields = [
                'password_hash', 'two_factor_secret', 'backup_codes'
            ]
            for field in sensitive_fields:
                data.pop(field, None)
        
        # إضافة معلومات إضافية
        data['role_display'] = self.get_role_display()
        data['is_locked'] = self.is_locked()
        
        return data
    
    def __repr__(self):
        return f'<User {self.username}>'
