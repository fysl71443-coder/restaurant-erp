#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
إنشاء بيانات تجريبية مبسطة للفواتير
Create Simple Sample Invoices Data
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

def create_simple_data():
    """إنشاء بيانات تجريبية مبسطة للفواتير"""
    
    print("🔄 بدء إنشاء البيانات التجريبية المبسطة...")
    
    with app.app_context():
        try:
            # إنشاء فواتير مبيعات تجريبية
            print("🛍️ إنشاء فواتير المبيعات...")
            customers = Customer.query.all()
            
            if customers:
                for i in range(8):
                    customer = random.choice(customers)
                    invoice_date = datetime.now() - timedelta(days=random.randint(1, 30))
                    subtotal = random.uniform(1000, 10000)
                    tax_rate = 0.15  # ضريبة القيمة المضافة 15%
                    tax_amount = subtotal * tax_rate
                    total_amount = subtotal + tax_amount
                    
                    invoice = Invoice(
                        customer_name=customer.name,
                        date=invoice_date,
                        total_amount=round(total_amount, 2)
                    )
                    db.session.add(invoice)
                
                db.session.commit()
                print("✅ تم إنشاء 8 فواتير مبيعات")
            else:
                print("⚠️ لا توجد عملاء لإنشاء فواتير المبيعات")
            
            # إنشاء فواتير مشتريات تجريبية
            print("🛒 إنشاء فواتير المشتريات...")
            suppliers = Supplier.query.all()
            
            if suppliers:
                for i in range(6):
                    supplier = random.choice(suppliers)
                    invoice_date = datetime.now() - timedelta(days=random.randint(1, 30))
                    subtotal = random.uniform(2000, 15000)
                    tax_rate = 0.15
                    tax_amount = subtotal * tax_rate
                    total_amount = subtotal + tax_amount
                    
                    purchase_invoice = PurchaseInvoice(
                        supplier_name=supplier.name,
                        date=invoice_date,
                        total_amount=round(total_amount, 2)
                    )
                    db.session.add(purchase_invoice)
                
                db.session.commit()
                print("✅ تم إنشاء 6 فواتير مشتريات")
            else:
                print("⚠️ لا توجد موردين لإنشاء فواتير المشتريات")
            
            # إنشاء مدفوعات تجريبية
            print("💰 إنشاء المدفوعات...")
            invoices = Invoice.query.all()
            
            if invoices:
                for i in range(4):
                    invoice = random.choice(invoices)
                    payment_date = datetime.now() - timedelta(days=random.randint(1, 20))
                    amount = random.uniform(500, invoice.total_amount)
                    
                    payment = Payment(
                        amount=round(amount, 2),
                        date=payment_date,
                        payment_method=random.choice(['نقدي', 'تحويل بنكي', 'شيك', 'بطاقة ائتمان']),
                        payment_type=random.choice(['received', 'paid'])
                    )
                    db.session.add(payment)
                
                db.session.commit()
                print("✅ تم إنشاء 4 مدفوعات")
            else:
                print("⚠️ لا توجد فواتير لإنشاء المدفوعات")
            
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
    create_simple_data()
