#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
إنشاء بيانات تجريبية للمدفوعات
Create Sample Payments Data
"""

from app import app
from database import db, Payment, Customer, Supplier, Invoice
from datetime import datetime, timedelta
import random

def create_sample_payments():
    """إنشاء بيانات تجريبية للمدفوعات"""
    print("🚀 إنشاء بيانات تجريبية للمدفوعات...")
    
    with app.app_context():
        try:
            # حذف البيانات الموجودة
            Payment.query.delete()
            db.session.commit()
            print("✅ تم حذف البيانات القديمة")
            
            # إنشاء عملاء وموردين إذا لم يكونوا موجودين
            customers = Customer.query.all()
            if not customers:
                customers_data = [
                    {'name': 'أحمد محمد', 'email': 'ahmed@example.com', 'phone': '0501234567'},
                    {'name': 'فاطمة علي', 'email': 'fatima@example.com', 'phone': '0507654321'},
                    {'name': 'محمد سالم', 'email': 'mohammed@example.com', 'phone': '0509876543'},
                    {'name': 'نورا أحمد', 'email': 'nora@example.com', 'phone': '0502468135'},
                ]
                
                for customer_data in customers_data:
                    customer = Customer(**customer_data)
                    db.session.add(customer)
                
                db.session.commit()
                customers = Customer.query.all()
                print(f"✅ تم إنشاء {len(customers)} عميل")
            
            suppliers = Supplier.query.all()
            if not suppliers:
                suppliers_data = [
                    {'name': 'شركة التوريدات المتقدمة', 'email': 'advanced@supply.com', 'phone': '0112345678'},
                    {'name': 'مؤسسة الخليج للتجارة', 'email': 'gulf@trade.com', 'phone': '0118765432'},
                    {'name': 'شركة النور للمواد', 'email': 'alnoor@materials.com', 'phone': '0119876543'},
                ]
                
                for supplier_data in suppliers_data:
                    supplier = Supplier(**supplier_data)
                    db.session.add(supplier)
                
                db.session.commit()
                suppliers = Supplier.query.all()
                print(f"✅ تم إنشاء {len(suppliers)} مورد")
            
            # إنشاء مدفوعات تجريبية
            payment_methods = ['cash', 'bank_transfer', 'check', 'card']
            payment_types = ['received', 'paid']
            
            payments_data = []
            
            # مدفوعات مقبوضة (من العملاء)
            for i in range(15):
                customer = random.choice(customers)
                payment_data = {
                    'date': datetime.now() - timedelta(days=random.randint(1, 90)),
                    'amount': round(random.uniform(500, 5000), 2),
                    'payment_method': random.choice(payment_methods),
                    'payment_type': 'received',
                    'reference_number': f'REC-{1000 + i}',
                    'customer_name': customer.name,
                    'notes': f'دفعة من العميل {customer.name}',
                    'created_at': datetime.now()
                }
                payments_data.append(payment_data)
            
            # مدفوعات مدفوعة (للموردين)
            for i in range(10):
                supplier = random.choice(suppliers)
                payment_data = {
                    'date': datetime.now() - timedelta(days=random.randint(1, 60)),
                    'amount': round(random.uniform(1000, 8000), 2),
                    'payment_method': random.choice(payment_methods),
                    'payment_type': 'paid',
                    'reference_number': f'PAY-{2000 + i}',
                    'supplier_name': supplier.name,
                    'notes': f'دفعة للمورد {supplier.name}',
                    'created_at': datetime.now()
                }
                payments_data.append(payment_data)
            
            # إضافة المدفوعات إلى قاعدة البيانات
            for payment_data in payments_data:
                payment = Payment(**payment_data)
                db.session.add(payment)
            
            db.session.commit()
            print(f"✅ تم إنشاء {len(payments_data)} دفعة")
            
            # عرض الإحصائيات
            total_received = sum(p['amount'] for p in payments_data if p['payment_type'] == 'received')
            total_paid = sum(p['amount'] for p in payments_data if p['payment_type'] == 'paid')
            net_flow = total_received - total_paid
            
            print("\n📊 إحصائيات المدفوعات:")
            print(f"💰 إجمالي المقبوضات: {total_received:,.2f} ر.س")
            print(f"💸 إجمالي المدفوعات: {total_paid:,.2f} ر.س")
            print(f"📈 صافي التدفق: {net_flow:,.2f} ر.س")
            
        except Exception as e:
            print(f"❌ خطأ في إنشاء البيانات: {e}")
            db.session.rollback()

def main():
    """الدالة الرئيسية"""
    print("🚀 إنشاء بيانات تجريبية للمدفوعات")
    print("=" * 50)
    
    create_sample_payments()
    
    print("=" * 50)
    print("✅ انتهى إنشاء البيانات!")

if __name__ == "__main__":
    main()
