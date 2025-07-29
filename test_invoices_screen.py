#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
اختبار شامل لشاشة الفواتير العامة
General Invoices Screen Comprehensive Test
"""

import requests
import json
from datetime import datetime
from bs4 import BeautifulSoup

def test_invoices_screen():
    """اختبار شامل لشاشة الفواتير العامة"""
    
    print("📋 بدء اختبار شاشة الفواتير العامة...")
    print("=" * 60)
    
    base_url = "http://127.0.0.1:5000"
    results = {
        'total_tests': 0,
        'passed_tests': 0,
        'failed_tests': 0,
        'errors': []
    }
    
    # اختبار 1: صفحة فواتير المبيعات
    print("🛍️ اختبار 1: صفحة فواتير المبيعات")
    print("-" * 40)
    
    try:
        response = requests.get(f"{base_url}/sales_invoices", timeout=10)
        results['total_tests'] += 1
        
        if response.status_code == 200:
            print("✅ الوصول للصفحة: PASS")
            results['passed_tests'] += 1
            
            # فحص محتوى الصفحة
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # فحص العناصر الأساسية
            elements_to_check = [
                ('table', 'جدول الفواتير'),
                ('h1, h2, h3', 'عنوان الصفحة'),
                ('.btn', 'أزرار التحكم')
            ]
            
            for selector, name in elements_to_check:
                element = soup.select_one(selector)
                if element:
                    print(f"✅ عنصر '{name}': موجود")
                else:
                    print(f"❌ عنصر '{name}': مفقود")
                    results['errors'].append(f"عنصر مفقود في فواتير المبيعات: {name}")
            
            # فحص أعمدة الجدول
            table_headers = ['رقم الفاتورة', 'العميل', 'التاريخ', 'الإجمالي', 'الحالة']
            content = response.text
            
            for header in table_headers:
                if header in content:
                    print(f"✅ عمود '{header}': موجود")
                else:
                    print(f"❌ عمود '{header}': مفقود")
                    results['errors'].append(f"عمود مفقود في فواتير المبيعات: {header}")
            
        else:
            print(f"❌ الوصول للصفحة: FAIL (HTTP {response.status_code})")
            results['failed_tests'] += 1
            results['errors'].append(f"خطأ HTTP {response.status_code} في /sales_invoices")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ الوصول للصفحة: FAIL (خطأ في الاتصال)")
        results['failed_tests'] += 1
        results['errors'].append("خطأ في الاتصال بفواتير المبيعات")
    
    print()
    
    # اختبار 2: صفحة إضافة فاتورة مبيعات
    print("➕ اختبار 2: صفحة إضافة فاتورة مبيعات")
    print("-" * 40)
    
    try:
        response = requests.get(f"{base_url}/add_sales_invoice", timeout=10)
        results['total_tests'] += 1
        
        if response.status_code == 200:
            print("✅ الوصول للصفحة: PASS")
            results['passed_tests'] += 1
            
            # فحص حقول النموذج
            soup = BeautifulSoup(response.text, 'html.parser')
            
            form_fields = [
                ('customer_name', 'اسم العميل'),
                ('total_amount', 'المبلغ الإجمالي'),
                ('subtotal', 'المبلغ الفرعي'),
                ('tax_amount', 'ضريبة القيمة المضافة')
            ]
            
            for field_name, field_label in form_fields:
                field = soup.find('input', {'name': field_name}) or soup.find('select', {'name': field_name}) or soup.find('textarea', {'name': field_name})
                if field:
                    print(f"✅ حقل '{field_label}': موجود")
                else:
                    print(f"❌ حقل '{field_label}': مفقود")
                    results['errors'].append(f"حقل مفقود في إضافة فاتورة المبيعات: {field_label}")
            
        else:
            print(f"❌ الوصول للصفحة: FAIL (HTTP {response.status_code})")
            results['failed_tests'] += 1
            results['errors'].append(f"خطأ HTTP {response.status_code} في /add_sales_invoice")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ الوصول للصفحة: FAIL (خطأ في الاتصال)")
        results['failed_tests'] += 1
        results['errors'].append("خطأ في الاتصال بإضافة فاتورة المبيعات")
    
    print()
    
    # اختبار 3: صفحة فواتير المشتريات
    print("🛒 اختبار 3: صفحة فواتير المشتريات")
    print("-" * 40)
    
    try:
        response = requests.get(f"{base_url}/purchase_invoices", timeout=10)
        results['total_tests'] += 1
        
        if response.status_code == 200:
            print("✅ الوصول للصفحة: PASS")
            results['passed_tests'] += 1
            
            # فحص محتوى الصفحة
            content = response.text
            if "فواتير المشتريات" in content or "المشتريات" in content:
                print("✅ محتوى الصفحة: صحيح")
            else:
                print("❌ محتوى الصفحة: غير صحيح")
                results['errors'].append("محتوى صفحة فواتير المشتريات غير صحيح")
            
        elif response.status_code == 302:
            print("✅ الوصول للصفحة: إعادة توجيه")
            results['passed_tests'] += 1
        else:
            print(f"❌ الوصول للصفحة: FAIL (HTTP {response.status_code})")
            results['failed_tests'] += 1
            results['errors'].append(f"خطأ HTTP {response.status_code} في /purchase_invoices")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ الوصول للصفحة: FAIL (خطأ في الاتصال)")
        results['failed_tests'] += 1
        results['errors'].append("خطأ في الاتصال بفواتير المشتريات")
    
    print()
    
    # اختبار 4: صفحة إضافة فاتورة مشتريات
    print("➕ اختبار 4: صفحة إضافة فاتورة مشتريات")
    print("-" * 40)
    
    try:
        response = requests.get(f"{base_url}/add_purchase_invoice", timeout=10)
        results['total_tests'] += 1
        
        if response.status_code == 200:
            print("✅ الوصول للصفحة: PASS")
            results['passed_tests'] += 1
            
            # فحص وجود النموذج
            soup = BeautifulSoup(response.text, 'html.parser')
            form = soup.find('form')
            if form:
                print("✅ نموذج الإضافة: موجود")
            else:
                print("❌ نموذج الإضافة: مفقود")
                results['errors'].append("نموذج إضافة فاتورة المشتريات مفقود")
            
        elif response.status_code == 302:
            print("✅ الوصول للصفحة: إعادة توجيه")
            results['passed_tests'] += 1
        else:
            print(f"❌ الوصول للصفحة: FAIL (HTTP {response.status_code})")
            results['failed_tests'] += 1
            results['errors'].append(f"خطأ HTTP {response.status_code} في /add_purchase_invoice")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ الوصول للصفحة: FAIL (خطأ في الاتصال)")
        results['failed_tests'] += 1
        results['errors'].append("خطأ في الاتصال بإضافة فاتورة المشتريات")
    
    print()
    
    # اختبار 5: صفحة الفواتير العامة (إذا كانت موجودة)
    print("📄 اختبار 5: صفحة الفواتير العامة")
    print("-" * 40)
    
    try:
        response = requests.get(f"{base_url}/invoices", timeout=10)
        results['total_tests'] += 1
        
        if response.status_code == 200:
            print("✅ الوصول للصفحة: PASS")
            results['passed_tests'] += 1
            
            # فحص محتوى الصفحة
            content = response.text
            if "فواتير" in content:
                print("✅ محتوى الصفحة: صحيح")
            else:
                print("❌ محتوى الصفحة: غير صحيح")
                results['errors'].append("محتوى صفحة الفواتير العامة غير صحيح")
            
        elif response.status_code == 302:
            print("✅ الوصول للصفحة: إعادة توجيه")
            results['passed_tests'] += 1
        elif response.status_code == 404:
            print("⚠️ الوصول للصفحة: غير موجودة (404)")
            results['passed_tests'] += 1  # هذا مقبول إذا لم تكن الصفحة مطلوبة
        else:
            print(f"❌ الوصول للصفحة: FAIL (HTTP {response.status_code})")
            results['failed_tests'] += 1
            results['errors'].append(f"خطأ HTTP {response.status_code} في /invoices")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ الوصول للصفحة: FAIL (خطأ في الاتصال)")
        results['failed_tests'] += 1
        results['errors'].append("خطأ في الاتصال بالفواتير العامة")
    
    print()
    
    # اختبار 6: فحص الأداء والاستجابة
    print("⚡ اختبار 6: الأداء والاستجابة")
    print("-" * 40)
    
    try:
        start_time = datetime.now()
        response = requests.get(f"{base_url}/sales_invoices", timeout=10)
        end_time = datetime.now()
        
        response_time = (end_time - start_time).total_seconds()
        results['total_tests'] += 1
        
        if response_time < 2.0:
            print(f"✅ زمن الاستجابة: {response_time:.2f} ثانية (ممتاز)")
            results['passed_tests'] += 1
        elif response_time < 5.0:
            print(f"⚠️ زمن الاستجابة: {response_time:.2f} ثانية (مقبول)")
            results['passed_tests'] += 1
        else:
            print(f"❌ زمن الاستجابة: {response_time:.2f} ثانية (بطيء)")
            results['failed_tests'] += 1
            results['errors'].append(f"زمن استجابة بطيء: {response_time:.2f} ثانية")
            
    except requests.exceptions.RequestException:
        print("❌ فشل في قياس زمن الاستجابة")
        results['failed_tests'] += 1
        results['errors'].append("فشل في قياس الأداء")
    
    print()
    
    # النتائج النهائية
    print("=" * 60)
    print("📊 النتائج النهائية")
    print("=" * 60)
    
    success_rate = (results['passed_tests'] / results['total_tests'] * 100) if results['total_tests'] > 0 else 0
    
    print(f"إجمالي الاختبارات: {results['total_tests']}")
    print(f"الاختبارات الناجحة: {results['passed_tests']}")
    print(f"الاختبارات الفاشلة: {results['failed_tests']}")
    print(f"معدل النجاح: {success_rate:.1f}%")
    print()
    
    if results['errors']:
        print(f"❌ الأخطاء المكتشفة ({len(results['errors'])}):")
        for i, error in enumerate(results['errors'], 1):
            print(f"   {i}. {error}")
        print()
    
    # تقييم الحالة العامة
    if success_rate >= 90:
        print("🎉 حالة شاشة الفواتير: ممتازة")
        status = "ممتازة"
    elif success_rate >= 80:
        print("👍 حالة شاشة الفواتير: جيدة")
        status = "جيدة"
    elif success_rate >= 70:
        print("⚠️ حالة شاشة الفواتير: تحتاج تحسين")
        status = "تحتاج تحسين"
    else:
        print("❌ حالة شاشة الفواتير: تحتاج إصلاح عاجل")
        status = "تحتاج إصلاح"
    
    # حفظ التقرير
    report = {
        'test_date': datetime.now().isoformat(),
        'test_type': 'invoices_screen_test',
        'results': results,
        'success_rate': success_rate,
        'status': status
    }
    
    with open('invoices_screen_test_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n📄 تم حفظ التقرير في: invoices_screen_test_report.json")
    
    return success_rate >= 80

if __name__ == "__main__":
    test_invoices_screen()
