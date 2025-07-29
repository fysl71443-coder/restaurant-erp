#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
إنشاء بيانات تجريبية للفواتير
Create Sample Invoices Data
"""

from flask import Flask
from database import db, init_db, Customer, Invoice, Supplier, PurchaseInvoice, Payment
from datetime import datetime, timedelta
import random

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///accounting_system.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key-here'

init_db(app)

def create_sample_data():
    """إنشاء بيانات تجريبية للفواتير"""
    
    print("🔄 بدء إنشاء البيانات التجريبية...")
    
    with app.app_context():
        try:
            # إنشاء عملاء تجريبيين
            customers_data = [
                {'name': 'شركة الرياض للتجارة', 'email': 'riyadh@company.com', 'phone': '0112345678'},
                {'name': 'مؤسسة جدة التجارية', 'email': 'jeddah@company.com', 'phone': '0123456789'},
                {'name': 'شركة الدمام للصناعات', 'email': 'dammam@company.com', 'phone': '0134567890'},
                {'name': 'مكتب الخبر للاستشارات', 'email': 'khobar@company.com', 'phone': '0145678901'},
                {'name': 'شركة المدينة للخدمات', 'email': 'madinah@company.com', 'phone': '0156789012'}
            ]
            
            print("👥 إنشاء العملاء...")
            for customer_data in customers_data:
                existing_customer = Customer.query.filter_by(name=customer_data['name']).first()
                if not existing_customer:
                    customer = Customer(**customer_data)
                    db.session.add(customer)
            
            db.session.commit()
            print(f"✅ تم إنشاء {len(customers_data)} عميل")
            
            # إنشاء موردين تجريبيين
            suppliers_data = [
                {'name': 'مورد الرياض', 'contact_info': 'أحمد محمد - 0112345678'},
                {'name': 'مورد جدة', 'contact_info': 'محمد أحمد - 0123456789'},
                {'name': 'مورد الدمام', 'contact_info': 'سعد علي - 0134567890'}
            ]
            
            print("🏭 إنشاء الموردين...")
            for supplier_data in suppliers_data:
                existing_supplier = Supplier.query.filter_by(name=supplier_data['name']).first()
                if not existing_supplier:
                    supplier = Supplier(**supplier_data)
                    db.session.add(supplier)
            
            db.session.commit()
            print(f"✅ تم إنشاء {len(suppliers_data)} مورد")
            
            # إنشاء فواتير مبيعات تجريبية
            print("🛍️ إنشاء فواتير المبيعات...")
            customers = Customer.query.all()
            
            for i in range(10):
                customer = random.choice(customers)
                invoice_date = datetime.now() - timedelta(days=random.randint(1, 30))
                subtotal = random.uniform(1000, 10000)
                tax_rate = 0.15  # ضريبة القيمة المضافة 15%
                tax_amount = subtotal * tax_rate
                total_amount = subtotal + tax_amount
                
                invoice = Invoice(
                    customer_name=customer.name,
                    customer_id=customer.id,
                    invoice_number=f"INV-{2025}{i+1:04d}",
                    date=invoice_date,
                    subtotal=round(subtotal, 2),
                    tax_amount=round(tax_amount, 2),
                    total_amount=round(total_amount, 2),
                    status=random.choice(['معلقة', 'مدفوعة', 'متأخرة']),
                    invoice_type='sales'
                )
                db.session.add(invoice)
            
            db.session.commit()
            print("✅ تم إنشاء 10 فواتير مبيعات")
            
            # إنشاء فواتير مشتريات تجريبية
            print("🛒 إنشاء فواتير المشتريات...")
            suppliers = Supplier.query.all()
            
            for i in range(8):
                supplier = random.choice(suppliers)
                invoice_date = datetime.now() - timedelta(days=random.randint(1, 30))
                subtotal = random.uniform(2000, 15000)
                tax_rate = 0.15
                tax_amount = subtotal * tax_rate
                total_amount = subtotal + tax_amount
                
                purchase_invoice = PurchaseInvoice(
                    supplier_name=supplier.name,
                    date=invoice_date,
                    subtotal=round(subtotal, 2),
                    tax_amount=round(tax_amount, 2),
                    total_amount=round(total_amount, 2),
                    status=random.choice(['معلقة', 'مدفوعة', 'متأخرة'])
                )
                db.session.add(purchase_invoice)
            
            db.session.commit()
            print("✅ تم إنشاء 8 فواتير مشتريات")
            
            # إنشاء مدفوعات تجريبية
            print("💰 إنشاء المدفوعات...")
            invoices = Invoice.query.all()
            
            for i in range(6):
                invoice = random.choice(invoices)
                payment_date = datetime.now() - timedelta(days=random.randint(1, 20))
                amount = random.uniform(500, invoice.total_amount)
                
                payment = Payment(
                    payment_reference=f"PAY-{2025}{i+1:04d}",
                    amount=round(amount, 2),
                    date=payment_date,
                    payment_method=random.choice(['نقدي', 'تحويل بنكي', 'شيك', 'بطاقة ائتمان']),
                    description=f"دفعة من فاتورة {invoice.invoice_number or f'INV-{invoice.id}'}",
                    payment_type=random.choice(['مقبوضات', 'مدفوعات'])
                )
                db.session.add(payment)
            
            db.session.commit()
            print("✅ تم إنشاء 6 مدفوعات")
            
            print("\n🎉 تم إنشاء جميع البيانات التجريبية بنجاح!")
            
            # عرض ملخص البيانات
            print("\n📊 ملخص البيانات المُنشأة:")
            print(f"👥 العملاء: {Customer.query.count()}")
            print(f"🏭 الموردين: {Supplier.query.count()}")
            print(f"🛍️ فواتير المبيعات: {Invoice.query.count()}")
            print(f"🛒 فواتير المشتريات: {PurchaseInvoice.query.count()}")
            print(f"💰 المدفوعات: {Payment.query.count()}")
            
        except Exception as e:
            print(f"❌ خطأ في إنشاء البيانات: {str(e)}")
            db.session.rollback()

if __name__ == "__main__":
    create_sample_data()
