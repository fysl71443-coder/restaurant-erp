#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار شامل لفواتير المبيعات والمشتريات وتسجيل المدفوعات
"""

import requests
import json
import time
from datetime import datetime

# إعدادات الاختبار
BASE_URL = "http://localhost:5000"
TEST_RESULTS = []

def log_test(test_name, status, details=""):
    """تسجيل نتيجة الاختبار"""
    result = {
        'test': test_name,
        'status': status,
        'details': details,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    TEST_RESULTS.append(result)
    
    status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
    print(f"{status_icon} {test_name}: {status}")
    if details:
        print(f"   📝 {details}")

def test_sales_invoice_pages():
    """اختبار صفحات فواتير المبيعات"""
    print("💰 اختبار صفحات فواتير المبيعات:")
    
    pages = [
        ("/sales_invoices", "قائمة فواتير المبيعات"),
        ("/add_sales_invoice", "إضافة فاتورة مبيعات")
    ]
    
    for url, name in pages:
        try:
            response = requests.get(f"{BASE_URL}{url}", timeout=10)
            if response.status_code == 200:
                log_test(f"فواتير المبيعات - {name}", "PASS", f"كود الاستجابة: {response.status_code}")
                
                # التحقق من وجود عناصر مهمة
                html_content = response.text
                if "فواتير المبيعات" in html_content or "فاتورة مبيعات" in html_content:
                    log_test(f"فواتير المبيعات - محتوى {name}", "PASS", "المحتوى العربي موجود")
                else:
                    log_test(f"فواتير المبيعات - محتوى {name}", "WARNING", "المحتوى العربي قد يكون ناقص")
                    
            else:
                log_test(f"فواتير المبيعات - {name}", "FAIL", f"كود الاستجابة: {response.status_code}")
        except Exception as e:
            log_test(f"فواتير المبيعات - {name}", "FAIL", f"خطأ: {str(e)}")
        time.sleep(0.5)

def test_purchase_invoice_pages():
    """اختبار صفحات فواتير المشتريات"""
    print("\n🛒 اختبار صفحات فواتير المشتريات:")
    
    pages = [
        ("/purchase_invoices", "قائمة فواتير المشتريات"),
        ("/add_purchase_invoice", "إضافة فاتورة مشتريات")
    ]
    
    for url, name in pages:
        try:
            response = requests.get(f"{BASE_URL}{url}", timeout=10)
            if response.status_code == 200:
                log_test(f"فواتير المشتريات - {name}", "PASS", f"كود الاستجابة: {response.status_code}")
                
                # التحقق من وجود عناصر مهمة
                html_content = response.text
                if "فواتير المشتريات" in html_content or "فاتورة مشتريات" in html_content:
                    log_test(f"فواتير المشتريات - محتوى {name}", "PASS", "المحتوى العربي موجود")
                else:
                    log_test(f"فواتير المشتريات - محتوى {name}", "WARNING", "المحتوى العربي قد يكون ناقص")
                    
            else:
                log_test(f"فواتير المشتريات - {name}", "FAIL", f"كود الاستجابة: {response.status_code}")
        except Exception as e:
            log_test(f"فواتير المشتريات - {name}", "FAIL", f"خطأ: {str(e)}")
        time.sleep(0.5)

def test_payment_pages():
    """اختبار صفحات المدفوعات"""
    print("\n💳 اختبار صفحات المدفوعات:")
    
    pages = [
        ("/payments", "قائمة المدفوعات"),
        ("/add_payment", "تسجيل دفع جديد")
    ]
    
    for url, name in pages:
        try:
            response = requests.get(f"{BASE_URL}{url}", timeout=10)
            if response.status_code == 200:
                log_test(f"المدفوعات - {name}", "PASS", f"كود الاستجابة: {response.status_code}")
                
                # التحقق من وجود عناصر مهمة
                html_content = response.text
                if "المدفوعات" in html_content or "دفع" in html_content:
                    log_test(f"المدفوعات - محتوى {name}", "PASS", "المحتوى العربي موجود")
                else:
                    log_test(f"المدفوعات - محتوى {name}", "WARNING", "المحتوى العربي قد يكون ناقص")
                    
            else:
                log_test(f"المدفوعات - {name}", "FAIL", f"كود الاستجابة: {response.status_code}")
        except Exception as e:
            log_test(f"المدفوعات - {name}", "FAIL", f"خطأ: {str(e)}")
        time.sleep(0.5)

def test_sales_invoice_form_elements():
    """اختبار عناصر نموذج فاتورة المبيعات"""
    print("\n📝 اختبار عناصر نموذج فاتورة المبيعات:")
    
    try:
        response = requests.get(f"{BASE_URL}/add_sales_invoice", timeout=10)
        if response.status_code == 200:
            html_content = response.text
            
            # التحقق من وجود الحقول المطلوبة
            required_fields = [
                'customer_name',
                'subtotal',
                'tax_amount',
                'discount',
                'total_amount',
                'notes'
            ]
            
            for field in required_fields:
                if f'name="{field}"' in html_content or f'id="{field}"' in html_content:
                    log_test(f"نموذج فاتورة المبيعات - حقل {field}", "PASS", "الحقل موجود")
                else:
                    log_test(f"نموذج فاتورة المبيعات - حقل {field}", "FAIL", "الحقل مفقود")
            
            # التحقق من وجود وظائف JavaScript
            js_functions = [
                'calculateTotal',
                'addInvoiceItem',
                'removeInvoiceItem'
            ]
            
            found_functions = [func for func in js_functions if func in html_content]
            
            if len(found_functions) >= 2:
                log_test("نموذج فاتورة المبيعات - وظائف JavaScript", "PASS", f"وظائف موجودة: {len(found_functions)}")
            else:
                log_test("نموذج فاتورة المبيعات - وظائف JavaScript", "WARNING", f"وظائف محدودة: {len(found_functions)}")
                
        else:
            log_test("نموذج فاتورة المبيعات", "FAIL", f"كود الاستجابة: {response.status_code}")
    except Exception as e:
        log_test("نموذج فاتورة المبيعات", "FAIL", f"خطأ: {str(e)}")

def test_payment_form_elements():
    """اختبار عناصر نموذج تسجيل الدفع"""
    print("\n💰 اختبار عناصر نموذج تسجيل الدفع:")
    
    try:
        response = requests.get(f"{BASE_URL}/add_payment", timeout=10)
        if response.status_code == 200:
            html_content = response.text
            
            # التحقق من وجود الحقول المطلوبة
            required_fields = [
                'amount',
                'payment_method',
                'payment_type',
                'reference_number'
            ]
            
            for field in required_fields:
                if f'name="{field}"' in html_content or f'id="{field}"' in html_content:
                    log_test(f"نموذج تسجيل الدفع - حقل {field}", "PASS", "الحقل موجود")
                else:
                    log_test(f"نموذج تسجيل الدفع - حقل {field}", "FAIL", "الحقل مفقود")
            
            # التحقق من وجود خيارات طرق الدفع
            payment_methods = [
                'cash',
                'bank_transfer',
                'check',
                'card'
            ]
            
            found_methods = [method for method in payment_methods if method in html_content]
            
            if len(found_methods) >= 3:
                log_test("نموذج تسجيل الدفع - طرق الدفع", "PASS", f"طرق متاحة: {len(found_methods)}")
            else:
                log_test("نموذج تسجيل الدفع - طرق الدفع", "WARNING", f"طرق محدودة: {len(found_methods)}")
                
        else:
            log_test("نموذج تسجيل الدفع", "FAIL", f"كود الاستجابة: {response.status_code}")
    except Exception as e:
        log_test("نموذج تسجيل الدفع", "FAIL", f"خطأ: {str(e)}")

def test_invoice_creation():
    """اختبار إنشاء فاتورة مبيعات"""
    print("\n🧾 اختبار إنشاء فاتورة مبيعات:")
    
    try:
        # بيانات فاتورة تجريبية
        invoice_data = {
            'customer_name': 'عميل اختبار',
            'subtotal': '1000.00',
            'tax_amount': '150.00',
            'discount': '0.00',
            'total_amount': '1150.00',
            'notes': 'فاتورة اختبار'
        }
        
        response = requests.post(f"{BASE_URL}/add_sales_invoice", data=invoice_data, timeout=10)
        
        if response.status_code in [200, 201, 302]:
            log_test("إنشاء فاتورة مبيعات", "PASS", "تم إنشاء الفاتورة بنجاح")
        elif response.status_code == 400:
            log_test("إنشاء فاتورة مبيعات", "WARNING", "خطأ في البيانات المرسلة")
        else:
            log_test("إنشاء فاتورة مبيعات", "FAIL", f"كود الاستجابة: {response.status_code}")
            
    except Exception as e:
        log_test("إنشاء فاتورة مبيعات", "FAIL", f"خطأ: {str(e)}")

def test_purchase_invoice_creation():
    """اختبار إنشاء فاتورة مشتريات"""
    print("\n📦 اختبار إنشاء فاتورة مشتريات:")
    
    try:
        # بيانات فاتورة مشتريات تجريبية
        purchase_data = {
            'supplier_name': 'مورد اختبار',
            'subtotal': '2000.00',
            'tax_amount': '300.00',
            'discount': '100.00',
            'total_amount': '2200.00',
            'notes': 'فاتورة مشتريات اختبار'
        }
        
        response = requests.post(f"{BASE_URL}/add_purchase_invoice", data=purchase_data, timeout=10)
        
        if response.status_code in [200, 201, 302]:
            log_test("إنشاء فاتورة مشتريات", "PASS", "تم إنشاء الفاتورة بنجاح")
        elif response.status_code == 400:
            log_test("إنشاء فاتورة مشتريات", "WARNING", "خطأ في البيانات المرسلة")
        else:
            log_test("إنشاء فاتورة مشتريات", "FAIL", f"كود الاستجابة: {response.status_code}")
            
    except Exception as e:
        log_test("إنشاء فاتورة مشتريات", "FAIL", f"خطأ: {str(e)}")

def test_payment_creation():
    """اختبار تسجيل دفع"""
    print("\n💸 اختبار تسجيل دفع:")
    
    try:
        # بيانات دفع تجريبية
        payment_data = {
            'amount': '1150.00',
            'payment_method': 'bank_transfer',
            'payment_type': 'received',
            'reference_number': 'TEST-001',
            'customer_name': 'عميل اختبار',
            'notes': 'دفع اختبار'
        }
        
        response = requests.post(f"{BASE_URL}/add_payment", data=payment_data, timeout=10)
        
        if response.status_code in [200, 201, 302]:
            log_test("تسجيل دفع", "PASS", "تم تسجيل الدفع بنجاح")
        elif response.status_code == 400:
            log_test("تسجيل دفع", "WARNING", "خطأ في البيانات المرسلة")
        else:
            log_test("تسجيل دفع", "FAIL", f"كود الاستجابة: {response.status_code}")
            
    except Exception as e:
        log_test("تسجيل دفع", "FAIL", f"خطأ: {str(e)}")

def test_navigation_links():
    """اختبار روابط التنقل"""
    print("\n🔗 اختبار روابط التنقل:")
    
    try:
        # اختبار الصفحة الرئيسية للتحقق من وجود الروابط
        response = requests.get(f"{BASE_URL}/", timeout=10)
        if response.status_code == 200:
            html_content = response.text
            
            # التحقق من وجود روابط في القائمة الجانبية
            navigation_links = [
                '/sales_invoices',
                '/purchase_invoices',
                '/payments'
            ]
            
            found_links = [link for link in navigation_links if link in html_content]
            
            if len(found_links) >= 2:
                log_test("روابط التنقل", "PASS", f"روابط موجودة: {len(found_links)}/3")
            else:
                log_test("روابط التنقل", "WARNING", f"روابط محدودة: {len(found_links)}/3")
                
        else:
            log_test("روابط التنقل", "FAIL", "فشل في تحميل الصفحة الرئيسية")
    except Exception as e:
        log_test("روابط التنقل", "FAIL", f"خطأ: {str(e)}")

def run_invoice_payment_test():
    """تشغيل الاختبار الشامل للفواتير والمدفوعات"""
    print("🧾 بدء الاختبار الشامل لفواتير المبيعات والمشتريات والمدفوعات")
    print("=" * 80)
    
    # اختبار صفحات فواتير المبيعات
    test_sales_invoice_pages()
    
    # اختبار صفحات فواتير المشتريات
    test_purchase_invoice_pages()
    
    # اختبار صفحات المدفوعات
    test_payment_pages()
    
    # اختبار عناصر النماذج
    test_sales_invoice_form_elements()
    test_payment_form_elements()
    
    # اختبار إنشاء الفواتير والمدفوعات
    test_invoice_creation()
    test_purchase_invoice_creation()
    test_payment_creation()
    
    # اختبار روابط التنقل
    test_navigation_links()
    
    # تلخيص النتائج
    print("\n" + "=" * 80)
    print("📊 ملخص نتائج اختبار الفواتير والمدفوعات:")
    
    total_tests = len(TEST_RESULTS)
    passed_tests = len([r for r in TEST_RESULTS if r['status'] == 'PASS'])
    failed_tests = len([r for r in TEST_RESULTS if r['status'] == 'FAIL'])
    warning_tests = len([r for r in TEST_RESULTS if r['status'] == 'WARNING'])
    
    print(f"   📈 إجمالي الاختبارات: {total_tests}")
    print(f"   ✅ نجح: {passed_tests}")
    print(f"   ❌ فشل: {failed_tests}")
    print(f"   ⚠️  تحذير: {warning_tests}")
    
    success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
    print(f"   🎯 معدل النجاح: {success_rate:.1f}%")
    
    # تحليل النتائج حسب الفئة
    print("\n📋 تحليل النتائج حسب الفئة:")
    
    categories = {
        'فواتير المبيعات': ['فواتير المبيعات', 'نموذج فاتورة المبيعات', 'إنشاء فاتورة مبيعات'],
        'فواتير المشتريات': ['فواتير المشتريات', 'إنشاء فاتورة مشتريات'],
        'المدفوعات': ['المدفوعات', 'نموذج تسجيل الدفع', 'تسجيل دفع'],
        'التنقل': ['روابط التنقل']
    }
    
    for category, keywords in categories.items():
        category_tests = [r for r in TEST_RESULTS if any(keyword in r['test'] for keyword in keywords)]
        category_passed = len([r for r in category_tests if r['status'] == 'PASS'])
        category_total = len(category_tests)
        category_rate = (category_passed / category_total) * 100 if category_total > 0 else 0
        
        status_icon = "✅" if category_rate >= 80 else "⚠️" if category_rate >= 60 else "❌"
        print(f"   {status_icon} {category}: {category_rate:.1f}% ({category_passed}/{category_total})")
    
    if success_rate >= 90:
        print("\n🎉 ممتاز! نظام الفواتير والمدفوعات يعمل بكفاءة عالية")
    elif success_rate >= 75:
        print("\n👍 جيد! نظام الفواتير والمدفوعات يعمل بشكل مقبول")
    elif success_rate >= 60:
        print("\n⚠️  مقبول! بعض أجزاء النظام تحتاج تحسين")
    else:
        print("\n❌ يحتاج إصلاح! مشاكل كثيرة في النظام")
    
    # حفظ النتائج في ملف
    with open('invoice_payment_test_results.json', 'w', encoding='utf-8') as f:
        json.dump(TEST_RESULTS, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 تم حفظ النتائج التفصيلية في: invoice_payment_test_results.json")
    
    return success_rate

if __name__ == "__main__":
    try:
        success_rate = run_invoice_payment_test()
        exit(0 if success_rate >= 75 else 1)
    except KeyboardInterrupt:
        print("\n⏹️  تم إيقاف الاختبار بواسطة المستخدم")
        exit(1)
    except Exception as e:
        print(f"\n❌ خطأ عام في اختبار الفواتير والمدفوعات: {str(e)}")
        exit(1)
