#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
النموذج الأساسي لجميع النماذج
Base Model for All Models
"""

from datetime import datetime, timezone
from app import db
from sqlalchemy import event
from sqlalchemy.ext.declarative import declared_attr

class BaseModel(db.Model):
    """النموذج الأساسي مع الحقول المشتركة"""
    
    __abstract__ = True
    
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(
        db.DateTime, 
        default=lambda: datetime.now(timezone.utc), 
        nullable=False,
        index=True
    )
    updated_at = db.Column(
        db.DateTime, 
        default=lambda: datetime.now(timezone.utc), 
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True
    )
    
    # حقول المراجعة
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    updated_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    # حقل الحذف الناعم
    is_deleted = db.Column(db.Boolean, default=False, nullable=False, index=True)
    deleted_at = db.Column(db.DateTime, nullable=True)
    deleted_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    @declared_attr
    def created_by(cls):
        return db.relationship('User', foreign_keys=[cls.created_by_id], post_update=True)
    
    @declared_attr
    def updated_by(cls):
        return db.relationship('User', foreign_keys=[cls.updated_by_id], post_update=True)
    
    @declared_attr
    def deleted_by(cls):
        return db.relationship('User', foreign_keys=[cls.deleted_by_id], post_update=True)
    
    def to_dict(self, include_relationships=False):
        """تحويل النموذج إلى قاموس"""
        result = {}
        
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            
            # تحويل التواريخ إلى نص
            if isinstance(value, datetime):
                value = value.isoformat()
            
            result[column.name] = value
        
        # إضافة العلاقات إذا طُلب ذلك
        if include_relationships:
            for relationship in self.__mapper__.relationships:
                related_obj = getattr(self, relationship.key)
                
                if related_obj is not None:
                    if hasattr(related_obj, 'to_dict'):
                        if relationship.uselist:
                            result[relationship.key] = [obj.to_dict() for obj in related_obj]
                        else:
                            result[relationship.key] = related_obj.to_dict()
                    else:
                        result[relationship.key] = str(related_obj)
        
        return result
    
    def soft_delete(self, user_id=None):
        """حذف ناعم للسجل"""
        self.is_deleted = True
        self.deleted_at = datetime.now(timezone.utc)
        if user_id:
            self.deleted_by_id = user_id
        db.session.commit()
    
    def restore(self):
        """استعادة السجل المحذوف"""
        self.is_deleted = False
        self.deleted_at = None
        self.deleted_by_id = None
        db.session.commit()
    
    @classmethod
    def get_active(cls):
        """الحصول على السجلات غير المحذوفة فقط"""
        return cls.query.filter_by(is_deleted=False)
    
    @classmethod
    def get_deleted(cls):
        """الحصول على السجلات المحذوفة فقط"""
        return cls.query.filter_by(is_deleted=True)
    
    def __repr__(self):
        return f'<{self.__class__.__name__} {self.id}>'

# إعداد الأحداث التلقائية
@event.listens_for(BaseModel, 'before_insert', propagate=True)
def set_created_by(mapper, connection, target):
    """تعيين منشئ السجل تلقائياً"""
    from flask_login import current_user
    if current_user and current_user.is_authenticated:
        target.created_by_id = current_user.id

@event.listens_for(BaseModel, 'before_update', propagate=True)
def set_updated_by(mapper, connection, target):
    """تعيين محدث السجل تلقائياً"""
    from flask_login import current_user
    if current_user and current_user.is_authenticated:
        target.updated_by_id = current_user.id
        target.updated_at = datetime.now(timezone.utc)

class AuditMixin:
    """خليط للمراجعة والتتبع"""
    
    def log_change(self, action, details=None, user_id=None):
        """تسجيل التغيير في سجل المراجعة"""
        from app.models.audit_log import AuditLog
        from flask_login import current_user
        
        if not user_id and current_user and current_user.is_authenticated:
            user_id = current_user.id
        
        log_entry = AuditLog(
            table_name=self.__tablename__,
            record_id=self.id,
            action=action,
            details=details or {},
            user_id=user_id
        )
        
        db.session.add(log_entry)
        db.session.commit()

class TimestampMixin:
    """خليط للطوابع الزمنية"""
    
    created_at = db.Column(
        db.DateTime, 
        default=lambda: datetime.now(timezone.utc), 
        nullable=False
    )
    updated_at = db.Column(
        db.DateTime, 
        default=lambda: datetime.now(timezone.utc), 
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

class SoftDeleteMixin:
    """خليط للحذف الناعم"""
    
    is_deleted = db.Column(db.Boolean, default=False, nullable=False)
    deleted_at = db.Column(db.DateTime, nullable=True)
    
    def soft_delete(self):
        """حذف ناعم"""
        self.is_deleted = True
        self.deleted_at = datetime.now(timezone.utc)
    
    def restore(self):
        """استعادة من الحذف"""
        self.is_deleted = False
        self.deleted_at = None
    
    @classmethod
    def active(cls):
        """فلترة السجلات النشطة فقط"""
        return cls.query.filter_by(is_deleted=False)

class SearchableMixin:
    """خليط للبحث"""
    
    @classmethod
    def search(cls, expression, page=1, per_page=20):
        """البحث في النموذج"""
        # يمكن تحسينه لاحقاً باستخدام Elasticsearch أو مكتبة بحث أخرى
        return cls.query.filter(
            cls.name.contains(expression) if hasattr(cls, 'name') else False
        ).paginate(page=page, per_page=per_page, error_out=False)

class CacheableMixin:
    """خليط للتخزين المؤقت"""
    
    @classmethod
    def get_cached(cls, cache_key, query_func, timeout=300):
        """الحصول على البيانات مع التخزين المؤقت"""
        from app import cache
        
        result = cache.get(cache_key)
        if result is None:
            result = query_func()
            cache.set(cache_key, result, timeout=timeout)
        
        return result
    
    def invalidate_cache(self, cache_keys):
        """إلغاء التخزين المؤقت"""
        from app import cache
        
        if isinstance(cache_keys, str):
            cache_keys = [cache_keys]
        
        for key in cache_keys:
            cache.delete(key)

class ValidatedMixin:
    """خليط للتحقق من صحة البيانات"""
    
    def validate(self):
        """التحقق من صحة البيانات"""
        errors = []
        
        # التحقق من الحقول المطلوبة
        for column in self.__table__.columns:
            if not column.nullable and column.default is None:
                value = getattr(self, column.name)
                if value is None or (isinstance(value, str) and not value.strip()):
                    errors.append(f'الحقل {column.name} مطلوب')
        
        return errors
    
    def is_valid(self):
        """فحص صحة البيانات"""
        return len(self.validate()) == 0

class EncryptedMixin:
    """خليط للتشفير"""
    
    @staticmethod
    def encrypt_field(value):
        """تشفير حقل"""
        from cryptography.fernet import Fernet
        import os
        
        key = os.environ.get('ENCRYPTION_KEY')
        if not key:
            return value  # إرجاع القيمة كما هي إذا لم يكن هناك مفتاح
        
        f = Fernet(key.encode())
        return f.encrypt(value.encode()).decode()
    
    @staticmethod
    def decrypt_field(encrypted_value):
        """فك تشفير حقل"""
        from cryptography.fernet import Fernet
        import os
        
        key = os.environ.get('ENCRYPTION_KEY')
        if not key:
            return encrypted_value  # إرجاع القيمة كما هي إذا لم يكن هناك مفتاح
        
        f = Fernet(key.encode())
        return f.decrypt(encrypted_value.encode()).decode()

# دالة مساعدة لإنشاء فهارس مركبة
def create_composite_index(table_name, columns, unique=False):
    """إنشاء فهرس مركب"""
    from sqlalchemy import Index
    
    index_name = f"idx_{table_name}_{'_'.join(columns)}"
    return Index(index_name, *columns, unique=unique)
