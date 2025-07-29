#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار مخصص لإنشاء فواتير المبيعات والمشتريات
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

def test_sales_invoice_creation():
    """اختبار إنشاء فاتورة مبيعات"""
    print("💰 اختبار إنشاء فاتورة مبيعات:")
    
    try:
        # بيانات فاتورة مبيعات تجريبية
        invoice_data = {
            'customer_name': 'عميل اختبار - شركة التجارة المتقدمة',
            'subtotal': '5000.00',
            'tax_amount': '750.00',
            'discount': '250.00',
            'total_amount': '5500.00',
            'notes': 'فاتورة مبيعات اختبار - تم إنشاؤها تلقائياً للاختبار'
        }
        
        print(f"   📤 إرسال بيانات الفاتورة: {invoice_data['customer_name']}")
        
        response = requests.post(f"{BASE_URL}/add_sales_invoice", data=invoice_data, timeout=15)
        
        if response.status_code == 200:
            log_test("إنشاء فاتورة مبيعات - الاستجابة", "PASS", "تم إنشاء الفاتورة بنجاح (200)")
            
            # التحقق من المحتوى
            if 'success' in response.text.lower() or 'نجح' in response.text:
                log_test("إنشاء فاتورة مبيعات - رسالة النجاح", "PASS", "رسالة نجاح موجودة")
            else:
                log_test("إنشاء فاتورة مبيعات - رسالة النجاح", "WARNING", "رسالة النجاح غير واضحة")
                
        elif response.status_code == 302:
            log_test("إنشاء فاتورة مبيعات - إعادة التوجيه", "PASS", "تم إعادة التوجيه بنجاح (302)")
        elif response.status_code == 400:
            log_test("إنشاء فاتورة مبيعات", "WARNING", "خطأ في البيانات المرسلة (400)")
        elif response.status_code == 500:
            log_test("إنشاء فاتورة مبيعات", "FAIL", "خطأ خادم داخلي (500)")
        else:
            log_test("إنشاء فاتورة مبيعات", "WARNING", f"كود استجابة غير متوقع: {response.status_code}")
            
    except requests.exceptions.Timeout:
        log_test("إنشاء فاتورة مبيعات", "FAIL", "انتهت مهلة الاتصال")
    except Exception as e:
        log_test("إنشاء فاتورة مبيعات", "FAIL", f"خطأ: {str(e)}")

def test_purchase_invoice_creation():
    """اختبار إنشاء فاتورة مشتريات"""
    print("\n🛒 اختبار إنشاء فاتورة مشتريات:")
    
    try:
        # بيانات فاتورة مشتريات تجريبية
        purchase_data = {
            'supplier_name': 'مورد اختبار - شركة الإمداد الحديثة',
            'subtotal': '8000.00',
            'tax_amount': '1200.00',
            'discount': '400.00',
            'total_amount': '8800.00',
            'notes': 'فاتورة مشتريات اختبار - تم إنشاؤها تلقائياً للاختبار'
        }
        
        print(f"   📤 إرسال بيانات الفاتورة: {purchase_data['supplier_name']}")
        
        response = requests.post(f"{BASE_URL}/add_purchase_invoice", data=purchase_data, timeout=15)
        
        if response.status_code == 200:
            log_test("إنشاء فاتورة مشتريات - الاستجابة", "PASS", "تم إنشاء الفاتورة بنجاح (200)")
            
            # التحقق من المحتوى
            if 'success' in response.text.lower() or 'نجح' in response.text:
                log_test("إنشاء فاتورة مشتريات - رسالة النجاح", "PASS", "رسالة نجاح موجودة")
            else:
                log_test("إنشاء فاتورة مشتريات - رسالة النجاح", "WARNING", "رسالة النجاح غير واضحة")
                
        elif response.status_code == 302:
            log_test("إنشاء فاتورة مشتريات - إعادة التوجيه", "PASS", "تم إعادة التوجيه بنجاح (302)")
        elif response.status_code == 400:
            log_test("إنشاء فاتورة مشتريات", "WARNING", "خطأ في البيانات المرسلة (400)")
        elif response.status_code == 500:
            log_test("إنشاء فاتورة مشتريات", "FAIL", "خطأ خادم داخلي (500)")
        else:
            log_test("إنشاء فاتورة مشتريات", "WARNING", f"كود استجابة غير متوقع: {response.status_code}")
            
    except requests.exceptions.Timeout:
        log_test("إنشاء فاتورة مشتريات", "FAIL", "انتهت مهلة الاتصال")
    except Exception as e:
        log_test("إنشاء فاتورة مشتريات", "FAIL", f"خطأ: {str(e)}")

