#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
اختبار شامل للشاشة الرئيسية
Main Screen Comprehensive Test
"""

import requests
import json
from datetime import datetime
from bs4 import BeautifulSoup

def test_main_screen():
    """اختبار شامل للشاشة الرئيسية"""
    
    print("🏠 بدء اختبار الشاشة الرئيسية...")
    print("=" * 60)
    
    base_url = "http://127.0.0.1:5000"
    results = {
        'total_tests': 0,
        'passed_tests': 0,
        'failed_tests': 0,
        'errors': []
    }
    
    # اختبار 1: الوصول للشاشة الرئيسية
    print("🏠 اختبار 1: الشاشة الرئيسية")
    print("-" * 40)
    
    try:
        response = requests.get(f"{base_url}/", timeout=10)
        results['total_tests'] += 1
        
        if response.status_code == 200:
            print("✅ الوصول للصفحة: PASS")
            results['passed_tests'] += 1
            
            # فحص محتوى الصفحة
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # فحص العناصر الأساسية
            elements_to_check = [
                ('title', 'عنوان الصفحة'),
                ('.navbar', 'شريط التنقل'),
                ('.container', 'الحاوية الرئيسية'),
                ('footer', 'التذييل')
            ]
            
            for selector, name in elements_to_check:
                element = soup.select_one(selector)
                if element:
                    print(f"✅ عنصر '{name}': موجود")
                else:
                    print(f"❌ عنصر '{name}': مفقود")
                    results['errors'].append(f"عنصر مفقود: {name}")
            
        else:
            print(f"❌ الوصول للصفحة: FAIL (HTTP {response.status_code})")
            results['failed_tests'] += 1
            results['errors'].append(f"خطأ HTTP {response.status_code} في /")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ الوصول للصفحة: FAIL (خطأ في الاتصال)")
        results['failed_tests'] += 1
        results['errors'].append("خطأ في الاتصال بالخادم")
    
    print()
    
    # اختبار 2: الوصول لصفحة لوحة التحكم
    print("📊 اختبار 2: لوحة التحكم")
    print("-" * 40)
    
    try:
        response = requests.get(f"{base_url}/dashboard", timeout=10)
        results['total_tests'] += 1
        
        if response.status_code == 200:
            print("✅ الوصول للصفحة: PASS")
            results['passed_tests'] += 1
            
            # فحص محتوى لوحة التحكم
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # فحص البطاقات الإحصائية
            stats_cards = [
                'إجمالي المبيعات',
                'إجمالي المشتريات', 
                'عدد الموظفين',
                'الرصيد النقدي'
            ]
            
            for card_name in stats_cards:
                # البحث عن النص في الصفحة
                if card_name in response.text:
                    print(f"✅ بطاقة '{card_name}': موجودة")
                else:
                    print(f"❌ بطاقة '{card_name}': مفقودة")
                    results['errors'].append(f"بطاقة مفقودة: {card_name}")
            
        else:
            print(f"❌ الوصول للصفحة: FAIL (HTTP {response.status_code})")
            results['failed_tests'] += 1
            results['errors'].append(f"خطأ HTTP {response.status_code} في /dashboard")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ الوصول للصفحة: FAIL (خطأ في الاتصال)")
        results['failed_tests'] += 1
        results['errors'].append("خطأ في الاتصال بلوحة التحكم")
    
    print()
    
    # اختبار 3: فحص القوائم الرئيسية
    print("📋 اختبار 3: القوائم الرئيسية")
    print("-" * 40)
    
    main_pages = [
        ('/sales', 'المبيعات'),
        ('/purchases', 'المشتريات'),
        ('/employees', 'الموظفين'),
        ('/customers', 'العملاء'),
        ('/reports', 'التقارير')
    ]
    
    for url, name in main_pages:
        try:
            response = requests.get(f"{base_url}{url}", timeout=10)
            results['total_tests'] += 1
            
            if response.status_code == 200:
                print(f"✅ صفحة '{name}': تعمل")
                results['passed_tests'] += 1
            elif response.status_code == 302:
                print(f"✅ صفحة '{name}': إعادة توجيه")
                results['passed_tests'] += 1
            else:
                print(f"❌ صفحة '{name}': خطأ HTTP {response.status_code}")
                results['failed_tests'] += 1
                results['errors'].append(f"خطأ HTTP {response.status_code} في {url}")
                
        except requests.exceptions.RequestException:
            print(f"❌ صفحة '{name}': خطأ في الاتصال")
            results['failed_tests'] += 1
            results['errors'].append(f"خطأ في الاتصال بـ {url}")
    
    print()
    
    # اختبار 4: فحص الاستجابة والأداء
    print("⚡ اختبار 4: الأداء والاستجابة")
    print("-" * 40)
    
    try:
        start_time = datetime.now()
        response = requests.get(f"{base_url}/", timeout=10)
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
        print("🎉 حالة النظام: ممتازة")
    elif success_rate >= 80:
        print("👍 حالة النظام: جيدة")
    elif success_rate >= 70:
        print("⚠️ حالة النظام: تحتاج تحسين")
    else:
        print("❌ حالة النظام: تحتاج إصلاح عاجل")
    
    # حفظ التقرير
    report = {
        'test_date': datetime.now().isoformat(),
        'test_type': 'main_screen_test',
        'results': results,
        'success_rate': success_rate,
        'status': 'excellent' if success_rate >= 90 else 'good' if success_rate >= 80 else 'needs_improvement'
    }
    
    with open('main_screen_test_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n📄 تم حفظ التقرير في: main_screen_test_report.json")

if __name__ == "__main__":
    test_main_screen()
