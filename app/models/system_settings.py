#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نموذج إعدادات النظام
System Settings Model
"""

from datetime import datetime
from sqlalchemy import Index, event
from sqlalchemy.ext.hybrid import hybrid_property
from app import db
from app.models.base import BaseModel, AuditMixin, EncryptedMixin

class SystemSettings(BaseModel, AuditMixin, EncryptedMixin):
    """نموذج إعدادات النظام مع تشفير القيم الحساسة"""
    
    __tablename__ = 'system_settings'
    
    # معرف الإعداد
    key = db.Column(db.String(100), unique=True, nullable=False, index=True)
    
    # قيمة الإعداد (مشفرة إذا كانت حساسة)
    _value = db.Column('value', db.Text, nullable=True)
    _encrypted_value = db.Column('encrypted_value', db.Text, nullable=True)
    
    # معلومات الإعداد
    category = db.Column(db.String(50), nullable=False, index=True)
    data_type = db.Column(db.String(20), default='string', nullable=False)
    is_sensitive = db.Column(db.Boolean, default=False, nullable=False)
    is_system = db.Column(db.Boolean, default=False, nullable=False)  # إعدادات النظام الأساسية
    
    # وصف الإعداد
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    
    # قيود الإعداد
    min_value = db.Column(db.Float, nullable=True)
    max_value = db.Column(db.Float, nullable=True)
    allowed_values = db.Column(db.JSON, nullable=True)  # قائمة القيم المسموحة
    validation_regex = db.Column(db.String(500), nullable=True)
    
    # معلومات العرض
    display_order = db.Column(db.Integer, default=0, nullable=False)
    is_visible = db.Column(db.Boolean, default=True, nullable=False)
    requires_restart = db.Column(db.Boolean, default=False, nullable=False)
    
    # فهارس محسنة
    __table_args__ = (
        Index('idx_settings_category_order', 'category', 'display_order'),
        Index('idx_settings_key_category', 'key', 'category'),
        Index('idx_settings_visible_system', 'is_visible', 'is_system'),
    )
    
    # أنواع البيانات المدعومة
    DATA_TYPES = {
        'string': 'نص',
        'integer': 'رقم صحيح',
        'float': 'رقم عشري',
        'boolean': 'صحيح/خطأ',
        'json': 'JSON',
        'email': 'بريد إلكتروني',
        'url': 'رابط',
        'password': 'كلمة مرور',
        'file': 'ملف',
        'color': 'لون',
        'date': 'تاريخ',
        'datetime': 'تاريخ ووقت'
    }
    
    # فئات الإعدادات
    CATEGORIES = {
        'general': 'عام',
        'company': 'معلومات الشركة',
        'financial': 'مالي',
        'security': 'أمان',
        'email': 'بريد إلكتروني',
        'backup': 'نسخ احتياطي',
        'notifications': 'إشعارات',
        'appearance': 'المظهر',
        'integrations': 'تكاملات',
        'advanced': 'متقدم'
    }
    
    @hybrid_property
    def value(self):
        """قيمة الإعداد (مفكوكة التشفير إذا كانت حساسة)"""
        if self.is_sensitive and self._encrypted_value:
            decrypted = self.decrypt_field(self._encrypted_value)
            return self._convert_from_string(decrypted)
        elif self._value:
            return self._convert_from_string(self._value)
        return None
    
    @value.setter
    def value(self, new_value):
        """تعيين قيمة الإعداد (مشفرة إذا كانت حساسة)"""
        string_value = self._convert_to_string(new_value)
        
        if self.is_sensitive:
            self._encrypted_value = self.encrypt_field(string_value) if string_value else None
            self._value = None
        else:
            self._value = string_value
            self._encrypted_value = None
    
    def _convert_to_string(self, value):
        """تحويل القيمة إلى نص للتخزين"""
        if value is None:
            return None
        
        if self.data_type == 'boolean':
            return 'true' if value else 'false'
        elif self.data_type == 'json':
            import json
            return json.dumps(value, ensure_ascii=False)
        elif self.data_type in ['integer', 'float']:
            return str(value)
        elif self.data_type in ['date', 'datetime']:
            if isinstance(value, datetime):
                return value.isoformat()
            return str(value)
        else:
            return str(value)
    
    def _convert_from_string(self, string_value):
        """تحويل النص المخزن إلى النوع المطلوب"""
        if string_value is None:
            return None
        
        try:
            if self.data_type == 'boolean':
                return string_value.lower() in ['true', '1', 'yes', 'on']
            elif self.data_type == 'integer':
                return int(string_value)
            elif self.data_type == 'float':
                return float(string_value)
            elif self.data_type == 'json':
                import json
                return json.loads(string_value)
            elif self.data_type == 'date':
                from datetime import datetime
                return datetime.fromisoformat(string_value).date()
            elif self.data_type == 'datetime':
                from datetime import datetime
                return datetime.fromisoformat(string_value)
            else:
                return string_value
        except (ValueError, TypeError):
            return string_value
    
    def validate_value(self, value):
        """التحقق من صحة القيمة"""
        errors = []
        
        # التحقق من النوع
        if value is not None:
            if self.data_type == 'integer':
                try:
                    int(value)
                except (ValueError, TypeError):
                    errors.append('القيمة يجب أن تكون رقم صحيح')
            
            elif self.data_type == 'float':
                try:
                    float(value)
                except (ValueError, TypeError):
                    errors.append('القيمة يجب أن تكون رقم عشري')
            
            elif self.data_type == 'email':
                from app.security.validators import validate_email_format
                result = validate_email_format(str(value))
                if not result['is_valid']:
                    errors.append(result['error'])
            
            elif self.data_type == 'url':
                from app.security.validators import validate_url
                result = validate_url(str(value))
                if not result['is_valid']:
                    errors.append(result['error'])
            
            elif self.data_type == 'json':
                try:
                    import json
                    json.loads(str(value))
                except (ValueError, TypeError):
                    errors.append('القيمة يجب أن تكون JSON صحيح')
        
        # التحقق من الحد الأدنى والأقصى
        if self.data_type in ['integer', 'float'] and value is not None:
            numeric_value = float(value)
            
            if self.min_value is not None and numeric_value < self.min_value:
                errors.append(f'القيمة يجب أن تكون أكبر من أو تساوي {self.min_value}')
            
            if self.max_value is not None and numeric_value > self.max_value:
                errors.append(f'القيمة يجب أن تكون أصغر من أو تساوي {self.max_value}')
        
        # التحقق من القيم المسموحة
        if self.allowed_values and value is not None:
            if str(value) not in [str(v) for v in self.allowed_values]:
                errors.append(f'القيمة يجب أن تكون واحدة من: {", ".join(map(str, self.allowed_values))}')
        
        # التحقق من التعبير النمطي
        if self.validation_regex and value is not None:
            import re
            if not re.match(self.validation_regex, str(value)):
                errors.append('تنسيق القيمة غير صحيح')
        
        return errors
    
    def get_category_display(self):
        """الحصول على فئة الإعداد للعرض"""
        return self.CATEGORIES.get(self.category, self.category)
    
    def get_data_type_display(self):
        """الحصول على نوع البيانات للعرض"""
        return self.DATA_TYPES.get(self.data_type, self.data_type)
    
    def get_display_value(self):
        """الحصول على القيمة للعرض (مع إخفاء الحساسة)"""
        if self.is_sensitive:
            if self.data_type == 'password':
                return '••••••••'
            elif self.value:
                return '***'
            else:
                return ''
        else:
            return self.value
    
    @classmethod
    def get_setting(cls, key, default=None):
        """الحصول على قيمة إعداد"""
        setting = cls.query.filter_by(key=key).first()
        if setting:
            return setting.value
        return default
    
    @classmethod
    def set_setting(cls, key, value, category='general', title=None, description=None, 
                   data_type='string', is_sensitive=False):
        """تعيين قيمة إعداد"""
        setting = cls.query.filter_by(key=key).first()
        
        if setting:
            # تحديث الإعداد الموجود
            old_value = setting.value
            setting.value = value
            
            # تسجيل التغيير
            setting.log_change('update', {
                'key': key,
                'old_value': '***' if setting.is_sensitive else old_value,
                'new_value': '***' if setting.is_sensitive else value
            })
        else:
            # إنشاء إعداد جديد
            setting = cls(
                key=key,
                value=value,
                category=category,
                title=title or key,
                description=description,
                data_type=data_type,
                is_sensitive=is_sensitive
            )
            db.session.add(setting)
            
            # تسجيل الإنشاء
            setting.log_change('create', {
                'key': key,
                'category': category,
                'data_type': data_type
            })
        
        db.session.commit()
        return setting
    
    @classmethod
    def get_category_settings(cls, category):
        """الحصول على جميع إعدادات فئة معينة"""
        return cls.query.filter_by(
            category=category,
            is_visible=True
        ).order_by(cls.display_order, cls.title).all()
    
    @classmethod
    def get_all_categories(cls):
        """الحصول على جميع الفئات المتاحة"""
        categories = db.session.query(cls.category).distinct().all()
        return [cat[0] for cat in categories]
    
    @classmethod
    def initialize_default_settings(cls):
        """تهيئة الإعدادات الافتراضية"""
        default_settings = [
            # إعدادات عامة
            ('app_name', 'نظام المحاسبة الاحترافي', 'general', 'اسم التطبيق', 'string', False),
            ('app_version', '2.0.0', 'general', 'إصدار التطبيق', 'string', False),
            ('default_language', 'ar', 'general', 'اللغة الافتراضية', 'string', False),
            ('timezone', 'Asia/Riyadh', 'general', 'المنطقة الزمنية', 'string', False),
            
            # معلومات الشركة
            ('company_name', '', 'company', 'اسم الشركة', 'string', False),
            ('company_address', '', 'company', 'عنوان الشركة', 'string', False),
            ('company_phone', '', 'company', 'هاتف الشركة', 'string', False),
            ('company_email', '', 'company', 'بريد الشركة', 'email', False),
            ('company_tax_number', '', 'company', 'الرقم الضريبي', 'string', True),
            ('company_logo', '', 'company', 'شعار الشركة', 'file', False),
            
            # إعدادات مالية
            ('default_currency', 'SAR', 'financial', 'العملة الافتراضية', 'string', False),
            ('tax_rate', 15.0, 'financial', 'نسبة الضريبة', 'float', False),
            ('payment_terms', 30, 'financial', 'شروط الدفع (أيام)', 'integer', False),
            
            # إعدادات الأمان
            ('session_timeout', 3600, 'security', 'انتهاء الجلسة (ثانية)', 'integer', False),
            ('max_login_attempts', 5, 'security', 'محاولات الدخول القصوى', 'integer', False),
            ('password_min_length', 8, 'security', 'الحد الأدنى لطول كلمة المرور', 'integer', False),
            ('two_factor_enabled', False, 'security', 'تفعيل المصادقة الثنائية', 'boolean', False),
            
            # إعدادات البريد الإلكتروني
            ('smtp_server', '', 'email', 'خادم SMTP', 'string', False),
            ('smtp_port', 587, 'email', 'منفذ SMTP', 'integer', False),
            ('smtp_username', '', 'email', 'اسم مستخدم SMTP', 'string', True),
            ('smtp_password', '', 'email', 'كلمة مرور SMTP', 'password', True),
            ('email_from', '', 'email', 'البريد المرسل', 'email', False),
            
            # إعدادات النسخ الاحتياطي
            ('backup_enabled', True, 'backup', 'تفعيل النسخ الاحتياطي', 'boolean', False),
            ('backup_frequency', 'daily', 'backup', 'تكرار النسخ الاحتياطي', 'string', False),
            ('backup_retention_days', 30, 'backup', 'مدة الاحتفاظ بالنسخ (أيام)', 'integer', False),
            
            # إعدادات المظهر
            ('theme', 'light', 'appearance', 'المظهر', 'string', False),
            ('items_per_page', 20, 'appearance', 'عدد العناصر في الصفحة', 'integer', False),
            ('date_format', 'Y-m-d', 'appearance', 'تنسيق التاريخ', 'string', False),
        ]
        
        for key, value, category, title, data_type, is_sensitive in default_settings:
            if not cls.query.filter_by(key=key).first():
                setting = cls(
                    key=key,
                    value=value,
                    category=category,
                    title=title,
                    data_type=data_type,
                    is_sensitive=is_sensitive,
                    is_system=True
                )
                db.session.add(setting)
        
        db.session.commit()
    
    def to_dict(self, include_sensitive=False):
        """تحويل إلى قاموس"""
        data = super().to_dict()
        
        # إضافة البيانات المحسوبة
        data['category_display'] = self.get_category_display()
        data['data_type_display'] = self.get_data_type_display()
        data['display_value'] = self.get_display_value()
        
        # إضافة القيمة الحقيقية إذا طُلب ذلك
        if include_sensitive or not self.is_sensitive:
            data['value'] = self.value
        
        # إخفاء القيم المشفرة
        data.pop('_value', None)
        data.pop('_encrypted_value', None)
        
        return data
    
    def __repr__(self):
        return f'<SystemSettings {self.key}>'

# الأحداث التلقائية
@event.listens_for(SystemSettings, 'after_insert')
def log_setting_creation(mapper, connection, target):
    """تسجيل إنشاء إعداد جديد"""
    target.log_change('create', {
        'key': target.key,
        'category': target.category,
        'data_type': target.data_type,
        'is_sensitive': target.is_sensitive
    })

@event.listens_for(SystemSettings, 'after_update')
def log_setting_update(mapper, connection, target):
    """تسجيل تحديث الإعداد"""
    target.log_change('update', {
        'key': target.key,
        'category': target.category
    })
