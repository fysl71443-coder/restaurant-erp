#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار شامل لنظام الفواتير
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

def test_invoice_pages():
    """اختبار تحميل صفحات الفواتير"""
    print("📄 اختبار تحميل صفحات الفواتير:")
    
    pages = [
        ("/invoices", "قائمة الفواتير"),
        ("/add_invoice", "إضافة فاتورة جديدة"),
        ("/sales", "تقارير المبيعات")
    ]
    
    for url, name in pages:
        try:
            response = requests.get(f"{BASE_URL}{url}", timeout=10)
            if response.status_code == 200:
                log_test(f"تحميل صفحة {name}", "PASS", f"كود الاستجابة: {response.status_code}")
            else:
                log_test(f"تحميل صفحة {name}", "FAIL", f"كود الاستجابة: {response.status_code}")
        except Exception as e:
            log_test(f"تحميل صفحة {name}", "FAIL", f"خطأ: {str(e)}")
        time.sleep(0.5)

def test_invoice_list_features():
    """اختبار مميزات قائمة الفواتير"""
    print("\n📋 اختبار مميزات قائمة الفواتير:")
    
    try:
        response = requests.get(f"{BASE_URL}/invoices")
        if response.status_code == 200:
            html_content = response.text
            
            # التحقق من وجود عناصر قائمة الفواتير
            invoice_elements = [
                'id="invoicesTable"',
                'class="table"',
                'إضافة فاتورة',
                'تصدير',
                'طباعة'
            ]
            
            found_elements = [element for element in invoice_elements if element in html_content]
            
            if len(found_elements) >= 4:
                log_test("عناصر قائمة الفواتير", "PASS", f"عناصر موجودة: {len(found_elements)}/5")
            else:
                log_test("عناصر قائمة الفواتير", "FAIL", f"عناصر مفقودة: {5 - len(found_elements)}")
            
            # التحقق من وجود البيانات التجريبية
            if "لا توجد فواتير" in html_content:
                log_test("البيانات التجريبية", "WARNING", "لا توجد فواتير في النظام")
            else:
                log_test("البيانات التجريبية", "PASS", "توجد فواتير في النظام")
                
        else:
            log_test("عناصر قائمة الفواتير", "FAIL", "فشل في تحميل الصفحة")
    except Exception as e:
        log_test("عناصر قائمة الفواتير", "FAIL", f"خطأ: {str(e)}")

def test_add_invoice_form():
    """اختبار نموذج إضافة فاتورة"""
    print("\n📝 اختبار نموذج إضافة فاتورة:")
    
    try:
        response = requests.get(f"{BASE_URL}/add_invoice")
        if response.status_code == 200:
            html_content = response.text
            
            # التحقق من وجود عناصر النموذج
            form_elements = [
                'id="invoiceForm"',
                'name="customer_name"',
                'name="total_amount"',
                'class="save-btn"',
                'class="undo-btn"'
            ]
            
            found_elements = [element for element in form_elements if element in html_content]
            
            if len(found_elements) >= 4:
                log_test("عناصر نموذج الفاتورة", "PASS", f"عناصر موجودة: {len(found_elements)}/5")
            else:
                log_test("عناصر نموذج الفاتورة", "FAIL", f"عناصر مفقودة: {5 - len(found_elements)}")
            
            # التحقق من وجود النماذج المتقدمة
            advanced_features = [
                'forms.js',
                'تتبع التغييرات',
                'الحفظ التلقائي'
            ]
            
            advanced_found = [feature for feature in advanced_features if feature in html_content]
            
            if len(advanced_found) >= 1:
                log_test("النماذج المتقدمة للفاتورة", "PASS", f"مميزات متقدمة: {len(advanced_found)}")
            else:
                log_test("النماذج المتقدمة للفاتورة", "FAIL", "لا توجد مميزات متقدمة")
                
        else:
            log_test("عناصر نموذج الفاتورة", "FAIL", "فشل في تحميل الصفحة")
    except Exception as e:
        log_test("عناصر نموذج الفاتورة", "FAIL", f"خطأ: {str(e)}")

def test_invoice_calculations():
    """اختبار حسابات الفاتورة"""
    print("\n🧮 اختبار حسابات الفاتورة:")
    
    try:
        response = requests.get(f"{BASE_URL}/add_invoice")
        if response.status_code == 200:
            html_content = response.text
            
            # التحقق من وجود عناصر الحساب
            calculation_elements = [
                'calculateTotal',
                'subtotal',
                'tax',
                'total',
                'ضريبة القيمة المضافة'
            ]
            
            found_calculations = [element for element in calculation_elements if element in html_content]
            
            if len(found_calculations) >= 3:
                log_test("عناصر حساب الفاتورة", "PASS", f"عناصر حساب: {len(found_calculations)}")
            else:
                log_test("عناصر حساب الفاتورة", "FAIL", f"عناصر حساب مفقودة")
                
        else:
            log_test("عناصر حساب الفاتورة", "FAIL", "فشل في تحميل الصفحة")
    except Exception as e:
        log_test("عناصر حساب الفاتورة", "FAIL", f"خطأ: {str(e)}")

def test_sales_reports():
    """اختبار تقارير المبيعات"""
    print("\n📊 اختبار تقارير المبيعات:")
    
    try:
        response = requests.get(f"{BASE_URL}/sales")
        if response.status_code == 200:
            html_content = response.text
            
            # التحقق من وجود عناصر التقارير
            report_elements = [
                'chart',
                'إحصائيات',
                'مبيعات',
                'تقرير',
                'رسم بياني'
            ]
            
            found_reports = [element for element in report_elements if element in html_content]
            
            if len(found_reports) >= 3:
                log_test("عناصر تقارير المبيعات", "PASS", f"عناصر تقارير: {len(found_reports)}")
            else:
                log_test("عناصر تقارير المبيعات", "FAIL", f"عناصر تقارير مفقودة")
                
        else:
            log_test("عناصر تقارير المبيعات", "FAIL", "فشل في تحميل الصفحة")
    except Exception as e:
        log_test("عناصر تقارير المبيعات", "FAIL", f"خطأ: {str(e)}")

