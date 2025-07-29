#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار شاشة المبيعات المحسنة
Sales Screen Enhanced Testing
"""

import requests
import json
from datetime import datetime

def test_sales_screen():
    """اختبار شامل لشاشة المبيعات"""
    
    print("🛍️ بدء اختبار شاشة المبيعات المحسنة...")
    print("=" * 60)
    
    base_url = "http://127.0.0.1:5000"
    results = {
        'total_tests': 0,
        'passed_tests': 0,
        'failed_tests': 0,
        'errors': []
    }
    
    # اختبار 1: الوصول لصفحة المبيعات الرئيسية
    print("\n📊 اختبار 1: صفحة المبيعات الرئيسية")
    print("-" * 40)
    
    try:
        response = requests.get(f"{base_url}/sales", timeout=10)
        results['total_tests'] += 1
        
        if response.status_code == 200:
            print("✅ الوصول للصفحة: PASS")
            results['passed_tests'] += 1
            
            # فحص محتوى الصفحة
            content = response.text
            required_elements = [
                'مبيعات اليوم',
                'مبيعات الشهر', 
                'عدد المعاملات',
                'متوسط البيعة',
                'آخر المبيعات'
            ]
            
            for element in required_elements:
                if element in content:
                    print(f"✅ عنصر '{element}': موجود")
                else:
                    print(f"❌ عنصر '{element}': مفقود")
                    results['errors'].append(f"عنصر مفقود: {element}")
                    
        else:
            print(f"❌ الوصول للصفحة: FAIL (HTTP {response.status_code})")
            results['failed_tests'] += 1
            results['errors'].append(f"خطأ HTTP {response.status_code} في /sales")
            
    except Exception as e:
        print(f"❌ خطأ في الاتصال: {str(e)}")
        results['failed_tests'] += 1
        results['errors'].append(f"خطأ اتصال /sales: {str(e)}")
    
    # اختبار 2: صفحة إضافة فاتورة مبيعات
    print("\n📝 اختبار 2: صفحة إضافة فاتورة مبيعات")
    print("-" * 40)
    
    try:
        response = requests.get(f"{base_url}/add_sales_invoice", timeout=10)
        results['total_tests'] += 1
        
        if response.status_code == 200:
            print("✅ الوصول للصفحة: PASS")
            results['passed_tests'] += 1
            
            # فحص عناصر النموذج
            content = response.text
            form_elements = [
                'customer_name',
                'total_amount',
                'subtotal',
                'tax_amount'
            ]
            
            for element in form_elements:
                if element in content:
                    print(f"✅ حقل '{element}': موجود")
                else:
                    print(f"❌ حقل '{element}': مفقود")
                    results['errors'].append(f"حقل مفقود: {element}")
                    
        else:
            print(f"❌ الوصول للصفحة: FAIL (HTTP {response.status_code})")
            results['failed_tests'] += 1
            results['errors'].append(f"خطأ HTTP {response.status_code} في /add_sales_invoice")
            
    except Exception as e:
        print(f"❌ خطأ في الاتصال: {str(e)}")
        results['failed_tests'] += 1
        results['errors'].append(f"خطأ اتصال /add_sales_invoice: {str(e)}")
    
    # اختبار 3: صفحة فواتير المبيعات
    print("\n📋 اختبار 3: صفحة فواتير المبيعات")
    print("-" * 40)
    
    try:
        response = requests.get(f"{base_url}/sales_invoices", timeout=10)
        results['total_tests'] += 1
        
        if response.status_code == 200:
            print("✅ الوصول للصفحة: PASS")
            results['passed_tests'] += 1
            
            # فحص عناصر الجدول
            content = response.text
            table_elements = [
                'رقم الفاتورة',
                'العميل',
                'التاريخ',
                'الإجمالي',
                'الحالة'
            ]
            
            for element in table_elements:
                if element in content:
                    print(f"✅ عمود '{element}': موجود")
                else:
                    print(f"❌ عمود '{element}': مفقود")
                    results['errors'].append(f"عمود مفقود: {element}")
                    
        else:
            print(f"❌ الوصول للصفحة: FAIL (HTTP {response.status_code})")
            results['failed_tests'] += 1
            results['errors'].append(f"خطأ HTTP {response.status_code} في /sales_invoices")
            
    except Exception as e:
        print(f"❌ خطأ في الاتصال: {str(e)}")
        results['failed_tests'] += 1
        results['errors'].append(f"خطأ اتصال /sales_invoices: {str(e)}")
    
    # اختبار 4: صفحة العملاء
    print("\n👥 اختبار 4: صفحة العملاء")
    print("-" * 40)
    
    try:
        response = requests.get(f"{base_url}/customers", timeout=10)
        results['total_tests'] += 1
        
        if response.status_code == 200:
            print("✅ الوصول للصفحة: PASS")
            results['passed_tests'] += 1
        else:
            print(f"❌ الوصول للصفحة: FAIL (HTTP {response.status_code})")
            results['failed_tests'] += 1
            results['errors'].append(f"خطأ HTTP {response.status_code} في /customers")
            
    except Exception as e:
        print(f"❌ خطأ في الاتصال: {str(e)}")
        results['failed_tests'] += 1
        results['errors'].append(f"خطأ اتصال /customers: {str(e)}")
    
    # اختبار 5: صفحة تسجيل الدفع
    print("\n💰 اختبار 5: صفحة تسجيل الدفع")
    print("-" * 40)
    
    try:
        response = requests.get(f"{base_url}/add_payment", timeout=10)
        results['total_tests'] += 1
        
        if response.status_code == 200:
            print("✅ الوصول للصفحة: PASS")
            results['passed_tests'] += 1
        else:
            print(f"❌ الوصول للصفحة: FAIL (HTTP {response.status_code})")
            results['failed_tests'] += 1
            results['errors'].append(f"خطأ HTTP {response.status_code} في /add_payment")
            
    except Exception as e:
        print(f"❌ خطأ في الاتصال: {str(e)}")
        results['failed_tests'] += 1
        results['errors'].append(f"خطأ اتصال /add_payment: {str(e)}")
    
    # النتائج النهائية
    print("\n" + "=" * 60)
    print("📊 النتائج النهائية")
    print("=" * 60)
    
    success_rate = (results['passed_tests'] / results['total_tests'] * 100) if results['total_tests'] > 0 else 0
    
    print(f"إجمالي الاختبارات: {results['total_tests']}")
    print(f"الاختبارات الناجحة: {results['passed_tests']}")
    print(f"الاختبارات الفاشلة: {results['failed_tests']}")
    print(f"معدل النجاح: {success_rate:.1f}%")
    
    if results['errors']:
        print(f"\n❌ الأخطاء المكتشفة ({len(results['errors'])}):")
        for i, error in enumerate(results['errors'], 1):
            print(f"   {i}. {error}")
    else:
        print("\n✅ لا توجد أخطاء - جميع الاختبارات نجحت!")
    
    # تقييم الحالة العامة
    if success_rate >= 90:
        print(f"\n🎉 حالة النظام: ممتازة ({success_rate:.1f}%)")
        status = "ممتاز"
    elif success_rate >= 70:
        print(f"\n👍 حالة النظام: جيدة ({success_rate:.1f}%)")
        status = "جيد"
    elif success_rate >= 50:
        print(f"\n⚠️ حالة النظام: مقبولة ({success_rate:.1f}%)")
        status = "مقبول"
    else:
        print(f"\n❌ حالة النظام: تحتاج تحسين ({success_rate:.1f}%)")
        status = "يحتاج تحسين"
    
    # حفظ التقرير
    report = {
        'timestamp': datetime.now().isoformat(),
        'total_tests': results['total_tests'],
        'passed_tests': results['passed_tests'],
        'failed_tests': results['failed_tests'],
        'success_rate': success_rate,
        'status': status,
        'errors': results['errors']
    }
    
    with open('sales_screen_test_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n📄 تم حفظ التقرير في: sales_screen_test_report.json")
    
    return results

if __name__ == "__main__":
    test_sales_screen()
