#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نموذج عناصر الفاتورة
Invoice Items Model
"""

from sqlalchemy import Index, event
from sqlalchemy.ext.hybrid import hybrid_property
from app import db
from app.models.base import BaseModel, AuditMixin

class InvoiceItem(BaseModel, AuditMixin):
    """نموذج عناصر الفاتورة"""
    
    __tablename__ = 'invoice_items'
    
    # ربط مع الفاتورة
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoices.id'), nullable=False, index=True)
    
    # ربط مع المنتج (اختياري)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=True, index=True)
    
    # معلومات العنصر
    item_name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    sku = db.Column(db.String(50), nullable=True, index=True)  # رمز المنتج
    
    # الكمية والوحدة
    quantity = db.Column(db.Float, nullable=False, default=1.0)
    unit = db.Column(db.String(20), default='قطعة', nullable=False)
    
    # الأسعار
    unit_price = db.Column(db.Float, nullable=False, default=0.0)
    discount_rate = db.Column(db.Float, default=0.0, nullable=False)  # نسبة الخصم
    discount_amount = db.Column(db.Float, default=0.0, nullable=False)  # مبلغ الخصم
    total_amount = db.Column(db.Float, nullable=False, default=0.0)
    
    # معلومات الضريبة
    tax_rate = db.Column(db.Float, default=15.0, nullable=False)
    tax_amount = db.Column(db.Float, default=0.0, nullable=False)
    tax_inclusive = db.Column(db.Boolean, default=False, nullable=False)  # شامل الضريبة
    
    # ترتيب العنصر في الفاتورة
    sort_order = db.Column(db.Integer, default=0, nullable=False)
    
    # معلومات إضافية
    notes = db.Column(db.Text, nullable=True)
    warranty_period = db.Column(db.Integer, nullable=True)  # فترة الضمان بالأشهر
    
    # العلاقات
    product = db.relationship('Product', backref='invoice_items', lazy='select')
    
    # فهارس محسنة
    __table_args__ = (
        Index('idx_invoice_item_invoice_product', 'invoice_id', 'product_id'),
        Index('idx_invoice_item_sku', 'sku'),
        Index('idx_invoice_item_sort', 'invoice_id', 'sort_order'),
        Index('idx_invoice_item_amount', 'total_amount'),
    )
    
    # الوحدات المدعومة
    UNITS = {
        'قطعة': 'قطعة',
        'كيلو': 'كيلوجرام',
        'جرام': 'جرام',
        'لتر': 'لتر',
        'متر': 'متر',
        'متر مربع': 'متر مربع',
        'متر مكعب': 'متر مكعب',
        'ساعة': 'ساعة',
        'يوم': 'يوم',
        'شهر': 'شهر',
        'سنة': 'سنة',
        'خدمة': 'خدمة',
        'باقة': 'باقة'
    }
    
    @hybrid_property
    def subtotal(self):
        """المجموع الفرعي قبل الخصم والضريبة"""
        return self.quantity * self.unit_price
    
    @hybrid_property
    def net_amount(self):
        """المبلغ الصافي بعد الخصم وقبل الضريبة"""
        return self.subtotal - self.discount_amount
    
    def calculate_amounts(self):
        """حساب جميع المبالغ"""
        # حساب المجموع الفرعي
        subtotal = self.quantity * self.unit_price
        
        # حساب الخصم
        if self.discount_rate > 0:
            self.discount_amount = subtotal * (self.discount_rate / 100)
        else:
            self.discount_amount = 0.0
        
        # المبلغ بعد الخصم
        net_amount = subtotal - self.discount_amount
        
        # حساب الضريبة
        if self.tax_inclusive:
            # السعر شامل الضريبة
            self.tax_amount = net_amount * (self.tax_rate / (100 + self.tax_rate))
            self.total_amount = net_amount
        else:
            # السعر غير شامل الضريبة
            self.tax_amount = net_amount * (self.tax_rate / 100)
            self.total_amount = net_amount + self.tax_amount
    
    def update_from_product(self):
        """تحديث البيانات من المنتج المرتبط"""
        if self.product:
            self.item_name = self.product.name
            self.description = self.product.description
            self.sku = self.product.sku
            self.unit_price = self.product.price
            self.unit = self.product.unit or 'قطعة'
            
            # تحديث الكمية في المخزون
            if self.product.track_inventory:
                self.product.quantity -= self.quantity
                if self.product.quantity < 0:
                    self.product.quantity = 0
    
    def validate_data(self):
        """التحقق من صحة البيانات"""
        errors = []
        
        # التحقق من الاسم
        if not self.item_name or len(self.item_name.strip()) < 2:
            errors.append('اسم العنصر يجب أن يكون حرفين على الأقل')
        
        # التحقق من الكمية
        if self.quantity <= 0:
            errors.append('الكمية يجب أن تكون أكبر من صفر')
        
        # التحقق من السعر
        if self.unit_price < 0:
            errors.append('سعر الوحدة لا يمكن أن يكون سالب')
        
        # التحقق من نسبة الخصم
        if self.discount_rate < 0 or self.discount_rate > 100:
            errors.append('نسبة الخصم يجب أن تكون بين 0 و 100')
        
        # التحقق من نسبة الضريبة
        if self.tax_rate < 0 or self.tax_rate > 100:
            errors.append('نسبة الضريبة يجب أن تكون بين 0 و 100')
        
        # التحقق من الوحدة
        if self.unit not in self.UNITS:
            errors.append('وحدة القياس غير صحيحة')
        
        return errors
    
    def get_unit_display(self):
        """الحصول على وحدة القياس للعرض"""
        return self.UNITS.get(self.unit, self.unit)
    
    def get_formatted_quantity(self):
        """تنسيق الكمية للعرض"""
        if self.quantity == int(self.quantity):
            return str(int(self.quantity))
        else:
            return f"{self.quantity:.2f}"
    
    def get_formatted_price(self):
        """تنسيق السعر للعرض"""
        return f"{self.unit_price:,.2f}"
    
    def get_formatted_total(self):
        """تنسيق المجموع للعرض"""
        return f"{self.total_amount:,.2f}"
    
    def clone(self):
        """إنشاء نسخة من العنصر"""
        return InvoiceItem(
            item_name=self.item_name,
            description=self.description,
            sku=self.sku,
            quantity=self.quantity,
            unit=self.unit,
            unit_price=self.unit_price,
            discount_rate=self.discount_rate,
            tax_rate=self.tax_rate,
            tax_inclusive=self.tax_inclusive,
            notes=self.notes,
            warranty_period=self.warranty_period,
            product_id=self.product_id
        )
    
    def to_dict(self):
        """تحويل إلى قاموس"""
        data = super().to_dict()
        
        # إضافة البيانات المحسوبة
        data['subtotal'] = self.subtotal
        data['net_amount'] = self.net_amount
        data['unit_display'] = self.get_unit_display()
        data['formatted_quantity'] = self.get_formatted_quantity()
        data['formatted_price'] = self.get_formatted_price()
        data['formatted_total'] = self.get_formatted_total()
        
        # إضافة معلومات المنتج إذا كان موجود
        if self.product:
            data['product_name'] = self.product.name
            data['product_available_quantity'] = self.product.quantity
        
        return data
    
    def __repr__(self):
        return f'<InvoiceItem {self.item_name} x {self.quantity}>'

# الأحداث التلقائية
@event.listens_for(InvoiceItem, 'before_insert')
def calculate_amounts_before_insert(mapper, connection, target):
    """حساب المبالغ قبل الإدراج"""
    target.calculate_amounts()

@event.listens_for(InvoiceItem, 'before_update')
def calculate_amounts_before_update(mapper, connection, target):
    """حساب المبالغ قبل التحديث"""
    target.calculate_amounts()

@event.listens_for(InvoiceItem, 'after_insert')
def update_product_inventory_after_insert(mapper, connection, target):
    """تحديث المخزون بعد الإدراج"""
    if target.product and target.product.track_inventory:
        target.product.quantity -= target.quantity
        if target.product.quantity < 0:
            target.product.quantity = 0

@event.listens_for(InvoiceItem, 'after_update')
def update_product_inventory_after_update(mapper, connection, target):
    """تحديث المخزون بعد التحديث"""
    # هذا يحتاج معالجة أكثر تعقيداً لتتبع التغييرات في الكمية
    pass

@event.listens_for(InvoiceItem, 'after_delete')
def restore_product_inventory_after_delete(mapper, connection, target):
    """استعادة المخزون بعد الحذف"""
    if target.product and target.product.track_inventory:
        target.product.quantity += target.quantity

@event.listens_for(InvoiceItem, 'after_insert')
def log_item_creation(mapper, connection, target):
    """تسجيل إضافة عنصر جديد"""
    target.log_change('create', {
        'item_name': target.item_name,
        'quantity': target.quantity,
        'unit_price': target.unit_price,
        'total_amount': target.total_amount,
        'invoice_id': target.invoice_id
    })

@event.listens_for(InvoiceItem, 'after_update')
def log_item_update(mapper, connection, target):
    """تسجيل تحديث العنصر"""
    target.log_change('update', {
        'item_name': target.item_name,
        'quantity': target.quantity,
        'total_amount': target.total_amount
    })

@event.listens_for(InvoiceItem, 'after_delete')
def log_item_deletion(mapper, connection, target):
    """تسجيل حذف العنصر"""
    target.log_change('delete', {
        'item_name': target.item_name,
        'quantity': target.quantity,
        'total_amount': target.total_amount,
        'invoice_id': target.invoice_id
    })
