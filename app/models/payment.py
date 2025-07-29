#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نموذج المدفوعات المحسن
Enhanced Payment Model
"""

from datetime import datetime
from sqlalchemy import Index, event
from sqlalchemy.ext.hybrid import hybrid_property
from app import db
from app.models.base import BaseModel, AuditMixin, EncryptedMixin

class Payment(BaseModel, AuditMixin, EncryptedMixin):
    """نموذج المدفوعات مع ميزات أمان متقدمة"""
    
    __tablename__ = 'payments'
    
    # معلومات الدفعة الأساسية
    payment_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    amount = db.Column(db.Float, nullable=False, index=True)
    
    # نوع الدفعة
    payment_type = db.Column(db.String(20), nullable=False, index=True)  # received, paid
    payment_method = db.Column(db.String(30), nullable=False, index=True)
    
    # ربط مع الفاتورة (اختياري)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoices.id'), nullable=True, index=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=True, index=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=True, index=True)
    
    # معلومات الدفع
    reference_number = db.Column(db.String(100), nullable=True, index=True)
    bank_name = db.Column(db.String(100), nullable=True)
    _account_number = db.Column('account_number', db.Text, nullable=True)  # مشفر
    check_number = db.Column(db.String(50), nullable=True)
    check_date = db.Column(db.DateTime, nullable=True)
    
    # معلومات البطاقة الائتمانية (مشفرة)
    _card_last_four = db.Column('card_last_four', db.Text, nullable=True)
    _card_type = db.Column('card_type', db.Text, nullable=True)
    _transaction_id = db.Column('transaction_id', db.Text, nullable=True)
    
    # حالة الدفعة
    status = db.Column(db.String(20), default='pending', nullable=False, index=True)
    verification_status = db.Column(db.String(20), default='unverified', nullable=False)
    
    # معلومات العملة
    currency = db.Column(db.String(3), default='SAR', nullable=False)
    exchange_rate = db.Column(db.Float, default=1.0, nullable=False)
    amount_in_base_currency = db.Column(db.Float, nullable=False)
    
    # معلومات إضافية
    description = db.Column(db.Text, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    receipt_url = db.Column(db.String(255), nullable=True)
    
    # معلومات المعالجة
    processed_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    processed_at = db.Column(db.DateTime, nullable=True)
    verified_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    verified_at = db.Column(db.DateTime, nullable=True)
    
    # معلومات الرسوم
    processing_fee = db.Column(db.Float, default=0.0, nullable=False)
    gateway_fee = db.Column(db.Float, default=0.0, nullable=False)
    net_amount = db.Column(db.Float, nullable=False)
    
    # العلاقات
    customer = db.relationship('Customer', backref='customer_payments', lazy='select')
    supplier = db.relationship('Supplier', backref='supplier_payments', lazy='select')
    processed_by = db.relationship('User', foreign_keys=[processed_by_id], lazy='select')
    verified_by = db.relationship('User', foreign_keys=[verified_by_id], lazy='select')
    
    # فهارس محسنة
    __table_args__ = (
        Index('idx_payment_number_date', 'payment_number', 'date'),
        Index('idx_payment_type_method', 'payment_type', 'payment_method'),
        Index('idx_payment_status_date', 'status', 'date'),
        Index('idx_payment_amount_currency', 'amount', 'currency'),
        Index('idx_payment_reference', 'reference_number'),
        Index('idx_payment_customer_date', 'customer_id', 'date'),
        Index('idx_payment_supplier_date', 'supplier_id', 'date'),
        Index('idx_payment_invoice_date', 'invoice_id', 'date'),
    )
    
    # أنواع الدفعات
    PAYMENT_TYPES = {
        'received': 'مقبوض',
        'paid': 'مدفوع',
        'refund': 'مسترد',
        'adjustment': 'تسوية'
    }
    
    # طرق الدفع
    PAYMENT_METHODS = {
        'cash': 'نقد',
        'bank_transfer': 'تحويل بنكي',
        'check': 'شيك',
        'credit_card': 'بطاقة ائتمان',
        'debit_card': 'بطاقة خصم',
        'online_payment': 'دفع إلكتروني',
        'mobile_payment': 'دفع محمول',
        'cryptocurrency': 'عملة رقمية'
    }
    
    # حالات الدفعة
    STATUSES = {
        'pending': 'في الانتظار',
        'processing': 'قيد المعالجة',
        'completed': 'مكتملة',
        'failed': 'فاشلة',
        'cancelled': 'ملغية',
        'refunded': 'مسترد'
    }
    
    # حالات التحقق
    VERIFICATION_STATUSES = {
        'unverified': 'غير محقق',
        'verified': 'محقق',
        'rejected': 'مرفوض',
        'suspicious': 'مشبوه'
    }
    
    @hybrid_property
    def account_number(self):
        """رقم الحساب (مفكوك التشفير)"""
        if self._account_number:
            return self.decrypt_field(self._account_number)
        return None
    
    @account_number.setter
    def account_number(self, value):
        """تعيين رقم الحساب (مشفر)"""
        if value:
            self._account_number = self.encrypt_field(str(value))
        else:
            self._account_number = None
    
    @hybrid_property
    def card_last_four(self):
        """آخر أربعة أرقام من البطاقة (مفكوك التشفير)"""
        if self._card_last_four:
            return self.decrypt_field(self._card_last_four)
        return None
    
    @card_last_four.setter
    def card_last_four(self, value):
        """تعيين آخر أربعة أرقام من البطاقة (مشفر)"""
        if value:
            self._card_last_four = self.encrypt_field(str(value))
        else:
            self._card_last_four = None
    
    @hybrid_property
    def card_type(self):
        """نوع البطاقة (مفكوك التشفير)"""
        if self._card_type:
            return self.decrypt_field(self._card_type)
        return None
    
    @card_type.setter
    def card_type(self, value):
        """تعيين نوع البطاقة (مشفر)"""
        if value:
            self._card_type = self.encrypt_field(str(value))
        else:
            self._card_type = None
    
    @hybrid_property
    def transaction_id(self):
        """معرف المعاملة (مفكوك التشفير)"""
        if self._transaction_id:
            return self.decrypt_field(self._transaction_id)
        return None
    
    @transaction_id.setter
    def transaction_id(self, value):
        """تعيين معرف المعاملة (مشفر)"""
        if value:
            self._transaction_id = self.encrypt_field(str(value))
        else:
            self._transaction_id = None
    
    def generate_payment_number(self):
        """إنشاء رقم دفعة تلقائي"""
        if not self.payment_number:
            year = datetime.now().year
            month = datetime.now().month
            
            # البحث عن آخر رقم دفعة في الشهر
            last_payment = Payment.query.filter(
                Payment.date >= datetime(year, month, 1)
            ).order_by(Payment.id.desc()).first()
            
            if last_payment and last_payment.payment_number:
                try:
                    last_number = int(last_payment.payment_number.split('-')[-1])
                    next_number = last_number + 1
                except:
                    next_number = 1
            else:
                next_number = 1
            
            prefix = 'PAY' if self.payment_type == 'paid' else 'REC'
            self.payment_number = f"{prefix}-{year}{month:02d}-{next_number:06d}"
    
    def calculate_net_amount(self):
        """حساب المبلغ الصافي"""
        self.net_amount = self.amount - self.processing_fee - self.gateway_fee
        
        # حساب المبلغ بالعملة الأساسية
        self.amount_in_base_currency = self.amount * self.exchange_rate
    
    def validate_data(self):
        """التحقق من صحة البيانات"""
        errors = []
        
        # التحقق من المبلغ
        if self.amount <= 0:
            errors.append('المبلغ يجب أن يكون أكبر من صفر')
        
        # التحقق من نوع الدفعة
        if self.payment_type not in self.PAYMENT_TYPES:
            errors.append('نوع الدفعة غير صحيح')
        
        # التحقق من طريقة الدفع
        if self.payment_method not in self.PAYMENT_METHODS:
            errors.append('طريقة الدفع غير صحيحة')
        
        # التحقق من الحالة
        if self.status not in self.STATUSES:
            errors.append('حالة الدفعة غير صحيحة')
        
        # التحقق من معدل الصرف
        if self.exchange_rate <= 0:
            errors.append('معدل الصرف يجب أن يكون أكبر من صفر')
        
        # التحقق من الشيك
        if self.payment_method == 'check':
            if not self.check_number:
                errors.append('رقم الشيك مطلوب')
            if not self.bank_name:
                errors.append('اسم البنك مطلوب')
        
        # التحقق من التحويل البنكي
        if self.payment_method == 'bank_transfer':
            if not self.reference_number:
                errors.append('رقم المرجع مطلوب للتحويل البنكي')
        
        return errors
    
    def process(self, user_id):
        """معالجة الدفعة"""
        if self.status == 'pending':
            self.status = 'processing'
            self.processed_by_id = user_id
            self.processed_at = datetime.utcnow()
            
            # محاكاة معالجة الدفع
            # في التطبيق الحقيقي، هنا سيتم التكامل مع بوابة الدفع
            
            self.status = 'completed'
            db.session.commit()
            
            # تسجيل المعالجة
            self.log_change('process', {
                'processed_by': user_id,
                'payment_number': self.payment_number,
                'amount': self.amount
            })
    
    def verify(self, user_id, verification_status='verified'):
        """التحقق من الدفعة"""
        self.verification_status = verification_status
        self.verified_by_id = user_id
        self.verified_at = datetime.utcnow()
        db.session.commit()
        
        # تسجيل التحقق
        self.log_change('verify', {
            'verified_by': user_id,
            'verification_status': verification_status,
            'payment_number': self.payment_number
        })
    
    def cancel(self, user_id, reason=None):
        """إلغاء الدفعة"""
        if self.status in ['pending', 'processing']:
            self.status = 'cancelled'
            
            if reason:
                self.notes = f"{self.notes or ''}\nسبب الإلغاء: {reason}"
            
            db.session.commit()
            
            # تسجيل الإلغاء
            self.log_change('cancel', {
                'cancelled_by': user_id,
                'reason': reason,
                'payment_number': self.payment_number
            })
    
    def refund(self, amount=None, reason=None):
        """استرداد الدفعة"""
        if self.status == 'completed':
            refund_amount = amount or self.amount
            
            # إنشاء دفعة استرداد جديدة
            refund_payment = Payment(
                payment_type='refund',
                payment_method=self.payment_method,
                amount=refund_amount,
                currency=self.currency,
                exchange_rate=self.exchange_rate,
                reference_number=f"REFUND-{self.payment_number}",
                description=f"استرداد للدفعة {self.payment_number}",
                notes=reason,
                customer_id=self.customer_id,
                supplier_id=self.supplier_id,
                invoice_id=self.invoice_id
            )
            
            db.session.add(refund_payment)
            
            # تحديث حالة الدفعة الأصلية
            if refund_amount >= self.amount:
                self.status = 'refunded'
            
            db.session.commit()
            
            # تسجيل الاسترداد
            self.log_change('refund', {
                'refund_amount': refund_amount,
                'reason': reason,
                'payment_number': self.payment_number
            })
            
            return refund_payment
    
    def get_payment_type_display(self):
        """الحصول على نوع الدفعة للعرض"""
        return self.PAYMENT_TYPES.get(self.payment_type, self.payment_type)
    
    def get_payment_method_display(self):
        """الحصول على طريقة الدفع للعرض"""
        return self.PAYMENT_METHODS.get(self.payment_method, self.payment_method)
    
    def get_status_display(self):
        """الحصول على حالة الدفعة للعرض"""
        return self.STATUSES.get(self.status, self.status)
    
    def get_verification_status_display(self):
        """الحصول على حالة التحقق للعرض"""
        return self.VERIFICATION_STATUSES.get(self.verification_status, self.verification_status)
    
    def is_completed(self):
        """فحص إذا كانت الدفعة مكتملة"""
        return self.status == 'completed'
    
    def is_verified(self):
        """فحص إذا كانت الدفعة محققة"""
        return self.verification_status == 'verified'
    
    def can_be_processed(self):
        """فحص إمكانية المعالجة"""
        return self.status == 'pending'
    
    def can_be_cancelled(self):
        """فحص إمكانية الإلغاء"""
        return self.status in ['pending', 'processing']
    
    def can_be_refunded(self):
        """فحص إمكانية الاسترداد"""
        return self.status == 'completed' and self.payment_type in ['received', 'paid']
    
    def to_dict(self, include_sensitive=False):
        """تحويل إلى قاموس مع إخفاء البيانات الحساسة"""
        data = super().to_dict()
        
        # إضافة البيانات المحسوبة
        data['payment_type_display'] = self.get_payment_type_display()
        data['payment_method_display'] = self.get_payment_method_display()
        data['status_display'] = self.get_status_display()
        data['verification_status_display'] = self.get_verification_status_display()
        data['is_completed'] = self.is_completed()
        data['is_verified'] = self.is_verified()
        data['can_be_processed'] = self.can_be_processed()
        data['can_be_cancelled'] = self.can_be_cancelled()
        data['can_be_refunded'] = self.can_be_refunded()
        
        # إضافة البيانات الحساسة إذا طُلب ذلك
        if include_sensitive:
            data['account_number'] = self.account_number
            data['card_last_four'] = self.card_last_four
            data['card_type'] = self.card_type
            data['transaction_id'] = self.transaction_id
        else:
            # إخفاء البيانات الحساسة
            data.pop('_account_number', None)
            data.pop('_card_last_four', None)
            data.pop('_card_type', None)
            data.pop('_transaction_id', None)
        
        return data
    
    def __repr__(self):
        return f'<Payment {self.payment_number}>'

# الأحداث التلقائية
@event.listens_for(Payment, 'before_insert')
def generate_payment_number_before_insert(mapper, connection, target):
    """إنشاء رقم دفعة قبل الإدراج"""
    target.generate_payment_number()
    target.calculate_net_amount()

@event.listens_for(Payment, 'before_update')
def calculate_net_amount_before_update(mapper, connection, target):
    """حساب المبلغ الصافي قبل التحديث"""
    target.calculate_net_amount()

@event.listens_for(Payment, 'after_insert')
def log_payment_creation(mapper, connection, target):
    """تسجيل إنشاء دفعة جديدة"""
    target.log_change('create', {
        'payment_number': target.payment_number,
        'payment_type': target.payment_type,
        'payment_method': target.payment_method,
        'amount': target.amount,
        'currency': target.currency
    })

@event.listens_for(Payment, 'after_update')
def log_payment_update(mapper, connection, target):
    """تسجيل تحديث الدفعة"""
    target.log_change('update', {
        'payment_number': target.payment_number,
        'status': target.status,
        'verification_status': target.verification_status
    })
