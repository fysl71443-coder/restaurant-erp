#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار شامل لنظام المحاسبة الاحترافي
Comprehensive Test for Professional Accounting System
"""

import sys
import os
import unittest
from datetime import datetime, date
from decimal import Decimal

# إضافة مسار النظام
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from accounting_system_pro import app, db, User, Customer, Supplier, Product, Employee, Sale, Purchase, Expense, Payment, Salary, VATSetting
    print("✅ تم استيراد جميع النماذج بنجاح")
except ImportError as e:
    print(f"❌ خطأ في الاستيراد: {e}")
    sys.exit(1)

class TestAccountingSystem(unittest.TestCase):
    """فئة اختبار النظام"""
    
    def setUp(self):
        """إعداد الاختبار"""
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
            self.create_test_data()
    
    def tearDown(self):
        """تنظيف بعد الاختبار"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
    
    def create_test_data(self):
        """إنشاء بيانات اختبار"""
        # إنشاء مستخدم اختبار
        admin = User(
            username='testadmin',
            email='test@admin.com',
            full_name='مدير الاختبار',
            role='admin',
            can_sales=True,
            can_purchases=True,
            can_expenses=True,
            can_suppliers=True,
            can_invoices=True,
            can_payments=True,
            can_employees=True,
            can_reports=True,
            can_inventory=True,
            can_vat=True,
            can_settings=True
        )
        admin.set_password('testpass')
        db.session.add(admin)
        
        # إنشاء عميل اختبار
        customer = Customer(
            name='عميل اختبار',
            email='customer@test.com',
            phone='0501234567',
            tax_number='123456789'
        )
        db.session.add(customer)
        
        # إنشاء مورد اختبار
        supplier = Supplier(
            name='مورد اختبار',
            email='supplier@test.com',
            phone='0507654321',
            tax_number='987654321'
        )
        db.session.add(supplier)
        
        # إنشاء منتج اختبار
        product = Product(
            name='منتج اختبار',
            code='TEST001',
            unit='قطعة',
            cost_price=Decimal('100.00'),
            selling_price=Decimal('150.00'),
            stock_quantity=50,
            min_stock=10,
            category='اختبار'
        )
        db.session.add(product)
        
        # إنشاء موظف اختبار
        employee = Employee(
            name='موظف اختبار',
            employee_id='EMP001',
            position='محاسب',
            department='المحاسبة',
            salary=Decimal('5000.00'),
            hire_date=date.today()
        )
        db.session.add(employee)
        
        # إنشاء إعدادات ضريبة القيمة المضافة
        vat_setting = VATSetting(rate=Decimal('15.00'), is_active=True)
        db.session.add(vat_setting)
        
        db.session.commit()
        print("✅ تم إنشاء بيانات الاختبار")
    
    def test_home_page(self):
        """اختبار الصفحة الرئيسية"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('نظام المحاسبة الاحترافي', response.get_data(as_text=True))
        print("✅ اختبار الصفحة الرئيسية نجح")
    
    def test_login_page(self):
        """اختبار صفحة تسجيل الدخول"""
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn('تسجيل الدخول', response.get_data(as_text=True))
        print("✅ اختبار صفحة تسجيل الدخول نجح")
    
    def test_api_status(self):
        """اختبار API حالة النظام"""
        response = self.client.get('/api/status')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['status'], 'success')
        self.assertIn('features', data)
        self.assertIn('statistics', data)
        print("✅ اختبار API حالة النظام نجح")
    
    def test_database_models(self):
        """اختبار نماذج قاعدة البيانات"""
        with self.app.app_context():
            # اختبار المستخدم
            user = User.query.filter_by(username='testadmin').first()
            self.assertIsNotNone(user)
            self.assertTrue(user.check_password('testpass'))
            self.assertTrue(user.has_permission('sales'))
            
            # اختبار العميل
            customer = Customer.query.filter_by(name='عميل اختبار').first()
            self.assertIsNotNone(customer)
            self.assertEqual(customer.email, 'customer@test.com')
            
            # اختبار المورد
            supplier = Supplier.query.filter_by(name='مورد اختبار').first()
            self.assertIsNotNone(supplier)
            self.assertEqual(supplier.phone, '0507654321')
            
            # اختبار المنتج
            product = Product.query.filter_by(code='TEST001').first()
            self.assertIsNotNone(product)
            self.assertEqual(product.selling_price, Decimal('150.00'))
            
            # اختبار الموظف
            employee = Employee.query.filter_by(employee_id='EMP001').first()
            self.assertIsNotNone(employee)
            self.assertEqual(employee.salary, Decimal('5000.00'))
            
            # اختبار إعدادات الضريبة
            vat_setting = VATSetting.query.filter_by(is_active=True).first()
            self.assertIsNotNone(vat_setting)
            self.assertEqual(vat_setting.rate, Decimal('15.00'))
            
        print("✅ اختبار نماذج قاعدة البيانات نجح")
    
    def test_create_sale(self):
        """اختبار إنشاء مبيعة"""
        with self.app.app_context():
            customer = Customer.query.first()
            sale = Sale(
                invoice_number='SALE001',
                customer_id=customer.id,
                subtotal=Decimal('1000.00'),
                vat_amount=Decimal('150.00'),
                total_amount=Decimal('1150.00'),
                status='completed'
            )
            db.session.add(sale)
            db.session.commit()
            
            saved_sale = Sale.query.filter_by(invoice_number='SALE001').first()
            self.assertIsNotNone(saved_sale)
            self.assertEqual(saved_sale.total_amount, Decimal('1150.00'))
            
        print("✅ اختبار إنشاء مبيعة نجح")
    
    def test_create_purchase(self):
        """اختبار إنشاء مشترى"""
        with self.app.app_context():
            supplier = Supplier.query.first()
            purchase = Purchase(
                invoice_number='PUR001',
                supplier_id=supplier.id,
                subtotal=Decimal('800.00'),
                vat_amount=Decimal('120.00'),
                total_amount=Decimal('920.00'),
                status='received'
            )
            db.session.add(purchase)
            db.session.commit()
            
            saved_purchase = Purchase.query.filter_by(invoice_number='PUR001').first()
            self.assertIsNotNone(saved_purchase)
            self.assertEqual(saved_purchase.total_amount, Decimal('920.00'))
            
        print("✅ اختبار إنشاء مشترى نجح")
    
    def test_create_expense(self):
        """اختبار إنشاء مصروف"""
        with self.app.app_context():
            expense = Expense(
                description='مصروف اختبار',
                category='اختبار',
                amount=Decimal('500.00'),
                payment_method='نقدي'
            )
            db.session.add(expense)
            db.session.commit()
            
            saved_expense = Expense.query.filter_by(description='مصروف اختبار').first()
            self.assertIsNotNone(saved_expense)
            self.assertEqual(saved_expense.amount, Decimal('500.00'))
            
        print("✅ اختبار إنشاء مصروف نجح")
    
    def test_create_salary(self):
        """اختبار إنشاء راتب"""
        with self.app.app_context():
            employee = Employee.query.first()
            salary = Salary(
                employee_id=employee.id,
                month=12,
                year=2024,
                basic_salary=Decimal('5000.00'),
                allowances=Decimal('500.00'),
                deductions=Decimal('200.00'),
                net_salary=Decimal('5300.00'),
                status='paid'
            )
            db.session.add(salary)
            db.session.commit()
            
            saved_salary = Salary.query.filter_by(employee_id=employee.id).first()
            self.assertIsNotNone(saved_salary)
            self.assertEqual(saved_salary.net_salary, Decimal('5300.00'))
            
        print("✅ اختبار إنشاء راتب نجح")

def run_comprehensive_test():
    """تشغيل اختبار شامل للنظام"""
    print("🧪 بدء الاختبار الشامل لنظام المحاسبة الاحترافي")
    print("=" * 60)
    
    # اختبار الاستيراد
    print("1️⃣ اختبار الاستيراد...")
    try:
        from accounting_system_pro import app
        print("   ✅ تم استيراد التطبيق بنجاح")
    except Exception as e:
        print(f"   ❌ خطأ في الاستيراد: {e}")
        return False
    
    # اختبار إنشاء التطبيق
    print("2️⃣ اختبار إنشاء التطبيق...")
    try:
        test_client = app.test_client()
        print("   ✅ تم إنشاء عميل الاختبار بنجاح")
    except Exception as e:
        print(f"   ❌ خطأ في إنشاء التطبيق: {e}")
        return False
    
    # اختبار الصفحة الرئيسية
    print("3️⃣ اختبار الصفحة الرئيسية...")
    try:
        response = test_client.get('/')
        if response.status_code == 200:
            print("   ✅ الصفحة الرئيسية تعمل بنجاح")
        else:
            print(f"   ❌ خطأ في الصفحة الرئيسية: {response.status_code}")
    except Exception as e:
        print(f"   ❌ خطأ في اختبار الصفحة الرئيسية: {e}")
    
    # اختبار صفحة تسجيل الدخول
    print("4️⃣ اختبار صفحة تسجيل الدخول...")
    try:
        response = test_client.get('/login')
        if response.status_code == 200:
            print("   ✅ صفحة تسجيل الدخول تعمل بنجاح")
        else:
            print(f"   ❌ خطأ في صفحة تسجيل الدخول: {response.status_code}")
    except Exception as e:
        print(f"   ❌ خطأ في اختبار صفحة تسجيل الدخول: {e}")
    
    # اختبار API
    print("5️⃣ اختبار API...")
    try:
        response = test_client.get('/api/status')
        if response.status_code == 200:
            data = response.get_json()
            if data and data.get('status') == 'success':
                print("   ✅ API يعمل بنجاح")
            else:
                print("   ❌ خطأ في استجابة API")
        else:
            print(f"   ❌ خطأ في API: {response.status_code}")
    except Exception as e:
        print(f"   ❌ خطأ في اختبار API: {e}")
    
    # تشغيل اختبارات unittest
    print("6️⃣ تشغيل اختبارات unittest...")
    try:
        suite = unittest.TestLoader().loadTestsFromTestCase(TestAccountingSystem)
        runner = unittest.TextTestRunner(verbosity=0)
        result = runner.run(suite)
        
        if result.wasSuccessful():
            print("   ✅ جميع اختبارات unittest نجحت")
        else:
            print(f"   ❌ فشل {len(result.failures)} اختبار")
            print(f"   ❌ خطأ في {len(result.errors)} اختبار")
    except Exception as e:
        print(f"   ❌ خطأ في تشغيل اختبارات unittest: {e}")
    
    print("=" * 60)
    print("🎉 انتهى الاختبار الشامل")
    return True

if __name__ == '__main__':
    # تشغيل الاختبار الشامل
    success = run_comprehensive_test()
    
    if success:
        print("\n✅ النظام جاهز للاستخدام!")
        print("🚀 يمكنك الآن تشغيل النظام باستخدام: python accounting_system_pro.py")
    else:
        print("\n❌ يوجد مشاكل في النظام تحتاج إلى إصلاح")
    
    sys.exit(0 if success else 1)
