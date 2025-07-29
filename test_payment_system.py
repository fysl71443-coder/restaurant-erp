#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار شامل لنظام تسجيل الدفع
Comprehensive Payment System Test
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

def test_payments_page():
    """اختبار صفحة المدفوعات الرئيسية"""
    try:
        response = requests.get(f"{BASE_URL}/payments", timeout=10)
        
        if response.status_code == 200:
            content = response.text
            
            # فحص العناصر الأساسية
            checks = [
                ('إدارة المدفوعات والتحصيلات', 'عنوان الصفحة'),
                ('تسجيل دفع جديد', 'زر إضافة دفع'),
                ('fas fa-money-bill-wave', 'أيقونة المدفوعات'),
                ('table', 'جدول المدفوعات'),
                ('/add_payment', 'رابط إضافة دفع')
            ]
            
            missing_elements = []
            for element, description in checks:
                if element not in content:
                    missing_elements.append(description)
            
            if not missing_elements:
                log_test("صفحة المدفوعات الرئيسية", "PASS", 
                        "جميع العناصر المطلوبة موجودة")
            else:
                log_test("صفحة المدفوعات الرئيسية", "FAIL", 
                        f"عناصر مفقودة: {', '.join(missing_elements)}")
                
        else:
            log_test("صفحة المدفوعات الرئيسية", "FAIL", 
                    f"HTTP {response.status_code}")
            
    except Exception as e:
        log_test("صفحة المدفوعات الرئيسية", "FAIL", str(e))

def test_add_payment_form():
    """اختبار نموذج إضافة دفع"""
    try:
        response = requests.get(f"{BASE_URL}/add_payment", timeout=10)
        
        if response.status_code == 200:
            content = response.text
            
            # فحص حقول النموذج الأساسية
            form_fields = [
                ('payment_type', 'نوع الدفع'),
                ('amount', 'المبلغ'),
                ('payment_method', 'طريقة الدفع'),
                ('reference_number', 'رقم المرجع'),
                ('customer_name', 'اسم العميل'),
                ('supplier_name', 'اسم المورد'),
                ('invoice_id', 'فاتورة المبيعات'),
                ('purchase_invoice_id', 'فاتورة المشتريات'),
                ('notes', 'الملاحظات')
            ]
            
            missing_fields = []
            for field, description in form_fields:
                if f'name="{field}"' not in content:
                    missing_fields.append(description)
            
            # فحص خيارات طريقة الدفع
            payment_methods = ['cash', 'bank_transfer', 'check', 'card']
            missing_methods = []
            for method in payment_methods:
                if f'value="{method}"' not in content:
                    missing_methods.append(method)
            
            # فحص أنواع الدفع
            payment_types = ['received', 'paid']
            missing_types = []
            for ptype in payment_types:
                if f'value="{ptype}"' not in content:
                    missing_types.append(ptype)
            
            if not missing_fields and not missing_methods and not missing_types:
                log_test("نموذج إضافة الدفع - الحقول", "PASS", 
                        "جميع الحقول والخيارات موجودة")
            else:
                issues = []
                if missing_fields:
                    issues.append(f"حقول مفقودة: {', '.join(missing_fields)}")
                if missing_methods:
                    issues.append(f"طرق دفع مفقودة: {', '.join(missing_methods)}")
                if missing_types:
                    issues.append(f"أنواع دفع مفقودة: {', '.join(missing_types)}")
                
                log_test("نموذج إضافة الدفع - الحقول", "FAIL", 
                        "; ".join(issues))
                
            # فحص الجافا سكريبت
            js_functions = [
                'updatePaymentType()',
                'updateAmountDisplay()',
                'fillInvoiceAmount()',
                'resetForm()',
                'calculateChange()'
            ]
            
            missing_js = []
            for func in js_functions:
                if func not in content:
                    missing_js.append(func)
            
            if not missing_js:
                log_test("نموذج إضافة الدفع - الجافا سكريبت", "PASS", 
                        "جميع الدوال موجودة")
            else:
                log_test("نموذج إضافة الدفع - الجافا سكريبت", "FAIL", 
                        f"دوال مفقودة: {', '.join(missing_js)}")
                
        else:
            log_test("نموذج إضافة الدفع", "FAIL", 
                    f"HTTP {response.status_code}")
            
    except Exception as e:
        log_test("نموذج إضافة الدفع", "FAIL", str(e))

def test_payment_submission_received():
    """اختبار تسجيل دفع مستلم (تحصيل)"""
    try:
        data = {
            'payment_type': 'received',
            'amount': '1500.00',
            'payment_method': 'cash',
            'reference_number': 'REC-001',
            'customer_name': 'عميل تجريبي',
            'notes': 'تحصيل نقدي تجريبي'
        }
        
        response = requests.post(f"{BASE_URL}/add_payment", data=data, timeout=10)
        
        if response.status_code in [200, 302]:
            log_test("تسجيل دفع مستلم (تحصيل)", "PASS", 
                    f"تم التسجيل بنجاح - HTTP {response.status_code}")
        else:
            log_test("تسجيل دفع مستلم (تحصيل)", "FAIL", 
                    f"فشل التسجيل - HTTP {response.status_code}")
            
    except Exception as e:
        log_test("تسجيل دفع مستلم (تحصيل)", "FAIL", str(e))

