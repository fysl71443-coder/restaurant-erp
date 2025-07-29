#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نموذج الفواتير المحسن
Enhanced Invoice Model
"""

from datetime import datetime, timedelta
from sqlalchemy import Index, event, func
from sqlalchemy.ext.hybrid import hybrid_property
from app import db
from app.models.base import BaseModel, AuditMixin, EncryptedMixin

class Invoice(BaseModel, AuditMixin, EncryptedMixin):
    """نموذج الفواتير مع ميزات أمان ومالية متقدمة"""
    
    __tablename__ = 'invoices'
    
    # معلومات الفاتورة الأساسية
    invoice_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    due_date = db.Column(db.DateTime, nullable=True, index=True)
    
    # معلومات العميل
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=True, index=True)
    customer_name = db.Column(db.String(100), nullable=False, index=True)
    customer_email = db.Column(db.String(120), nullable=True)
    customer_phone = db.Column(db.String(20), nullable=True)
    customer_address = db.Column(db.Text, nullable=True)
    
    # المبالغ المالية
    subtotal = db.Column(db.Float, default=0.0, nullable=False)
    tax_rate = db.Column(db.Float, default=15.0, nullable=False)  # نسبة الضريبة
    tax_amount = db.Column(db.Float, default=0.0, nullable=False)
    discount_rate = db.Column(db.Float, default=0.0, nullable=False)
    discount_amount = db.Column(db.Float, default=0.0, nullable=False)
    total_amount = db.Column(db.Float, default=0.0, nullable=False, index=True)
    paid_amount = db.Column(db.Float, default=0.0, nullable=False)
    remaining_amount = db.Column(db.Float, default=0.0, nullable=False, index=True)
    
    # معلومات الحالة
    status = db.Column(db.String(20), default='draft', nullable=False, index=True)
    payment_status = db.Column(db.String(20), default='unpaid', nullable=False, index=True)
    invoice_type = db.Column(db.String(20), default='sales', nullable=False, index=True)
    
    # معلومات إضافية
    notes = db.Column(db.Text, nullable=True)
    terms_conditions = db.Column(db.Text, nullable=True)
    reference_number = db.Column(db.String(50), nullable=True, index=True)
    po_number = db.Column(db.String(50), nullable=True)  # رقم أمر الشراء
    
    # معلومات الشحن
    shipping_address = db.Column(db.Text, nullable=True)
    shipping_cost = db.Column(db.Float, default=0.0, nullable=False)
    shipping_method = db.Column(db.String(50), nullable=True)
    
    # معلومات التوقيع الرقمي (مشفرة)
    _digital_signature = db.Column('digital_signature', db.Text, nullable=True)
    signature_timestamp = db.Column(db.DateTime, nullable=True)
    signature_valid = db.Column(db.Boolean, default=False, nullable=False)
    
    # معلومات المراجعة
    reviewed_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    reviewed_at = db.Column(db.DateTime, nullable=True)
    approved_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    approved_at = db.Column(db.DateTime, nullable=True)
    
    # معلومات الطباعة والإرسال
    printed_count = db.Column(db.Integer, default=0, nullable=False)
    last_printed_at = db.Column(db.DateTime, nullable=True)
    emailed_count = db.Column(db.Integer, default=0, nullable=False)
    last_emailed_at = db.Column(db.DateTime, nullable=True)
    
    # معلومات العملة
    currency = db.Column(db.String(3), default='SAR', nullable=False)
    exchange_rate = db.Column(db.Float, default=1.0, nullable=False)
    
    # العلاقات
    customer = db.relationship('Customer', backref='customer_invoices', lazy='select')
    payments = db.relationship('Payment', backref='invoice_rel', lazy='dynamic', cascade='all, delete-orphan')
    invoice_items = db.relationship('InvoiceItem', backref='invoice', lazy='dynamic', cascade='all, delete-orphan')
    reviewed_by = db.relationship('User', foreign_keys=[reviewed_by_id], lazy='select')
    approved_by = db.relationship('User', foreign_keys=[approved_by_id], lazy='select')
    
    # فهارس محسنة
    __table_args__ = (
        Index('idx_invoice_number_date', 'invoice_number', 'date'),
        Index('idx_invoice_customer_status', 'customer_name', 'status'),
        Index('idx_invoice_date_status', 'date', 'status'),
        Index('idx_invoice_amount_status', 'total_amount', 'payment_status'),
        Index('idx_invoice_due_date_status', 'due_date', 'payment_status'),
        Index('idx_invoice_type_date', 'invoice_type', 'date'),
        Index('idx_invoice_customer_date', 'customer_id', 'date'),
        Index('idx_invoice_reference', 'reference_number', 'po_number'),
    )
    
    # حالات الفاتورة
    STATUSES = {
        'draft': 'مسودة',
        'pending': 'في الانتظار',
        'sent': 'مرسلة',
        'viewed': 'تم الاطلاع',
        'approved': 'معتمدة',
        'rejected': 'مرفوضة',
        'cancelled': 'ملغية',
        'completed': 'مكتملة'
    }
    
    # حالات الدفع
    PAYMENT_STATUSES = {
        'unpaid': 'غير مدفوعة',
        'partial': 'مدفوعة جزئياً',
        'paid': 'مدفوعة',
        'overpaid': 'مدفوعة زائد',
        'refunded': 'مسترد'
    }
    
    # أنواع الفواتير
    INVOICE_TYPES = {
        'sales': 'مبيعات',
        'service': 'خدمات',
        'rental': 'إيجار',
        'subscription': 'اشتراك',
        'maintenance': 'صيانة',
        'consulting': 'استشارات'
    }
    
    # العملات المدعومة
    CURRENCIES = {
        'SAR': 'ريال سعودي',
        'USD': 'دولار أمريكي',
        'EUR': 'يورو',
        'GBP': 'جنيه إسترليني',
        'AED': 'درهم إماراتي'
    }
    
    @hybrid_property
    def digital_signature(self):
        """التوقيع الرقمي (مفكوك التشفير)"""
        if self._digital_signature:
            return self.decrypt_field(self._digital_signature)
        return None
    
    @digital_signature.setter
    def digital_signature(self, value):
        """تعيين التوقيع الرقمي (مشفر)"""
        if value:
            self._digital_signature = self.encrypt_field(str(value))
            self.signature_timestamp = datetime.utcnow()
        else:
            self._digital_signature = None
            self.signature_timestamp = None
    
    def generate_invoice_number(self):
        """إنشاء رقم فاتورة تلقائي"""
        if not self.invoice_number:
            year = datetime.now().year
            month = datetime.now().month
            
            # البحث عن آخر رقم فاتورة في الشهر
            last_invoice = Invoice.query.filter(
                func.extract('year', Invoice.date) == year,
                func.extract('month', Invoice.date) == month
            ).order_by(Invoice.id.desc()).first()
            
            if last_invoice and last_invoice.invoice_number:
                try:
                    last_number = int(last_invoice.invoice_number.split('-')[-1])
                    next_number = last_number + 1
                except:
                    next_number = 1
            else:
                next_number = 1
            
            self.invoice_number = f"INV-{year}{month:02d}-{next_number:06d}"
    
    def calculate_amounts(self):
        """حساب المبالغ تلقائياً"""
        # حساب المجموع الفرعي من العناصر
        self.subtotal = sum(item.total_amount for item in self.invoice_items)
        
        # حساب الخصم
        if self.discount_rate > 0:
            self.discount_amount = self.subtotal * (self.discount_rate / 100)
        
        # حساب الضريبة
        taxable_amount = self.subtotal - self.discount_amount
        self.tax_amount = taxable_amount * (self.tax_rate / 100)
        
        # حساب المجموع الكلي
        self.total_amount = taxable_amount + self.tax_amount + self.shipping_cost
        
        # حساب المبلغ المتبقي
        self.remaining_amount = self.total_amount - self.paid_amount
        
        # تحديث حالة الدفع
        self.update_payment_status()
    
    def update_payment_status(self):
        """تحديث حالة الدفع"""
        if self.paid_amount <= 0:
            self.payment_status = 'unpaid'
        elif self.paid_amount >= self.total_amount:
            if self.paid_amount > self.total_amount:
                self.payment_status = 'overpaid'
            else:
                self.payment_status = 'paid'
        else:
            self.payment_status = 'partial'
    
    def set_due_date(self, days=30):
        """تعيين تاريخ الاستحقاق"""
        if not self.due_date:
            self.due_date = self.date + timedelta(days=days)
    
    def is_overdue(self):
        """فحص إذا كانت الفاتورة متأخرة"""
        if self.due_date and self.payment_status != 'paid':
            return datetime.utcnow() > self.due_date
        return False
    
    def days_overdue(self):
        """عدد الأيام المتأخرة"""
        if self.is_overdue():
            return (datetime.utcnow() - self.due_date).days
        return 0
    
    def can_be_edited(self):
        """فحص إمكانية التعديل"""
        return self.status in ['draft', 'pending']
    
    def can_be_deleted(self):
        """فحص إمكانية الحذف"""
        return self.status == 'draft' and self.paid_amount == 0
    
    def can_be_sent(self):
        """فحص إمكانية الإرسال"""
        return self.status in ['draft', 'pending'] and self.total_amount > 0
    
    def mark_as_sent(self):
        """تحديد كمرسلة"""
        if self.can_be_sent():
            self.status = 'sent'
            self.emailed_count += 1
            self.last_emailed_at = datetime.utcnow()
            db.session.commit()
    
    def mark_as_printed(self):
        """تحديد كمطبوعة"""
        self.printed_count += 1
        self.last_printed_at = datetime.utcnow()
        db.session.commit()
    
    def approve(self, user_id):
        """اعتماد الفاتورة"""
        if self.status in ['pending', 'sent']:
            self.status = 'approved'
            self.approved_by_id = user_id
            self.approved_at = datetime.utcnow()
            db.session.commit()
            
            # تسجيل الاعتماد
            self.log_change('approve', {
                'approved_by': user_id,
                'invoice_number': self.invoice_number,
                'total_amount': self.total_amount
            })
    
    def reject(self, user_id, reason=None):
        """رفض الفاتورة"""
        if self.status in ['pending', 'sent']:
            self.status = 'rejected'
            self.reviewed_by_id = user_id
            self.reviewed_at = datetime.utcnow()
            
            if reason:
                self.notes = f"{self.notes or ''}\nسبب الرفض: {reason}"
            
            db.session.commit()
            
            # تسجيل الرفض
            self.log_change('reject', {
                'rejected_by': user_id,
                'reason': reason,
                'invoice_number': self.invoice_number
            })
    
    def cancel(self, user_id, reason=None):
        """إلغاء الفاتورة"""
        if self.status not in ['cancelled', 'completed']:
            self.status = 'cancelled'
            
            if reason:
                self.notes = f"{self.notes or ''}\nسبب الإلغاء: {reason}"
            
            db.session.commit()
            
            # تسجيل الإلغاء
            self.log_change('cancel', {
                'cancelled_by': user_id,
                'reason': reason,
                'invoice_number': self.invoice_number
            })
    
    def add_payment(self, amount, payment_method='cash', reference=None):
        """إضافة دفعة"""
        from app.models.payment import Payment
        
        payment = Payment(
            invoice_id=self.id,
            amount=amount,
            payment_method=payment_method,
            reference_number=reference,
            payment_type='received',
            date=datetime.utcnow()
        )
        
        db.session.add(payment)
        
        # تحديث المبلغ المدفوع
        self.paid_amount += amount
        self.calculate_amounts()
        
        # إذا تم دفع المبلغ كاملاً، تحديث الحالة
        if self.payment_status == 'paid':
            self.status = 'completed'
        
        db.session.commit()
        
        # تسجيل الدفعة
        self.log_change('payment_received', {
            'amount': amount,
            'payment_method': payment_method,
            'invoice_number': self.invoice_number
        })
        
        return payment
    
    def get_status_display(self):
        """الحصول على حالة الفاتورة للعرض"""
        return self.STATUSES.get(self.status, self.status)
    
    def get_payment_status_display(self):
        """الحصول على حالة الدفع للعرض"""
        return self.PAYMENT_STATUSES.get(self.payment_status, self.payment_status)
    
    def get_invoice_type_display(self):
        """الحصول على نوع الفاتورة للعرض"""
        return self.INVOICE_TYPES.get(self.invoice_type, self.invoice_type)
    
    def get_currency_display(self):
        """الحصول على العملة للعرض"""
        return self.CURRENCIES.get(self.currency, self.currency)
    
    def to_dict(self, include_items=False):
        """تحويل إلى قاموس"""
        data = super().to_dict()
        
        # إضافة البيانات المحسوبة
        data['status_display'] = self.get_status_display()
        data['payment_status_display'] = self.get_payment_status_display()
        data['invoice_type_display'] = self.get_invoice_type_display()
        data['currency_display'] = self.get_currency_display()
        data['is_overdue'] = self.is_overdue()
        data['days_overdue'] = self.days_overdue()
        data['can_be_edited'] = self.can_be_edited()
        data['can_be_deleted'] = self.can_be_deleted()
        data['can_be_sent'] = self.can_be_sent()
        
        # إضافة عناصر الفاتورة إذا طُلب ذلك
        if include_items:
            data['items'] = [item.to_dict() for item in self.invoice_items]
        
        # إخفاء التوقيع الرقمي المشفر
        data.pop('_digital_signature', None)
        
        return data
    
    def __repr__(self):
        return f'<Invoice {self.invoice_number}>'

# الأحداث التلقائية
@event.listens_for(Invoice, 'before_insert')
def generate_invoice_number_before_insert(mapper, connection, target):
    """إنشاء رقم فاتورة قبل الإدراج"""
    target.generate_invoice_number()
    target.set_due_date()
    target.calculate_amounts()

@event.listens_for(Invoice, 'before_update')
def calculate_amounts_before_update(mapper, connection, target):
    """حساب المبالغ قبل التحديث"""
    target.calculate_amounts()

@event.listens_for(Invoice, 'after_insert')
def log_invoice_creation(mapper, connection, target):
    """تسجيل إنشاء فاتورة جديدة"""
    target.log_change('create', {
        'invoice_number': target.invoice_number,
        'customer_name': target.customer_name,
        'total_amount': target.total_amount,
        'invoice_type': target.invoice_type
    })

@event.listens_for(Invoice, 'after_update')
def log_invoice_update(mapper, connection, target):
    """تسجيل تحديث الفاتورة"""
    target.log_change('update', {
        'invoice_number': target.invoice_number,
        'status': target.status,
        'payment_status': target.payment_status
    })