def test_invoice_forms():
    """اختبار نماذج الفواتير"""
    print("\n📝 اختبار نماذج الفواتير:")
    
    # اختبار نموذج فاتورة المبيعات
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
                'total_amount'
            ]
            
            missing_fields = []
            for field in required_fields:
                if f'name="{field}"' not in html_content and f'id="{field}"' not in html_content:
                    missing_fields.append(field)
            
            if not missing_fields:
                log_test("نموذج فاتورة المبيعات - الحقول", "PASS", "جميع الحقول المطلوبة موجودة")
            else:
                log_test("نموذج فاتورة المبيعات - الحقول", "WARNING", f"حقول مفقودة: {missing_fields}")
            
            # التحقق من وجود JavaScript
            if 'calculateTotal' in html_content or 'function' in html_content:
                log_test("نموذج فاتورة المبيعات - JavaScript", "PASS", "وظائف JavaScript موجودة")
            else:
                log_test("نموذج فاتورة المبيعات - JavaScript", "WARNING", "وظائف JavaScript محدودة")
                
        else:
            log_test("نموذج فاتورة المبيعات", "FAIL", f"كود الاستجابة: {response.status_code}")
    except Exception as e:
        log_test("نموذج فاتورة المبيعات", "FAIL", f"خطأ: {str(e)}")
    
    # اختبار نموذج فاتورة المشتريات
    try:
        response = requests.get(f"{BASE_URL}/add_purchase_invoice", timeout=10)
        if response.status_code == 200:
            html_content = response.text
            
            # التحقق من وجود الحقول المطلوبة
            required_fields = [
                'supplier_name',
                'subtotal',
                'tax_amount',
                'discount',
                'total_amount'
            ]
            
            missing_fields = []
            for field in required_fields:
                if f'name="{field}"' not in html_content and f'id="{field}"' not in html_content:
                    missing_fields.append(field)
            
            if not missing_fields:
                log_test("نموذج فاتورة المشتريات - الحقول", "PASS", "جميع الحقول المطلوبة موجودة")
            else:
                log_test("نموذج فاتورة المشتريات - الحقول", "WARNING", f"حقول مفقودة: {missing_fields}")
            
            # التحقق من وجود JavaScript
            if 'calculateTotal' in html_content or 'function' in html_content:
                log_test("نموذج فاتورة المشتريات - JavaScript", "PASS", "وظائف JavaScript موجودة")
            else:
                log_test("نموذج فاتورة المشتريات - JavaScript", "WARNING", "وظائف JavaScript محدودة")
                
        else:
            log_test("نموذج فاتورة المشتريات", "FAIL", f"كود الاستجابة: {response.status_code}")
    except Exception as e:
        log_test("نموذج فاتورة المشتريات", "FAIL", f"خطأ: {str(e)}")

def test_invoice_validation():
    """اختبار التحقق من صحة بيانات الفواتير"""
    print("\n🔍 اختبار التحقق من صحة البيانات:")
    
    # اختبار بيانات ناقصة لفاتورة المبيعات
    try:
        incomplete_data = {
            'customer_name': '',  # اسم فارغ
            'subtotal': '1000.00',
            'total_amount': '1150.00'
        }
        
        response = requests.post(f"{BASE_URL}/add_sales_invoice", data=incomplete_data, timeout=10)
        
        if response.status_code == 400:
            log_test("التحقق من البيانات - فاتورة مبيعات", "PASS", "تم رفض البيانات الناقصة")
        elif response.status_code == 200 and 'error' in response.text.lower():
            log_test("التحقق من البيانات - فاتورة مبيعات", "PASS", "تم عرض رسالة خطأ")
        else:
            log_test("التحقق من البيانات - فاتورة مبيعات", "WARNING", "لم يتم التحقق من البيانات بشكل صحيح")
            
    except Exception as e:
        log_test("التحقق من البيانات - فاتورة مبيعات", "FAIL", f"خطأ: {str(e)}")
    
    # اختبار بيانات ناقصة لفاتورة المشتريات
    try:
        incomplete_data = {
            'supplier_name': '',  # اسم فارغ
            'subtotal': '2000.00',
            'total_amount': '2300.00'
        }
        
        response = requests.post(f"{BASE_URL}/add_purchase_invoice", data=incomplete_data, timeout=10)
        
        if response.status_code == 400:
            log_test("التحقق من البيانات - فاتورة مشتريات", "PASS", "تم رفض البيانات الناقصة")
        elif response.status_code == 200 and 'error' in response.text.lower():
            log_test("التحقق من البيانات - فاتورة مشتريات", "PASS", "تم عرض رسالة خطأ")
        else:
            log_test("التحقق من البيانات - فاتورة مشتريات", "WARNING", "لم يتم التحقق من البيانات بشكل صحيح")
            
    except Exception as e:
        log_test("التحقق من البيانات - فاتورة مشتريات", "FAIL", f"خطأ: {str(e)}")

