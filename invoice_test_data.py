#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
مولد البيانات التجريبية لاختبار نظام الفواتير
"""

from app import app
from database import db, Customer, Invoice, Product
from datetime import datetime, date, timedelta
import random

def create_test_customers():
    """إنشاء عملاء تجريبيين للفواتير"""
    
    test_customers = [
        {
            'name': 'شركة الرياض للتجارة',
            'email': 'info@riyadh-trade.com',
            'phone': '0112345678'
        },
        {
            'name': 'مؤسسة جدة للمقاولات',
            'email': 'contracts@jeddah-const.com',
            'phone': '0126789012'
        },
        {
            'name': 'شركة الدمام للصناعات',
            'email': 'sales@dammam-industries.com',
            'phone': '0133456789'
        },
        {
            'name': 'مكتب الخبر للاستشارات',
            'email': 'info@khobar-consulting.com',
            'phone': '0138901234'
        },
        {
            'name': 'شركة المدينة للتقنية',
            'email': 'tech@madinah-tech.com',
            'phone': '0148567890'
        },
        {
            'name': 'مؤسسة مكة للخدمات',
            'email': 'services@makkah-services.com',
            'phone': '0125678901'
        },
        {
            'name': 'شركة الطائف للتطوير',
            'email': 'dev@taif-development.com',
            'phone': '0127890123'
        },
        {
            'name': 'مكتب القصيم للتسويق',
            'email': 'marketing@qassim-marketing.com',
            'phone': '0163456789'
        }
    ]
    
    with app.app_context():
        customers = []
        for customer_data in test_customers:
            # التحقق من عدم وجود العميل
            existing = Customer.query.filter_by(email=customer_data['email']).first()
            if not existing:
                customer = Customer(**customer_data)
                db.session.add(customer)
                customers.append(customer)
        
        db.session.commit()
        print(f"✅ تم إنشاء {len(customers)} عميل تجريبي للفواتير!")
        return Customer.query.all()

def create_test_products():
    """إنشاء منتجات تجريبية للفواتير"""
    
    test_products = [
        {
            'name': 'خدمات استشارية',
            'price': 500.00,
            'quantity': 100
        },
        {
            'name': 'تطوير موقع إلكتروني',
            'price': 5000.00,
            'quantity': 50
        },
        {
            'name': 'تدريب موظفين',
            'price': 2000.00,
            'quantity': 75
        },
        {
            'name': 'صيانة أنظمة',
            'price': 1500.00,
            'quantity': 80
        },
        {
            'name': 'تصميم جرافيك',
            'price': 800.00,
            'quantity': 120
        },
        {
            'name': 'إدارة مشاريع',
            'price': 3000.00,
            'quantity': 30
        },
        {
            'name': 'تسويق رقمي',
            'price': 2500.00,
            'quantity': 40
        },
        {
            'name': 'تحليل بيانات',
            'price': 1800.00,
            'quantity': 60
        }
    ]
    
    with app.app_context():
        products = []
        for product_data in test_products:
            # التحقق من عدم وجود المنتج
            existing = Product.query.filter_by(name=product_data['name']).first()
            if not existing:
                product = Product(**product_data)
                db.session.add(product)
                products.append(product)
        
        db.session.commit()
        print(f"✅ تم إنشاء {len(products)} منتج تجريبي للفواتير!")
        return Product.query.all()

def create_test_invoices():
    """إنشاء فواتير تجريبية"""
    
    with app.app_context():
        customers = Customer.query.all()
        products = Product.query.all()
        
        if not customers or not products:
            print("❌ يجب إنشاء العملاء والمنتجات أولاً!")
            return []
        
        invoices = []
        
        # إنشاء فواتير للشهرين الماضيين
        start_date = date.today() - timedelta(days=60)
        
        for i in range(25):  # 25 فاتورة
            invoice_date = start_date + timedelta(days=random.randint(0, 60))
            customer = random.choice(customers)
            
            # حساب المبلغ الإجمالي
            num_items = random.randint(1, 4)
            subtotal = 0
            
            for _ in range(num_items):
                product = random.choice(products)
                quantity = random.randint(1, 5)
                subtotal += product.price * quantity
            
            # حساب الضريبة (15%)
            tax_amount = subtotal * 0.15
            total_amount = subtotal + tax_amount
            
            # تحديد حالة الفاتورة
            statuses = ['paid', 'pending', 'overdue']
            weights = [0.6, 0.3, 0.1]  # 60% مدفوعة، 30% معلقة، 10% متأخرة
            status = random.choices(statuses, weights=weights)[0]
            
            invoice = Invoice(
                customer_name=customer.name,
                date=invoice_date,
                total_amount=total_amount
            )
            
            db.session.add(invoice)
            invoices.append(invoice)
        
        db.session.commit()
        print(f"✅ تم إنشاء {len(invoices)} فاتورة تجريبية!")
        return invoices

def run_invoice_test_data():
    """تشغيل مولد البيانات التجريبية للفواتير"""
    print("🚀 بدء إنشاء البيانات التجريبية للفواتير...")
    
    try:
        # إنشاء العملاء
        customers = create_test_customers()
        
        # إنشاء المنتجات
        products = create_test_products()
        
        # إنشاء الفواتير
        invoices = create_test_invoices()
        
        print("\n🎉 تم إنشاء جميع البيانات التجريبية للفواتير بنجاح!")
        print(f"📊 الإحصائيات:")
        print(f"   - العملاء: {len(customers)}")
        print(f"   - المنتجات: {len(products)}")
        print(f"   - الفواتير: {len(invoices)}")
        
        # حساب إحصائيات الفواتير
        with app.app_context():
            all_invoices = Invoice.query.all()
            total_amount = sum(inv.total_amount for inv in all_invoices)
            paid_invoices = len([inv for inv in all_invoices if inv.status == 'paid'])
            pending_invoices = len([inv for inv in all_invoices if inv.status == 'pending'])
            overdue_invoices = len([inv for inv in all_invoices if inv.status == 'overdue'])
            
            print(f"   - إجمالي المبلغ: {total_amount:,.2f} ر.س")
            print(f"   - فواتير مدفوعة: {paid_invoices}")
            print(f"   - فواتير معلقة: {pending_invoices}")
            print(f"   - فواتير متأخرة: {overdue_invoices}")
        
        return True
        
    except Exception as e:
        print(f"❌ خطأ في إنشاء البيانات التجريبية: {str(e)}")
        return False

if __name__ == "__main__":
    run_invoice_test_data()