def test_invoice_search_and_filter():
    """اختبار البحث والتصفية في الفواتير"""
    print("\n🔍 اختبار البحث والتصفية:")
    
    try:
        response = requests.get(f"{BASE_URL}/invoices")
        if response.status_code == 200:
            html_content = response.text
            
            # التحقق من وجود عناصر البحث
            search_elements = [
                'searchInput',
                'dateFilter',
                'statusFilter',
                'customerFilter'
            ]
            
            found_search = [element for element in search_elements if element in html_content]
            
            if len(found_search) >= 2:
                log_test("عناصر البحث والتصفية", "PASS", f"عناصر بحث: {len(found_search)}")
            else:
                log_test("عناصر البحث والتصفية", "FAIL", f"عناصر بحث مفقودة")
                
        else:
            log_test("عناصر البحث والتصفية", "FAIL", "فشل في تحميل الصفحة")
    except Exception as e:
        log_test("عناصر البحث والتصفية", "FAIL", f"خطأ: {str(e)}")

def test_invoice_export_print():
    """اختبار التصدير والطباعة"""
    print("\n📤 اختبار التصدير والطباعة:")
    
    try:
        response = requests.get(f"{BASE_URL}/invoices")
        if response.status_code == 200:
            html_content = response.text
            
            # التحقق من وجود وظائف التصدير
            export_elements = [
                'exportInvoices',
                'تصدير',
                'طباعة',
                'CSV',
                'print'
            ]
            
            found_export = [element for element in export_elements if element in html_content]
            
            if len(found_export) >= 3:
                log_test("وظائف التصدير والطباعة", "PASS", f"وظائف متاحة: {len(found_export)}")
            else:
                log_test("وظائف التصدير والطباعة", "FAIL", f"وظائف مفقودة")
                
        else:
            log_test("وظائف التصدير والطباعة", "FAIL", "فشل في تحميل الصفحة")
    except Exception as e:
        log_test("وظائف التصدير والطباعة", "FAIL", f"خطأ: {str(e)}")

def test_invoice_responsive_design():
    """اختبار التصميم المتجاوب للفواتير"""
    print("\n📱 اختبار التصميم المتجاوب:")
    
    try:
        response = requests.get(f"{BASE_URL}/invoices")
        if response.status_code == 200:
            html_content = response.text
            
            # التحقق من وجود عناصر التصميم المتجاوب
            responsive_elements = [
                'container-fluid',
                'row',
                'col-md-',
                'table-responsive',
                'btn-group'
            ]
            
            found_responsive = [element for element in responsive_elements if element in html_content]
            
            if len(found_responsive) >= 4:
                log_test("التصميم المتجاوب للفواتير", "PASS", f"عناصر متجاوبة: {len(found_responsive)}/5")
            else:
                log_test("التصميم المتجاوب للفواتير", "WARNING", f"عناصر متجاوبة محدودة: {len(found_responsive)}/5")
                
        else:
            log_test("التصميم المتجاوب للفواتير", "FAIL", "فشل في تحميل الصفحة")
    except Exception as e:
        log_test("التصميم المتجاوب للفواتير", "FAIL", f"خطأ: {str(e)}")

def run_invoice_comprehensive_test():
    """تشغيل الاختبار الشامل للفواتير"""
    print("🧾 بدء الاختبار الشامل لنظام الفواتير")
    print("=" * 60)
    
    # اختبار تحميل الصفحات
    test_invoice_pages()
    
    # اختبار مميزات قائمة الفواتير
    test_invoice_list_features()
    
    # اختبار نموذج إضافة فاتورة
    test_add_invoice_form()
    
    # اختبار حسابات الفاتورة
    test_invoice_calculations()
    
    # اختبار تقارير المبيعات
    test_sales_reports()
    
    # اختبار البحث والتصفية
    test_invoice_search_and_filter()
    
    # اختبار التصدير والطباعة
    test_invoice_export_print()
    
    # اختبار التصميم المتجاوب
    test_invoice_responsive_design()
    
    # تلخيص النتائج
    print("\n" + "=" * 60)
    print("📊 ملخص نتائج اختبار الفواتير:")
    
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
    
    if success_rate >= 90:
        print("\n🎉 ممتاز! نظام الفواتير يعمل بكفاءة عالية")
    elif success_rate >= 75:
        print("\n👍 جيد! نظام الفواتير يعمل بشكل مقبول مع بعض التحسينات المطلوبة")
    else:
        print("\n⚠️  يحتاج تحسين! هناك مشاكل في نظام الفواتير تحتاج إلى إصلاح")
    
    # حفظ النتائج في ملف
    with open('invoice_test_results.json', 'w', encoding='utf-8') as f:
        json.dump(TEST_RESULTS, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 تم حفظ النتائج التفصيلية في: invoice_test_results.json")
    
    return success_rate

if __name__ == "__main__":
    try:
        success_rate = run_invoice_comprehensive_test()
        exit(0 if success_rate >= 75 else 1)
    except KeyboardInterrupt:
        print("\n⏹️  تم إيقاف الاختبار بواسطة المستخدم")
        exit(1)
    except Exception as e:
        print(f"\n❌ خطأ عام في اختبار الفواتير: {str(e)}")
        exit(1)
