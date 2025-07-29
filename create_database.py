#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
إنشاء قاعدة البيانات مع البيانات التجريبية
Create Database with Sample Data
"""

from flask import Flask
from database import db, init_db, Customer, Supplier, Invoice, Payment
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///accounting_system.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# تهيئة قاعدة البيانات
init_db(app)

def create_database():
    """إنشاء قاعدة البيانات والجداول"""
    try:
        with app.app_context():
            # إنشاء جميع الجداول
            db.create_all()
            print("✅ تم إنشاء قاعدة البيانات والجداول")
            
            # إضافة عملاء تجريبيين
            if Customer.query.count() == 0:
                customers = [
                    Customer(name="أحمد محمد", email="ahmed@example.com", phone="0501234567"),
                    Customer(name="فاطمة علي", email="fatima@example.com", phone="0509876543"),
                    Customer(name="محمد سعد", email="mohammed@example.com", phone="0505555555"),
                    Customer(name="سارة أحمد", email="sara@example.com", phone="0507777777"),
                    Customer(name="عبدالله خالد", email="abdullah@example.com", phone="0508888888")
                ]
                
                for customer in customers:
                    db.session.add(customer)
                
                db.session.commit()
                print("✅ تم إضافة العملاء التجريبيين")
            
            # إضافة موردين تجريبيين
            if Supplier.query.count() == 0:
                suppliers = [
                    Supplier(name="شركة التوريدات المتقدمة", contact_info="info@advanced.com - 0112345678"),
                    Supplier(name="مؤسسة الجودة التجارية", contact_info="sales@quality.com - 0113456789"),
                    Supplier(name="مكتب الخدمات الشاملة", contact_info="office@services.com - 0114567890"),
                    Supplier(name="شركة الإمدادات الحديثة", contact_info="supply@modern.com - 0115678901"),
                    Supplier(name="مؤسسة التجارة الذكية", contact_info="smart@trade.com - 0116789012")
                ]
                
                for supplier in suppliers:
                    db.session.add(supplier)
                
                db.session.commit()
                print("✅ تم إضافة الموردين التجريبيين")
            
            # إضافة فواتير تجريبية
            if Invoice.query.count() == 0:
                customers_list = Customer.query.all()
                invoices = [
                    Invoice(
                        customer_id=customers_list[0].id,
                        customer_name=customers_list[0].name,
                        invoice_number="INV-000001",
                        subtotal=1000.00,
                        tax_amount=150.00,
                        discount=50.00,
                        total_amount=1100.00,
                        notes="فاتورة تجريبية للاختبار"
                    ),
                    Invoice(
                        customer_id=customers_list[1].id,
                        customer_name=customers_list[1].name,
                        invoice_number="INV-000002",
                        subtotal=2000.00,
                        tax_amount=300.00,
                        discount=100.00,
                        total_amount=2200.00,
                        notes="فاتورة تجريبية ثانية"
                    ),
                    Invoice(
                        customer_id=customers_list[2].id,
                        customer_name=customers_list[2].name,
                        invoice_number="INV-000003",
                        subtotal=1500.00,
                        tax_amount=225.00,
                        discount=0.00,
                        total_amount=1725.00,
                        notes="فاتورة تجريبية ثالثة"
                    )
                ]
                
                for invoice in invoices:
                    db.session.add(invoice)
                
                db.session.commit()
                print("✅ تم إضافة الفواتير التجريبية")
            
            # إضافة مدفوعات تجريبية
            if Payment.query.count() == 0:
                invoices_list = Invoice.query.all()
                payments = [
                    Payment(
                        amount=500.00,
                        payment_method="cash",
                        payment_type="received",
                        payment_reference="PAY-000001",
                        reference_number="CASH-001",
                        invoice_id=invoices_list[0].id,
                        customer_name=invoices_list[0].customer_name,
                        notes="دفع نقدي تجريبي"
                    ),
                    Payment(
                        amount=1000.00,
                        payment_method="bank_transfer",
                        payment_type="received",
                        payment_reference="PAY-000002",
                        reference_number="BANK-001",
                        invoice_id=invoices_list[1].id,
                        customer_name=invoices_list[1].customer_name,
                        notes="تحويل بنكي تجريبي"
                    ),
                    Payment(
                        amount=750.00,
                        payment_method="check",
                        payment_type="paid",
                        payment_reference="PAY-000003",
                        reference_number="CHK-001",
                        supplier_name="مورد تجريبي",
                        notes="دفع بشيك تجريبي"
                    )
                ]
                
                for payment in payments:
                    db.session.add(payment)
                
                db.session.commit()
                print("✅ تم إضافة المدفوعات التجريبية")
            
            print("\n🎉 تم إنشاء قاعدة البيانات بنجاح مع البيانات التجريبية!")
            print("يمكنك الآن تشغيل التطبيق باستخدام: python app.py")
            
            return True
            
    except Exception as e:
        print(f"❌ خطأ في إنشاء قاعدة البيانات: {e}")
        return False

if __name__ == "__main__":
    print("🔄 بدء إنشاء قاعدة البيانات...")
    print("="*50)
    
    if create_database():
        print("✅ تم الإنجاز بنجاح")
    else:
        print("❌ فشل في الإنجاز")
