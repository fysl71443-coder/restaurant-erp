#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نموذج العملاء المحسن
Enhanced Customer Model
"""

from sqlalchemy import Index, event
from sqlalchemy.ext.hybrid import hybrid_property
from app import db
from app.models.base import BaseModel, AuditMixin, EncryptedMixin
from app.security.validators import validate_email_format, validate_phone_number

class Customer(BaseModel, AuditMixin, EncryptedMixin):
    """نموذج العملاء مع ميزات أمان متقدمة"""
    
    __tablename__ = 'customers'
    
    # المعلومات الأساسية
    name = db.Column(db.String(100), nullable=False, index=True)
    email = db.Column(db.String(120), nullable=True, index=True)
    phone = db.Column(db.String(20), nullable=True, index=True)
    
    # معلومات الشركة
    company_name = db.Column(db.String(150), nullable=True)
    tax_number = db.Column(db.String(50), nullable=True, index=True)
    commercial_register = db.Column(db.String(50), nullable=True)
    
    # معلومات الاتصال
    address = db.Column(db.Text, nullable=True)
    city = db.Column(db.String(50), nullable=True, index=True)
    country = db.Column(db.String(50), default='السعودية', nullable=False)
    postal_code = db.Column(db.String(10), nullable=True)
    
    # معلومات مالية (مشفرة)
    _credit_limit = db.Column('credit_limit', db.Text, nullable=True)
    _bank_account = db.Column('bank_account', db.Text, nullable=True)
    _iban = db.Column('iban', db.Text, nullable=True)
    
    # معلومات إضافية
    customer_type = db.Column(db.String(20), default='individual', nullable=False, index=True)
    status = db.Column(db.String(20), default='active', nullable=False, index=True)
    payment_terms = db.Column(db.Integer, default=30, nullable=False)  # أيام
    discount_rate = db.Column(db.Float, default=0.0, nullable=False)
    
    # معلومات التواصل الإضافية
    website = db.Column(db.String(255), nullable=True)
    social_media = db.Column(db.JSON, nullable=True)
    
    # معلومات المبيعات
    total_purchases = db.Column(db.Float, default=0.0, nullable=False)
    last_purchase_date = db.Column(db.DateTime, nullable=True)
    purchase_count = db.Column(db.Integer, default=0, nullable=False)
    
    # تقييم العميل
    rating = db.Column(db.Integer, default=5, nullable=False)  # 1-5
    notes = db.Column(db.Text, nullable=True)
    
    # معلومات الأمان
    verification_status = db.Column(db.String(20), default='pending', nullable=False)
    risk_level = db.Column(db.String(20), default='low', nullable=False)
    
    # العلاقات
    invoices = db.relationship('Invoice', backref='customer_rel', lazy='dynamic', cascade='all, delete-orphan')
    payments = db.relationship('Payment', backref='customer_rel', lazy='dynamic')
    
    # فهارس محسنة
    __table_args__ = (
        Index('idx_customer_name_status', 'name', 'status'),
        Index('idx_customer_email_phone', 'email', 'phone'),
        Index('idx_customer_company_tax', 'company_name', 'tax_number'),
        Index('idx_customer_city_country', 'city', 'country'),
        Index('idx_customer_type_status', 'customer_type', 'status'),
        Index('idx_customer_verification_risk', 'verification_status', 'risk_level'),
        Index('idx_customer_purchases', 'total_purchases', 'last_purchase_date'),
    )
    
    # أنواع العملاء
    CUSTOMER_TYPES = {
        'individual': 'فرد',
        'company': 'شركة',
        'government': 'جهة حكومية',
        'nonprofit': 'منظمة غير ربحية'
    }
    
    # حالات العميل
    STATUSES = {
        'active': 'نشط',
        'inactive': 'غير نشط',
        'suspended': 'معلق',
        'blacklisted': 'محظور'
    }
    
    # مستويات المخاطر
    RISK_LEVELS = {
        'low': 'منخفض',
        'medium': 'متوسط',
        'high': 'عالي',
        'critical': 'حرج'
    }
    
    # حالات التحقق
    VERIFICATION_STATUSES = {
        'pending': 'في الانتظار',
        'verified': 'محقق',
        'rejected': 'مرفوض',
        'expired': 'منتهي الصلاحية'
    }
    
    @hybrid_property
    def credit_limit(self):
        """الحد الائتماني (مفكوك التشفير)"""
        if self._credit_limit:
            decrypted = self.decrypt_field(self._credit_limit)
            return float(decrypted) if decrypted else 0.0
        return 0.0
    
    @credit_limit.setter
    def credit_limit(self, value):
        """تعيين الحد الائتماني (مشفر)"""
        if value is not None:
            self._credit_limit = self.encrypt_field(str(value))
        else:
            self._credit_limit = None
    
    @hybrid_property
    def bank_account(self):
        """رقم الحساب البنكي (مفكوك التشفير)"""
        if self._bank_account:
            return self.decrypt_field(self._bank_account)
        return None
    
    @bank_account.setter
    def bank_account(self, value):
        """تعيين رقم الحساب البنكي (مشفر)"""
        if value:
            self._bank_account = self.encrypt_field(str(value))
        else:
            self._bank_account = None
    
    @hybrid_property
    def iban(self):
        """رقم الآيبان (مفكوك التشفير)"""
        if self._iban:
            return self.decrypt_field(self._iban)
        return None
    
    @iban.setter
    def iban(self, value):
        """تعيين رقم الآيبان (مشفر)"""
        if value:
            self._iban = self.encrypt_field(str(value))
        else:
            self._iban = None
    
    def validate_data(self):
        """التحقق من صحة بيانات العميل"""
        errors = []
        
        # التحقق من الاسم
        if not self.name or len(self.name.strip()) < 2:
            errors.append('اسم العميل يجب أن يكون حرفين على الأقل')
        
        # التحقق من البريد الإلكتروني
        if self.email:
            email_validation = validate_email_format(self.email)
            if not email_validation['is_valid']:
                errors.append(email_validation['error'])
        
        # التحقق من رقم الهاتف
        if self.phone:
            phone_validation = validate_phone_number(self.phone)
            if not phone_validation['is_valid']:
                errors.append(phone_validation['error'])
        
        # التحقق من الرقم الضريبي
        if self.tax_number and len(self.tax_number) < 10:
            errors.append('الرقم الضريبي يجب أن يكون 10 أرقام على الأقل')
        
        # التحقق من نوع العميل
        if self.customer_type not in self.CUSTOMER_TYPES:
            errors.append('نوع العميل غير صحيح')
        
        # التحقق من الحالة
        if self.status not in self.STATUSES:
            errors.append('حالة العميل غير صحيحة')
        
        return errors
    
    def get_customer_type_display(self):
        """الحصول على نوع العميل للعرض"""
        return self.CUSTOMER_TYPES.get(self.customer_type, self.customer_type)
    
    def get_status_display(self):
        """الحصول على حالة العميل للعرض"""
        return self.STATUSES.get(self.status, self.status)
    
    def get_risk_level_display(self):
        """الحصول على مستوى المخاطر للعرض"""
        return self.RISK_LEVELS.get(self.risk_level, self.risk_level)
    
    def get_verification_status_display(self):
        """الحصول على حالة التحقق للعرض"""
        return self.VERIFICATION_STATUSES.get(self.verification_status, self.verification_status)
    
    def is_active(self):
        """فحص إذا كان العميل نشط"""
        return self.status == 'active'
    
    def is_verified(self):
        """فحص إذا كان العميل محقق"""
        return self.verification_status == 'verified'
    
    def is_high_risk(self):
        """فحص إذا كان العميل عالي المخاطر"""
        return self.risk_level in ['high', 'critical']
    
    def can_purchase(self, amount=0):
        """فحص إمكانية الشراء"""
        if not self.is_active():
            return False, 'العميل غير نشط'
        
        if self.status == 'blacklisted':
            return False, 'العميل محظور'
        
        if amount > 0 and self.credit_limit > 0:
            current_debt = self.get_current_debt()
            if current_debt + amount > self.credit_limit:
                return False, 'تجاوز الحد الائتماني'
        
        return True, 'يمكن الشراء'
    
    def get_current_debt(self):
        """الحصول على الدين الحالي"""
        from app.models.invoice import Invoice
        
        unpaid_invoices = Invoice.query.filter_by(
            customer_name=self.name,
            status='unpaid'
        ).all()
        
        return sum(invoice.total_amount for invoice in unpaid_invoices)
    
    def get_total_paid(self):
        """الحصول على إجمالي المدفوعات"""
        return sum(payment.amount for payment in self.payments if payment.payment_type == 'received')
    
    def get_average_purchase(self):
        """الحصول على متوسط المشتريات"""
        if self.purchase_count > 0:
            return self.total_purchases / self.purchase_count
        return 0.0
    
    def update_purchase_stats(self, amount):
        """تحديث إحصائيات المشتريات"""
        from datetime import datetime
        
        self.total_purchases += amount
        self.purchase_count += 1
        self.last_purchase_date = datetime.utcnow()
        
        # تحديث التقييم بناءً على المشتريات
        if self.total_purchases > 100000:
            self.rating = 5
        elif self.total_purchases > 50000:
            self.rating = 4
        elif self.total_purchases > 10000:
            self.rating = 3
        
        db.session.commit()
    
    def calculate_risk_level(self):
        """حساب مستوى المخاطر تلقائياً"""
        risk_score = 0
        
        # عوامل المخاطر
        if not self.is_verified():
            risk_score += 2
        
        if self.get_current_debt() > self.credit_limit:
            risk_score += 3
        
        if self.purchase_count == 0:
            risk_score += 1
        
        if self.total_purchases < 1000:
            risk_score += 1
        
        # تحديد مستوى المخاطر
        if risk_score >= 5:
            self.risk_level = 'critical'
        elif risk_score >= 3:
            self.risk_level = 'high'
        elif risk_score >= 1:
            self.risk_level = 'medium'
        else:
            self.risk_level = 'low'
        
        return self.risk_level
    
    def to_dict(self, include_sensitive=False):
        """تحويل إلى قاموس مع إخفاء البيانات الحساسة"""
        data = super().to_dict()
        
        # إضافة البيانات المحسوبة
        data['customer_type_display'] = self.get_customer_type_display()
        data['status_display'] = self.get_status_display()
        data['risk_level_display'] = self.get_risk_level_display()
        data['verification_status_display'] = self.get_verification_status_display()
        data['current_debt'] = self.get_current_debt()
        data['total_paid'] = self.get_total_paid()
        data['average_purchase'] = self.get_average_purchase()
        data['is_active'] = self.is_active()
        data['is_verified'] = self.is_verified()
        data['is_high_risk'] = self.is_high_risk()
        
        # إضافة البيانات الحساسة إذا طُلب ذلك
        if include_sensitive:
            data['credit_limit'] = self.credit_limit
            data['bank_account'] = self.bank_account
            data['iban'] = self.iban
        else:
            # إخفاء البيانات الحساسة
            data.pop('_credit_limit', None)
            data.pop('_bank_account', None)
            data.pop('_iban', None)
        
        return data
    
    def __repr__(self):
        return f'<Customer {self.name}>'

# الأحداث التلقائية
@event.listens_for(Customer, 'before_insert')
def calculate_risk_before_insert(mapper, connection, target):
    """حساب مستوى المخاطر قبل الإدراج"""
    target.calculate_risk_level()

@event.listens_for(Customer, 'before_update')
def calculate_risk_before_update(mapper, connection, target):
    """حساب مستوى المخاطر قبل التحديث"""
    target.calculate_risk_level()

@event.listens_for(Customer, 'after_insert')
def log_customer_creation(mapper, connection, target):
    """تسجيل إنشاء عميل جديد"""
    target.log_change('create', {
        'customer_name': target.name,
        'customer_type': target.customer_type,
        'status': target.status
    })

@event.listens_for(Customer, 'after_update')
def log_customer_update(mapper, connection, target):
    """تسجيل تحديث العميل"""
    target.log_change('update', {
        'customer_name': target.name,
        'updated_fields': list(target.__dict__.keys())
    })