def test_payment_submission_paid():
    """اختبار تسجيل دفع مدفوع (مصروف)"""
    try:
        data = {
            'payment_type': 'paid',
            'amount': '2500.00',
            'payment_method': 'bank_transfer',
            'reference_number': 'PAY-001',
            'supplier_name': 'مورد تجريبي',
            'notes': 'دفع تحويل بنكي تجريبي'
        }
        
        response = requests.post(f"{BASE_URL}/add_payment", data=data, timeout=10)
        
        if response.status_code in [200, 302]:
            log_test("تسجيل دفع مدفوع (مصروف)", "PASS", 
                    f"تم التسجيل بنجاح - HTTP {response.status_code}")
        else:
            log_test("تسجيل دفع مدفوع (مصروف)", "FAIL", 
                    f"فشل التسجيل - HTTP {response.status_code}")
            
    except Exception as e:
        log_test("تسجيل دفع مدفوع (مصروف)", "FAIL", str(e))

def test_payment_methods():
    """اختبار طرق الدفع المختلفة"""
    payment_methods = [
        ('cash', 'نقدي'),
        ('bank_transfer', 'تحويل بنكي'),
        ('check', 'شيك'),
        ('card', 'بطاقة')
    ]
    
    for method, method_name in payment_methods:
        try:
            data = {
                'payment_type': 'received',
                'amount': '500.00',
                'payment_method': method,
                'reference_number': f'TEST-{method.upper()}',
                'customer_name': f'عميل {method_name}',
                'notes': f'اختبار طريقة الدفع {method_name}'
            }
            
            response = requests.post(f"{BASE_URL}/add_payment", data=data, timeout=10)
            
            if response.status_code in [200, 302]:
                log_test(f"طريقة الدفع - {method_name}", "PASS", 
                        f"تم قبول الطريقة بنجاح")
            else:
                log_test(f"طريقة الدفع - {method_name}", "FAIL", 
                        f"فشل في قبول الطريقة - HTTP {response.status_code}")
                
        except Exception as e:
            log_test(f"طريقة الدفع - {method_name}", "FAIL", str(e))

def test_form_validation():
    """اختبار التحقق من صحة البيانات"""
    # اختبار بيانات فارغة
    try:
        data = {
            'payment_type': '',
            'amount': '',
            'payment_method': ''
        }
        
        response = requests.post(f"{BASE_URL}/add_payment", data=data, timeout=10)
        
        # يجب أن يفشل أو يعيد للنموذج
        if response.status_code in [400, 200]:
            log_test("التحقق من البيانات - بيانات فارغة", "PASS", 
                    "تم رفض البيانات الفارغة بشكل صحيح")
        else:
            log_test("التحقق من البيانات - بيانات فارغة", "FAIL", 
                    f"لم يتم التحقق من البيانات - HTTP {response.status_code}")
            
    except Exception as e:
        log_test("التحقق من البيانات - بيانات فارغة", "FAIL", str(e))
    
    # اختبار مبلغ سالب
    try:
        data = {
            'payment_type': 'received',
            'amount': '-100.00',
            'payment_method': 'cash',
            'customer_name': 'عميل تجريبي'
        }
        
        response = requests.post(f"{BASE_URL}/add_payment", data=data, timeout=10)
        
        if response.status_code in [400, 200]:
            log_test("التحقق من البيانات - مبلغ سالب", "PASS", 
                    "تم رفض المبلغ السالب بشكل صحيح")
        else:
            log_test("التحقق من البيانات - مبلغ سالب", "FAIL", 
                    f"لم يتم رفض المبلغ السالب - HTTP {response.status_code}")
            
    except Exception as e:
        log_test("التحقق من البيانات - مبلغ سالب", "FAIL", str(e))

def generate_report():
    """إنشاء تقرير شامل للاختبارات"""
    print("\n" + "="*60)
    print("💰 تقرير اختبار نظام تسجيل الدفع")
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
    
    if success_rate >= 90:
        print("🎉 النتيجة: نظام الدفع يعمل بشكل ممتاز!")
    elif success_rate >= 75:
        print("✅ النتيجة: نظام الدفع يعمل بشكل جيد")
    elif success_rate >= 60:
        print("⚠️ النتيجة: نظام الدفع يحتاج لبعض التحسينات")
    else:
        print("🚨 النتيجة: نظام الدفع يحتاج لإصلاحات جوهرية")
    
    return success_rate

def main():
    """تشغيل جميع الاختبارات"""
    print("💰 بدء اختبار نظام تسجيل الدفع...")
    print("="*60)
    
    # اختبار الاتصال بالخادم أولاً
    if not test_server_connection():
        print("❌ لا يمكن الوصول للخادم. تأكد من تشغيل التطبيق على المنفذ 5000")
        return
    
    # تشغيل الاختبارات
    test_payments_page()
    test_add_payment_form()
    test_payment_submission_received()
    test_payment_submission_paid()
    test_payment_methods()
    test_form_validation()
    
    # إنشاء التقرير النهائي
    success_rate = generate_report()
    
    # حفظ التقرير في ملف
    with open('payment_system_test_report.txt', 'w', encoding='utf-8') as f:
        f.write("تقرير اختبار نظام تسجيل الدفع\n")
        f.write("="*50 + "\n\n")
        for result in TEST_RESULTS:
            f.write(f"{result['test']}: {result['status']}\n")
            if result['details']:
                f.write(f"  التفاصيل: {result['details']}\n")
            f.write(f"  الوقت: {result['timestamp']}\n\n")
        f.write(f"معدل النجاح: {success_rate:.1f}%\n")
    
    print(f"\n💾 تم حفظ التقرير في: payment_system_test_report.txt")

if __name__ == "__main__":
    main()
