#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
اختبار مبسط للشاشة الرئيسية
Simple Main Screen Test
"""

import requests
import json
from datetime import datetime

def test_main_screen_simple():
    """اختبار مبسط للشاشة الرئيسية"""
    
    print("🏠 اختبار الشاشة الرئيسية المبسط...")
    print("=" * 50)
    
    base_url = "http://127.0.0.1:5000"
    results = {
        'total_tests': 0,
        'passed_tests': 0,
        'failed_tests': 0,
        'errors': []
    }
    
    # اختبار الصفحة الرئيسية
    print("🏠 اختبار الصفحة الرئيسية...")
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        results['total_tests'] += 1
        
        if response.status_code == 200:
            print("✅ الصفحة الرئيسية: تعمل بنجاح")
            results['passed_tests'] += 1
            
            # فحص وجود النصوص المهمة
            content = response.text
            if "نظام المحاسبة" in content:
                print("✅ عنوان النظام: موجود")
            else:
                print("❌ عنوان النظام: مفقود")
                results['errors'].append("عنوان النظام مفقود")
                
            if "إجمالي المبيعات" in content:
                print("✅ بطاقة المبيعات: موجودة")
            else:
                print("❌ بطاقة المبيعات: مفقودة")
                results['errors'].append("بطاقة المبيعات مفقودة")
                
            if "العملاء" in content:
                print("✅ بطاقة العملاء: موجودة")
            else:
                print("❌ بطاقة العملاء: مفقودة")
                results['errors'].append("بطاقة العملاء مفقودة")
                
        else:
            print(f"❌ الصفحة الرئيسية: خطأ HTTP {response.status_code}")
            results['failed_tests'] += 1
            results['errors'].append(f"خطأ HTTP {response.status_code} في الصفحة الرئيسية")
            
    except Exception as e:
        print(f"❌ الصفحة الرئيسية: خطأ في الاتصال")
        results['failed_tests'] += 1
        results['errors'].append("خطأ في الاتصال بالصفحة الرئيسية")
    
    print()
    
    # اختبار لوحة التحكم
    print("📊 اختبار لوحة التحكم...")
    try:
        response = requests.get(f"{base_url}/dashboard", timeout=5)
        results['total_tests'] += 1
        
        if response.status_code == 200 or response.status_code == 302:
            print("✅ لوحة التحكم: تعمل بنجاح")
            results['passed_tests'] += 1
        else:
            print(f"❌ لوحة التحكم: خطأ HTTP {response.status_code}")
            results['failed_tests'] += 1
            results['errors'].append(f"خطأ HTTP {response.status_code} في لوحة التحكم")
            
    except Exception as e:
        print(f"❌ لوحة التحكم: خطأ في الاتصال")
        results['failed_tests'] += 1
        results['errors'].append("خطأ في الاتصال بلوحة التحكم")
    
    print()
    
    # اختبار الصفحات الرئيسية
    print("📋 اختبار الصفحات الرئيسية...")
    main_pages = [
        ('/sales', 'المبيعات'),
        ('/customers', 'العملاء'),
        ('/employees', 'الموظفين')
    ]
    
    for url, name in main_pages:
        try:
            response = requests.get(f"{base_url}{url}", timeout=5)
            results['total_tests'] += 1
            
            if response.status_code == 200:
                print(f"✅ صفحة {name}: تعمل")
                results['passed_tests'] += 1
            else:
                print(f"❌ صفحة {name}: خطأ HTTP {response.status_code}")
                results['failed_tests'] += 1
                results['errors'].append(f"خطأ HTTP {response.status_code} في {url}")
                
        except Exception as e:
            print(f"❌ صفحة {name}: خطأ في الاتصال")
            results['failed_tests'] += 1
            results['errors'].append(f"خطأ في الاتصال بـ {url}")
    
    print()
    
    # النتائج النهائية
    print("=" * 50)
    print("📊 النتائج النهائية")
    print("=" * 50)
    
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
        print("🎉 حالة الشاشة الرئيسية: ممتازة")
        status = "ممتازة"
    elif success_rate >= 80:
        print("👍 حالة الشاشة الرئيسية: جيدة")
        status = "جيدة"
    elif success_rate >= 70:
        print("⚠️ حالة الشاشة الرئيسية: تحتاج تحسين")
        status = "تحتاج تحسين"
    else:
        print("❌ حالة الشاشة الرئيسية: تحتاج إصلاح عاجل")
        status = "تحتاج إصلاح"
    
    # حفظ التقرير
    report = {
        'test_date': datetime.now().isoformat(),
        'test_type': 'simple_main_screen_test',
        'results': results,
        'success_rate': success_rate,
        'status': status
    }
    
    with open('simple_main_test_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n📄 تم حفظ التقرير في: simple_main_test_report.json")
    
    return success_rate >= 80

if __name__ == "__main__":
    test_main_screen_simple()
