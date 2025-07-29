#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نموذج سجل المراجعة والتتبع
Audit Log and Tracking Model
"""

from datetime import datetime, timezone
from sqlalchemy import Index, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.sqlite import JSON
from app import db
from app.models.base import BaseModel

class AuditLog(BaseModel):
    """سجل المراجعة لتتبع جميع التغييرات"""
    
    __tablename__ = 'audit_logs'
    
    # معلومات السجل
    table_name = db.Column(db.String(50), nullable=False, index=True)
    record_id = db.Column(db.Integer, nullable=True, index=True)
    action = db.Column(db.String(20), nullable=False, index=True)
    
    # تفاصيل التغيير
    old_values = db.Column(JSON, nullable=True)
    new_values = db.Column(JSON, nullable=True)
    details = db.Column(JSON, nullable=True)
    
    # معلومات المستخدم والجلسة
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
    session_id = db.Column(db.String(255), nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.Text, nullable=True)
    
    # معلومات إضافية
    severity = db.Column(db.String(10), default='info', nullable=False, index=True)
    category = db.Column(db.String(30), nullable=True, index=True)
    tags = db.Column(JSON, nullable=True)
    
    # العلاقات
    user = db.relationship('User', backref='audit_logs', lazy='select')
    
    # فهارس محسنة
    __table_args__ = (
        Index('idx_audit_table_action', 'table_name', 'action'),
        Index('idx_audit_user_date', 'user_id', 'created_at'),
        Index('idx_audit_record_table', 'record_id', 'table_name'),
        Index('idx_audit_severity_date', 'severity', 'created_at'),
        Index('idx_audit_category_date', 'category', 'created_at'),
        Index('idx_audit_ip_date', 'ip_address', 'created_at'),
    )
    
    # أنواع الأحداث
    ACTIONS = {
        'create': 'إنشاء',
        'update': 'تحديث',
        'delete': 'حذف',
        'restore': 'استعادة',
        'login': 'تسجيل دخول',
        'logout': 'تسجيل خروج',
        'failed_login': 'محاولة دخول فاشلة',
        'password_change': 'تغيير كلمة المرور',
        'permission_change': 'تغيير صلاحيات',
        'export': 'تصدير بيانات',
        'import': 'استيراد بيانات',
        'backup': 'نسخ احتياطي',
        'restore_backup': 'استعادة نسخة احتياطية',
        'system_config': 'تغيير إعدادات النظام',
        'view': 'عرض',
        'search': 'بحث',
        'print': 'طباعة'
    }
    
    # مستويات الخطورة
    SEVERITY_LEVELS = {
        'debug': 'تصحيح',
        'info': 'معلومات',
        'warning': 'تحذير',
        'error': 'خطأ',
        'critical': 'حرج'
    }
    
    # فئات الأحداث
    CATEGORIES = {
        'authentication': 'المصادقة',
        'authorization': 'التخويل',
        'data_access': 'الوصول للبيانات',
        'data_modification': 'تعديل البيانات',
        'system_administration': 'إدارة النظام',
        'financial_transaction': 'معاملة مالية',
        'user_management': 'إدارة المستخدمين',
        'reporting': 'التقارير',
        'backup_restore': 'النسخ الاحتياطي',
        'security': 'الأمان'
    }
    
    @classmethod
    def log_action(cls, table_name, record_id, action, old_values=None, 
                   new_values=None, details=None, user_id=None, severity='info', 
                   category=None, tags=None):
        """تسجيل حدث في سجل المراجعة"""
        
        from flask import request, session
        from flask_login import current_user
        
        # الحصول على معلومات المستخدم
        if not user_id and current_user and current_user.is_authenticated:
            user_id = current_user.id
        
        # الحصول على معلومات الطلب
        ip_address = None
        user_agent = None
        session_id = None
        
        if request:
            ip_address = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
            user_agent = request.headers.get('User-Agent')
            session_id = session.get('_id') if session else None
        
        # إنشاء سجل المراجعة
        log_entry = cls(
            table_name=table_name,
            record_id=record_id,
            action=action,
            old_values=old_values,
            new_values=new_values,
            details=details or {},
            user_id=user_id,
            session_id=session_id,
            ip_address=ip_address,
            user_agent=user_agent,
            severity=severity,
            category=category,
            tags=tags or []
        )
        
        db.session.add(log_entry)
        db.session.commit()
        
        return log_entry
    
    @classmethod
    def log_login(cls, user_id, success=True, details=None):
        """تسجيل محاولة دخول"""
        action = 'login' if success else 'failed_login'
        severity = 'info' if success else 'warning'
        
        return cls.log_action(
            table_name='users',
            record_id=user_id,
            action=action,
            details=details,
            user_id=user_id if success else None,
            severity=severity,
            category='authentication'
        )
    
    @classmethod
    def log_data_change(cls, model_instance, action, old_values=None, new_values=None):
        """تسجيل تغيير في البيانات"""
        
        # تحديد الفئة بناءً على نوع النموذج
        category_map = {
            'users': 'user_management',
            'customers': 'data_modification',
            'invoices': 'financial_transaction',
            'payments': 'financial_transaction',
            'products': 'data_modification',
            'employees': 'user_management'
        }
        
        table_name = model_instance.__tablename__
        category = category_map.get(table_name, 'data_modification')
        
        return cls.log_action(
            table_name=table_name,
            record_id=model_instance.id,
            action=action,
            old_values=old_values,
            new_values=new_values,
            category=category,
            severity='info'
        )
    
    @classmethod
    def log_financial_transaction(cls, table_name, record_id, action, amount=None, details=None):
        """تسجيل معاملة مالية"""
        
        if details is None:
            details = {}
        
        if amount:
            details['amount'] = float(amount)
        
        return cls.log_action(
            table_name=table_name,
            record_id=record_id,
            action=action,
            details=details,
            severity='info',
            category='financial_transaction',
            tags=['financial', 'transaction']
        )
    
    @classmethod
    def log_security_event(cls, event_type, details=None, severity='warning'):
        """تسجيل حدث أمني"""
        
        return cls.log_action(
            table_name='security',
            record_id=None,
            action=event_type,
            details=details,
            severity=severity,
            category='security',
            tags=['security', event_type]
        )
    
    @classmethod
    def log_system_event(cls, event_type, details=None):
        """تسجيل حدث نظام"""
        
        return cls.log_action(
            table_name='system',
            record_id=None,
            action=event_type,
            details=details,
            severity='info',
            category='system_administration',
            tags=['system', event_type]
        )
    
    @classmethod
    def get_user_activity(cls, user_id, days=30):
        """الحصول على نشاط المستخدم"""
        
        from datetime import timedelta
        since_date = datetime.now(timezone.utc) - timedelta(days=days)
        
        return cls.query.filter(
            cls.user_id == user_id,
            cls.created_at >= since_date
        ).order_by(cls.created_at.desc()).all()
    
    @classmethod
    def get_table_activity(cls, table_name, record_id=None, days=30):
        """الحصول على نشاط جدول معين"""
        
        from datetime import timedelta
        since_date = datetime.now(timezone.utc) - timedelta(days=days)
        
        query = cls.query.filter(
            cls.table_name == table_name,
            cls.created_at >= since_date
        )
        
        if record_id:
            query = query.filter(cls.record_id == record_id)
        
        return query.order_by(cls.created_at.desc()).all()
    
    @classmethod
    def get_security_events(cls, days=7):
        """الحصول على الأحداث الأمنية"""
        
        from datetime import timedelta
        since_date = datetime.now(timezone.utc) - timedelta(days=days)
        
        return cls.query.filter(
            cls.category == 'security',
            cls.created_at >= since_date
        ).order_by(cls.created_at.desc()).all()
    
    @classmethod
    def get_failed_logins(cls, hours=24):
        """الحصول على محاولات الدخول الفاشلة"""
        
        from datetime import timedelta
        since_date = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        return cls.query.filter(
            cls.action == 'failed_login',
            cls.created_at >= since_date
        ).order_by(cls.created_at.desc()).all()
    
    @classmethod
    def cleanup_old_logs(cls, days=90):
        """تنظيف السجلات القديمة"""
        
        from datetime import timedelta
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        
        # حذف السجلات القديمة ما عدا الأحداث الحرجة
        deleted_count = cls.query.filter(
            cls.created_at < cutoff_date,
            cls.severity != 'critical'
        ).delete()
        
        db.session.commit()
        
        return deleted_count
    
    def get_action_display(self):
        """الحصول على اسم الحدث للعرض"""
        return self.ACTIONS.get(self.action, self.action)
    
    def get_severity_display(self):
        """الحصول على مستوى الخطورة للعرض"""
        return self.SEVERITY_LEVELS.get(self.severity, self.severity)
    
    def get_category_display(self):
        """الحصول على فئة الحدث للعرض"""
        return self.CATEGORIES.get(self.category, self.category)
    
    def to_dict(self):
        """تحويل إلى قاموس"""
        data = super().to_dict()
        
        # إضافة معلومات إضافية
        data['action_display'] = self.get_action_display()
        data['severity_display'] = self.get_severity_display()
        data['category_display'] = self.get_category_display()
        
        if self.user:
            data['user_name'] = self.user.full_name
            data['username'] = self.user.username
        
        return data
    
    def __repr__(self):
        return f'<AuditLog {self.action} on {self.table_name}>'