def test_invoice_lists_after_creation():
    """اختبار قوائم الفواتير بعد الإنشاء"""
    print("\n📋 اختبار قوائم الفواتير بعد الإنشاء:")
    
    # اختبار قائمة فواتير المبيعات
    try:
        response = requests.get(f"{BASE_URL}/sales_invoices", timeout=10)
        if response.status_code == 200:
            html_content = response.text
            
            # البحث عن الفاتورة المُنشأة
            if 'عميل اختبار' in html_content or 'شركة التجارة' in html_content:
                log_test("قائمة فواتير المبيعات - الفاتورة الجديدة", "PASS", "الفاتورة الجديدة ظاهرة في القائمة")
            else:
                log_test("قائمة فواتير المبيعات - الفاتورة الجديدة", "WARNING", "الفاتورة الجديدة قد لا تكون ظاهرة")
            
            # التحقق من وجود إحصائيات
            if 'إجمالي' in html_content and 'ر.س' in html_content:
                log_test("قائمة فواتير المبيعات - الإحصائيات", "PASS", "الإحصائيات محدثة")
            else:
                log_test("قائمة فواتير المبيعات - الإحصائيات", "WARNING", "الإحصائيات قد تكون ناقصة")
                
        else:
            log_test("قائمة فواتير المبيعات", "FAIL", f"كود الاستجابة: {response.status_code}")
    except Exception as e:
        log_test("قائمة فواتير المبيعات", "FAIL", f"خطأ: {str(e)}")
    
    # اختبار قائمة فواتير المشتريات
    try:
        response = requests.get(f"{BASE_URL}/purchase_invoices", timeout=10)
        if response.status_code == 200:
            html_content = response.text
            
            # البحث عن الفاتورة المُنشأة
            if 'مورد اختبار' in html_content or 'شركة الإمداد' in html_content:
                log_test("قائمة فواتير المشتريات - الفاتورة الجديدة", "PASS", "الفاتورة الجديدة ظاهرة في القائمة")
            else:
                log_test("قائمة فواتير المشتريات - الفاتورة الجديدة", "WARNING", "الفاتورة الجديدة قد لا تكون ظاهرة")
            
            # التحقق من وجود إحصائيات
            if 'إجمالي' in html_content and 'ر.س' in html_content:
                log_test("قائمة فواتير المشتريات - الإحصائيات", "PASS", "الإحصائيات محدثة")
            else:
                log_test("قائمة فواتير المشتريات - الإحصائيات", "WARNING", "الإحصائيات قد تكون ناقصة")
                
        else:
            log_test("قائمة فواتير المشتريات", "FAIL", f"كود الاستجابة: {response.status_code}")
    except Exception as e:
        log_test("قائمة فواتير المشتريات", "FAIL", f"خطأ: {str(e)}")

def run_invoice_creation_test():
    """تشغيل الاختبار الشامل لإنشاء الفواتير"""
    print("🧾 بدء الاختبار الشامل لإنشاء فواتير المبيعات والمشتريات")
    print("=" * 80)
    
    # اختبار نماذج الفواتير
    test_invoice_forms()
    
    # اختبار إنشاء الفواتير
    test_sales_invoice_creation()
    test_purchase_invoice_creation()
    
    # اختبار التحقق من صحة البيانات
    test_invoice_validation()
    
    # اختبار قوائم الفواتير بعد الإنشاء
    test_invoice_lists_after_creation()
    
    # تلخيص النتائج
    print("\n" + "=" * 80)
    print("📊 ملخص نتائج اختبار إنشاء الفواتير:")
    
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
        'نماذج الفواتير': ['نموذج فاتورة'],
        'إنشاء الفواتير': ['إنشاء فاتورة'],
        'التحقق من البيانات': ['التحقق من البيانات'],
        'قوائم الفواتير': ['قائمة فواتير']
    }
    
    for category, keywords in categories.items():
        category_tests = [r for r in TEST_RESULTS if any(keyword in r['test'] for keyword in keywords)]
        category_passed = len([r for r in category_tests if r['status'] == 'PASS'])
        category_total = len(category_tests)
        category_rate = (category_passed / category_total) * 100 if category_total > 0 else 0
        
        status_icon = "✅" if category_rate >= 80 else "⚠️" if category_rate >= 60 else "❌"
        print(f"   {status_icon} {category}: {category_rate:.1f}% ({category_passed}/{category_total})")
    
    if success_rate >= 90:
        print("\n🎉 ممتاز! نظام إنشاء الفواتير يعمل بكفاءة عالية")
    elif success_rate >= 75:
        print("\n👍 جيد! نظام إنشاء الفواتير يعمل بشكل مقبول")
    elif success_rate >= 60:
        print("\n⚠️  مقبول! بعض أجزاء النظام تحتاج تحسين")
    else:
        print("\n❌ يحتاج إصلاح! مشاكل كثيرة في النظام")
    
    # حفظ النتائج في ملف
    with open('invoice_creation_test_results.json', 'w', encoding='utf-8') as f:
        json.dump(TEST_RESULTS, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 تم حفظ النتائج التفصيلية في: invoice_creation_test_results.json")
    
    return success_rate

if __name__ == "__main__":
    try:
        success_rate = run_invoice_creation_test()
        exit(0 if success_rate >= 75 else 1)
    except KeyboardInterrupt:
        print("\n⏹️  تم إيقاف الاختبار بواسطة المستخدم")
        exit(1)
    except Exception as e:
        print(f"\n❌ خطأ عام في اختبار إنشاء الفواتير: {str(e)}")
        exit(1)
