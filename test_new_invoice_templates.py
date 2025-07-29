#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار شامل للنماذج الجديدة لفواتير المبيعات والمشتريات
Test script for new sales and purchase invoice templates
"""

import requests
import time
from datetime import datetime

# إعدادات الاختبار
BASE_URL = "http://127.0.0.1:5000"
TEST_RESULTS = []

def log_test(test_name, status, details=""):
    """تسجيل نتائج الاختبار"""
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
        print(f"   التفاصيل: {details}")

def test_sales_invoice_form():
    """اختبار نموذج فاتورة المبيعات الجديد"""
    try:
        response = requests.get(f"{BASE_URL}/add_sales_invoice", timeout=10)
        
        if response.status_code == 200:
            content = response.text
            
            # فحص العناصر الأساسية للنموذج
            checks = [
                ('customer_name', 'حقل اسم العميل'),
                ('subtotal', 'حقل المجموع الفرعي'),
                ('tax_amount', 'حقل الضريبة'),
                ('discount', 'حقل الخصم'),
                ('total_amount', 'حقل الإجمالي'),
                ('notes', 'حقل الملاحظات'),
                ('calculateVAT', 'دالة حساب الضريبة'),
                ('calculateTotal', 'دالة حساب الإجمالي'),
                ('updatePreview', 'دالة تحديث المعاينة'),
                ('preview_customer', 'معاينة العميل'),
                ('bg-success', 'تصميم المبيعات (أخضر)'),
                ('fas fa-file-invoice-dollar', 'أيقونة فاتورة المبيعات')
            ]
            
            missing_elements = []
            for element, description in checks:
                if element not in content:
                    missing_elements.append(description)
            
            if not missing_elements:
                log_test("نموذج فاتورة المبيعات - العناصر الأساسية", "PASS", 
                        "جميع العناصر المطلوبة موجودة")
            else:
                log_test("نموذج فاتورة المبيعات - العناصر الأساسية", "FAIL", 
                        f"عناصر مفقودة: {', '.join(missing_elements)}")
                
            # فحص الجافا سكريبت
            js_functions = ['calculateTotal()', 'calculateVAT()', 'updatePreview()']
            js_missing = [func for func in js_functions if func not in content]
            
            if not js_missing:
                log_test("نموذج فاتورة المبيعات - الجافا سكريبت", "PASS", 
                        "جميع دوال الجافا سكريبت موجودة")
            else:
                log_test("نموذج فاتورة المبيعات - الجافا سكريبت", "FAIL", 
                        f"دوال مفقودة: {', '.join(js_missing)}")
                
        else:
            log_test("نموذج فاتورة المبيعات - الوصول", "FAIL", 
                    f"HTTP {response.status_code}")
            
    except Exception as e:
        log_test("نموذج فاتورة المبيعات - الوصول", "FAIL", str(e))

def test_purchase_invoice_form():
    """اختبار نموذج فاتورة المشتريات الجديد"""
    try:
        response = requests.get(f"{BASE_URL}/add_purchase_invoice", timeout=10)
        
        if response.status_code == 200:
            content = response.text
            
            # فحص العناصر الأساسية للنموذج
            checks = [
                ('supplier_name', 'حقل اسم المورد'),
                ('subtotal', 'حقل المجموع الفرعي'),
                ('tax_amount', 'حقل الضريبة'),
                ('discount', 'حقل الخصم'),
                ('total_amount', 'حقل الإجمالي'),
                ('notes', 'حقل الملاحظات'),
                ('calculateVAT', 'دالة حساب الضريبة'),
                ('calculateTotal', 'دالة حساب الإجمالي'),
                ('updatePreview', 'دالة تحديث المعاينة'),
                ('preview_supplier', 'معاينة المورد'),
                ('bg-danger', 'تصميم المشتريات (أحمر)'),
                ('fas fa-file-invoice', 'أيقونة فاتورة المشتريات')
            ]
            
            missing_elements = []
            for element, description in checks:
                if element not in content:
                    missing_elements.append(description)
            
            if not missing_elements:
                log_test("نموذج فاتورة المشتريات - العناصر الأساسية", "PASS", 
                        "جميع العناصر المطلوبة موجودة")
            else:
                log_test("نموذج فاتورة المشتريات - العناصر الأساسية", "FAIL", 
                        f"عناصر مفقودة: {', '.join(missing_elements)}")
                
            # فحص الجافا سكريبت
            js_functions = ['calculateTotal()', 'calculateVAT()', 'updatePreview()']
            js_missing = [func for func in js_functions if func not in content]
            
            if not js_missing:
                log_test("نموذج فاتورة المشتريات - الجافا سكريبت", "PASS", 
                        "جميع دوال الجافا سكريبت موجودة")
            else:
                log_test("نموذج فاتورة المشتريات - الجافا سكريبت", "FAIL", 
                        f"دوال مفقودة: {', '.join(js_missing)}")
                
        else:
            log_test("نموذج فاتورة المشتريات - الوصول", "FAIL", 
                    f"HTTP {response.status_code}")
            
    except Exception as e:
        log_test("نموذج فاتورة المشتريات - الوصول", "FAIL", str(e))

def test_sales_invoice_submission():
    """اختبار إرسال فاتورة مبيعات"""
    try:
        data = {
            'customer_name': 'عميل تجريبي',
            'subtotal': '1000.00',
            'tax_amount': '150.00',
            'discount': '50.00',
            'total_amount': '1100.00',
            'notes': 'فاتورة اختبار للمبيعات'
        }
        
        response = requests.post(f"{BASE_URL}/add_sales_invoice", data=data, timeout=10)
        
        if response.status_code in [200, 302]:
            log_test("إرسال فاتورة المبيعات", "PASS", 
                    f"تم الإرسال بنجاح - HTTP {response.status_code}")
        else:
            log_test("إرسال فاتورة المبيعات", "FAIL", 
                    f"فشل الإرسال - HTTP {response.status_code}")
            
    except Exception as e:
        log_test("إرسال فاتورة المبيعات", "FAIL", str(e))

def test_purchase_invoice_submission():
    """اختبار إرسال فاتورة مشتريات"""
    try:
        data = {
            'supplier_name': 'مورد تجريبي',
            'subtotal': '2000.00',
            'tax_amount': '300.00',
            'discount': '100.00',
            'total_amount': '2200.00',
            'notes': 'فاتورة اختبار للمشتريات'
        }
        
        response = requests.post(f"{BASE_URL}/add_purchase_invoice", data=data, timeout=10)
        
        if response.status_code in [200, 302]:
            log_test("إرسال فاتورة المشتريات", "PASS", 
                    f"تم الإرسال بنجاح - HTTP {response.status_code}")
        else:
            log_test("إرسال فاتورة المشتريات", "FAIL", 
                    f"فشل الإرسال - HTTP {response.status_code}")
            
    except Exception as e:
        log_test("إرسال فاتورة المشتريات", "FAIL", str(e))

def test_server_connection():
    """اختبار الاتصال بالخادم"""
    try:
        response = requests.get(BASE_URL, timeout=5)
        if response.status_code == 200:
            log_test("الاتصال بالخادم", "PASS", "الخادم يعمل بشكل طبيعي")
            return True
        else:
            log_test("الاتصال بالخادم", "FAIL", f"HTTP {response.status_code}")
            return False
    except Exception as e:
        log_test("الاتصال بالخادم", "FAIL", str(e))
        return False

def generate_report():
    """إنشاء تقرير شامل للاختبارات"""
    print("\n" + "="*60)
    print("📊 تقرير اختبار النماذج الجديدة للفواتير")
    print("="*60)
    
    total_tests = len(TEST_RESULTS)
    passed_tests = len([r for r in TEST_RESULTS if r['status'] == 'PASS'])
    failed_tests = len([r for r in TEST_RESULTS if r['status'] == 'FAIL'])
    
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    print(f"📈 إجمالي الاختبارات: {total_tests}")
    print(f"✅ نجح: {passed_tests}")
    print(f"❌ فشل: {failed_tests}")
    print(f"📊 معدل النجاح: {success_rate:.1f}%")
    
    print(f"\n⏰ وقت الاختبار: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if success_rate >= 80:
        print("🎉 النتيجة: النماذج الجديدة تعمل بشكل ممتاز!")
    elif success_rate >= 60:
        print("⚠️ النتيجة: النماذج تحتاج لبعض التحسينات")
    else:
        print("🚨 النتيجة: النماذج تحتاج لإصلاحات جوهرية")
    
    return success_rate

def main():
    """تشغيل جميع الاختبارات"""
    print("🚀 بدء اختبار النماذج الجديدة للفواتير...")
    print("="*60)
    
    # اختبار الاتصال بالخادم أولاً
    if not test_server_connection():
        print("❌ لا يمكن الوصول للخادم. تأكد من تشغيل التطبيق على المنفذ 5000")
        return
    
    # تشغيل الاختبارات
    test_sales_invoice_form()
    test_purchase_invoice_form()
    test_sales_invoice_submission()
    test_purchase_invoice_submission()
    
    # إنشاء التقرير النهائي
    success_rate = generate_report()
    
    # حفظ التقرير في ملف
    with open('new_templates_test_report.txt', 'w', encoding='utf-8') as f:
        f.write("تقرير اختبار النماذج الجديدة للفواتير\n")
        f.write("="*50 + "\n\n")
        for result in TEST_RESULTS:
            f.write(f"{result['test']}: {result['status']}\n")
            if result['details']:
                f.write(f"  التفاصيل: {result['details']}\n")
            f.write(f"  الوقت: {result['timestamp']}\n\n")
        f.write(f"معدل النجاح: {success_rate:.1f}%\n")
    
    print(f"\n💾 تم حفظ التقرير في: new_templates_test_report.txt")

if __name__ == "__main__":
    main()
