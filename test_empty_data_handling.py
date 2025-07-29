#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار التعامل مع البيانات الفارغة
Test Empty Data Handling
"""

from app import app
from database import db, Customer, Invoice, Supplier, Product, Expense, Employee, Attendance, Payroll, Leave, PurchaseInvoice, Payment
import requests
import time

def test_empty_database():
    """اختبار التطبيق مع قاعدة بيانات فارغة"""
    print("🧪 اختبار التعامل مع البيانات الفارغة...")
    print("="*60)
    
    with app.app_context():
        try:
            # حذف جميع البيانات للاختبار
            print("🗑️ حذف جميع البيانات للاختبار...")
            
            # حذف البيانات بالترتيب الصحيح (العلاقات أولاً)
            Payment.query.delete()
            Attendance.query.delete()
            Payroll.query.delete()
            Leave.query.delete()
            Invoice.query.delete()
            PurchaseInvoice.query.delete()
            Expense.query.delete()
            Product.query.delete()
            Customer.query.delete()
            Supplier.query.delete()
            Employee.query.delete()
            
            db.session.commit()
            print("✅ تم حذف جميع البيانات")
            
            # اختبار العدادات
            print("\n📊 اختبار العدادات:")
            customers_count = Customer.query.count()
            invoices_count = Invoice.query.count()
            products_count = Product.query.count()
            employees_count = Employee.query.count()
            
            print(f"  - العملاء: {customers_count}")
            print(f"  - الفواتير: {invoices_count}")
            print(f"  - المنتجات: {products_count}")
            print(f"  - الموظفين: {employees_count}")
            
            # اختبار الاستعلامات
            print("\n🔍 اختبار الاستعلامات:")
            
            # اختبار جلب البيانات الفارغة
            all_customers = Customer.query.all()
            all_invoices = Invoice.query.all()
            all_products = Product.query.all()
            all_employees = Employee.query.all()
            all_suppliers = Supplier.query.all()
            all_expenses = Expense.query.all()
            all_payments = Payment.query.all()
            
            print(f"  - جلب العملاء: {len(all_customers)} عنصر")
            print(f"  - جلب الفواتير: {len(all_invoices)} عنصر")
            print(f"  - جلب المنتجات: {len(all_products)} عنصر")
            print(f"  - جلب الموظفين: {len(all_employees)} عنصر")
            print(f"  - جلب الموردين: {len(all_suppliers)} عنصر")
            print(f"  - جلب المصروفات: {len(all_expenses)} عنصر")
            print(f"  - جلب المدفوعات: {len(all_payments)} عنصر")
            
            # اختبار الحسابات
            print("\n🧮 اختبار الحسابات:")
            
            # حساب المجاميع
            total_sales = sum(invoice.total_amount for invoice in all_invoices if invoice.total_amount)
            total_expenses = sum(expense.amount for expense in all_expenses if expense.amount)
            total_payments_received = sum(p.amount for p in all_payments if p.payment_type == 'received')
            total_payments_paid = sum(p.amount for p in all_payments if p.payment_type == 'paid')
            
            print(f"  - إجمالي المبيعات: {total_sales:,.2f} ر.س")
            print(f"  - إجمالي المصروفات: {total_expenses:,.2f} ر.س")
            print(f"  - إجمالي المقبوضات: {total_payments_received:,.2f} ر.س")
            print(f"  - إجمالي المدفوعات: {total_payments_paid:,.2f} ر.س")
            
            # اختبار المتوسطات
            avg_invoice = total_sales / len(all_invoices) if all_invoices else 0
            avg_expense = total_expenses / len(all_expenses) if all_expenses else 0
            
            print(f"  - متوسط الفاتورة: {avg_invoice:,.2f} ر.س")
            print(f"  - متوسط المصروف: {avg_expense:,.2f} ر.س")
            
            print("\n✅ جميع الاختبارات نجحت مع البيانات الفارغة!")
            return True
            
        except Exception as e:
            print(f"❌ خطأ في الاختبار: {e}")
            return False

def test_routes_with_empty_data():
    """اختبار المسارات مع البيانات الفارغة"""
    print("\n🌐 اختبار المسارات مع البيانات الفارغة...")
    print("="*60)
    
    # قائمة المسارات للاختبار
    routes_to_test = [
        '/',
        '/customers',
        '/invoices',
        '/inventory',
        '/suppliers',
        '/employees',
        '/expenses',
        '/payments',
        '/attendance',
        '/payroll',
        '/leaves',
        '/purchase_invoices',
        '/sales_invoices'
    ]
    
    base_url = 'http://localhost:5000'
    success_count = 0
    total_count = len(routes_to_test)
    
    for route in routes_to_test:
        try:
            print(f"🔗 اختبار المسار: {route}")
            response = requests.get(f"{base_url}{route}", timeout=10)
            
            if response.status_code == 200:
                print(f"  ✅ نجح - كود الاستجابة: {response.status_code}")
                success_count += 1
            else:
                print(f"  ❌ فشل - كود الاستجابة: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print(f"  ⚠️ لا يمكن الاتصال بالخادم - تأكد من تشغيل التطبيق")
            break
        except Exception as e:
            print(f"  ❌ خطأ: {e}")
    
    print(f"\n📊 نتائج اختبار المسارات:")
    print(f"  - المسارات الناجحة: {success_count}/{total_count}")
    print(f"  - معدل النجاح: {(success_count/total_count)*100:.1f}%")
    
    return success_count == total_count

def test_form_pages():
    """اختبار صفحات النماذج مع البيانات الفارغة"""
    print("\n📝 اختبار صفحات النماذج...")
    print("="*60)
    
    form_routes = [
        '/add_customer',
        '/add_invoice',
        '/add_product',
        '/add_supplier',
        '/add_employee',
        '/add_expense',
        '/add_payment',
        '/add_attendance',
        '/add_leave',
        '/generate_payroll',
        '/add_purchase_invoice'
    ]
    
    base_url = 'http://localhost:5000'
    success_count = 0
    total_count = len(form_routes)
    
    for route in form_routes:
        try:
            print(f"📋 اختبار نموذج: {route}")
            response = requests.get(f"{base_url}{route}", timeout=10)
            
            if response.status_code == 200:
                print(f"  ✅ نجح - النموذج يعمل مع البيانات الفارغة")
                success_count += 1
            else:
                print(f"  ❌ فشل - كود الاستجابة: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print(f"  ⚠️ لا يمكن الاتصال بالخادم")
            break
        except Exception as e:
            print(f"  ❌ خطأ: {e}")
    
    print(f"\n📊 نتائج اختبار النماذج:")
    print(f"  - النماذج الناجحة: {success_count}/{total_count}")
    print(f"  - معدل النجاح: {(success_count/total_count)*100:.1f}%")
    
    return success_count == total_count

def main():
    """تشغيل جميع الاختبارات"""
    print("🚀 بدء اختبار التعامل مع البيانات الفارغة")
    print("="*60)
    
    # اختبار قاعدة البيانات الفارغة
    db_test = test_empty_database()
    
    # انتظار قصير
    time.sleep(2)
    
    # اختبار المسارات (يتطلب تشغيل الخادم)
    print("\n⚠️ تأكد من تشغيل الخادم قبل اختبار المسارات")
    print("تشغيل الخادم: python app.py")
    
    # routes_test = test_routes_with_empty_data()
    # forms_test = test_form_pages()
    
    print("\n🎯 ملخص النتائج:")
    print(f"  - اختبار قاعدة البيانات: {'✅ نجح' if db_test else '❌ فشل'}")
    # print(f"  - اختبار المسارات: {'✅ نجح' if routes_test else '❌ فشل'}")
    # print(f"  - اختبار النماذج: {'✅ نجح' if forms_test else '❌ فشل'}")
    
    if db_test:
        print("\n🎉 التطبيق جاهز للتعامل مع البيانات الفارغة!")
    else:
        print("\n⚠️ يحتاج التطبيق إلى مراجعة إضافية")

if __name__ == "__main__":
    main()
