#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار شامل لعمليات العرض والتعديل والحذف (CRUD) في جميع الشاشات
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

def test_crud_operations(entity_name, base_url, view_url_pattern, edit_url_pattern, delete_url_pattern):
    """اختبار عمليات CRUD لكيان معين"""
    print(f"\n🔍 اختبار عمليات CRUD - {entity_name}:")
    
    # اختبار صفحة القائمة
    try:
        response = requests.get(f"{BASE_URL}{base_url}", timeout=10)
        if response.status_code == 200:
            log_test(f"{entity_name} - قائمة العرض", "PASS", f"كود الاستجابة: {response.status_code}")
            
            # البحث عن أزرار العمليات في HTML
            html_content = response.text
            
            # التحقق من وجود أزرار العرض والتعديل والحذف
            crud_buttons = {
                'عرض': ['fa-eye', 'view', 'عرض'],
                'تعديل': ['fa-edit', 'edit', 'تعديل'],
                'حذف': ['fa-trash', 'delete', 'حذف']
            }
            
            for operation, keywords in crud_buttons.items():
                found = any(keyword in html_content for keyword in keywords)
                if found:
                    log_test(f"{entity_name} - زر {operation}", "PASS", "الزر موجود في الواجهة")
                else:
                    log_test(f"{entity_name} - زر {operation}", "FAIL", "الزر غير موجود")
                    
        else:
            log_test(f"{entity_name} - قائمة العرض", "FAIL", f"كود الاستجابة: {response.status_code}")
    except Exception as e:
        log_test(f"{entity_name} - قائمة العرض", "FAIL", f"خطأ: {str(e)}")
    
    # اختبار صفحات العرض والتعديل (إذا كانت متاحة)
    test_ids = [1, 2, 3]  # اختبار أول 3 عناصر
    
    for test_id in test_ids:
        # اختبار صفحة العرض
        if view_url_pattern:
            try:
                view_url = view_url_pattern.format(id=test_id)
                response = requests.get(f"{BASE_URL}{view_url}", timeout=10)
                if response.status_code == 200:
                    log_test(f"{entity_name} - عرض العنصر {test_id}", "PASS", "صفحة العرض تعمل")
                elif response.status_code == 404:
                    log_test(f"{entity_name} - عرض العنصر {test_id}", "WARNING", "العنصر غير موجود")
                else:
                    log_test(f"{entity_name} - عرض العنصر {test_id}", "FAIL", f"كود: {response.status_code}")
            except Exception as e:
                log_test(f"{entity_name} - عرض العنصر {test_id}", "FAIL", f"خطأ: {str(e)}")
        
        # اختبار صفحة التعديل
        if edit_url_pattern:
            try:
                edit_url = edit_url_pattern.format(id=test_id)
                response = requests.get(f"{BASE_URL}{edit_url}", timeout=10)
                if response.status_code == 200:
                    log_test(f"{entity_name} - تعديل العنصر {test_id}", "PASS", "صفحة التعديل تعمل")
                elif response.status_code == 404:
                    log_test(f"{entity_name} - تعديل العنصر {test_id}", "WARNING", "العنصر غير موجود")
                else:
                    log_test(f"{entity_name} - تعديل العنصر {test_id}", "FAIL", f"كود: {response.status_code}")
            except Exception as e:
                log_test(f"{entity_name} - تعديل العنصر {test_id}", "FAIL", f"خطأ: {str(e)}")
        
        time.sleep(0.5)  # تأخير قصير بين الطلبات

def test_form_elements(entity_name, add_url, required_fields):
    """اختبار عناصر النماذج"""
    print(f"\n📝 اختبار عناصر النماذج - {entity_name}:")
    
    try:
        response = requests.get(f"{BASE_URL}{add_url}", timeout=10)
        if response.status_code == 200:
            html_content = response.text
            
            # التحقق من وجود الحقول المطلوبة
            for field in required_fields:
                if f'name="{field}"' in html_content or f'id="{field}"' in html_content:
                    log_test(f"{entity_name} - حقل {field}", "PASS", "الحقل موجود")
                else:
                    log_test(f"{entity_name} - حقل {field}", "FAIL", "الحقل مفقود")
            
            # التحقق من وجود عناصر النموذج المتقدمة
            advanced_features = [
                'forms.js',
                'save-btn',
                'undo-btn',
                'تتبع التغييرات'
            ]
            
            found_features = [feature for feature in advanced_features if feature in html_content]
            
            if len(found_features) >= 2:
                log_test(f"{entity_name} - النماذج المتقدمة", "PASS", f"مميزات متقدمة: {len(found_features)}")
            else:
                log_test(f"{entity_name} - النماذج المتقدمة", "WARNING", f"مميزات محدودة: {len(found_features)}")
                
        else:
            log_test(f"{entity_name} - نموذج الإضافة", "FAIL", f"كود الاستجابة: {response.status_code}")
    except Exception as e:
        log_test(f"{entity_name} - نموذج الإضافة", "FAIL", f"خطأ: {str(e)}")

def test_data_validation(entity_name, add_url, test_data):
    """اختبار التحقق من صحة البيانات"""
    print(f"\n🔒 اختبار التحقق من البيانات - {entity_name}:")
    
    try:
        # اختبار إرسال بيانات فارغة
        response = requests.post(f"{BASE_URL}{add_url}", data={}, timeout=10)
        
        if response.status_code in [400, 422]:
            log_test(f"{entity_name} - رفض البيانات الفارغة", "PASS", "تم رفض البيانات الفارغة")
        elif response.status_code == 200 and 'error' in response.text.lower():
            log_test(f"{entity_name} - رفض البيانات الفارغة", "PASS", "رسالة خطأ ظهرت")
        else:
            log_test(f"{entity_name} - رفض البيانات الفارغة", "WARNING", "لم يتم رفض البيانات الفارغة")
        
        # اختبار إرسال بيانات صحيحة
        if test_data:
            response = requests.post(f"{BASE_URL}{add_url}", data=test_data, timeout=10)
            
            if response.status_code in [200, 201, 302]:
                log_test(f"{entity_name} - قبول البيانات الصحيحة", "PASS", "تم قبول البيانات الصحيحة")
            else:
                log_test(f"{entity_name} - قبول البيانات الصحيحة", "FAIL", f"كود: {response.status_code}")
                
    except Exception as e:
        log_test(f"{entity_name} - التحقق من البيانات", "FAIL", f"خطأ: {str(e)}")

def run_comprehensive_crud_test():
    """تشغيل الاختبار الشامل لعمليات CRUD"""
    print("🔧 بدء الاختبار الشامل لعمليات العرض والتعديل والحذف")
    print("=" * 80)
    
    # تعريف الكيانات للاختبار
    entities = [
        {
            'name': 'الموظفين',
            'base_url': '/employees',
            'add_url': '/add_employee',
            'view_url': '/view_employee/{id}',
            'edit_url': '/edit_employee/{id}',
            'delete_url': '/delete_employee/{id}',
            'required_fields': ['name', 'email', 'phone', 'position', 'department'],
            'test_data': {
                'name': 'موظف اختبار',
                'email': 'test@example.com',
                'phone': '0501234567',
                'position': 'مطور',
                'department': 'تقنية المعلومات',
                'salary': '5000'
            }
        },
        {
            'name': 'العملاء',
            'base_url': '/customers',
            'add_url': '/add_customer',
            'view_url': '/view_customer/{id}',
            'edit_url': '/edit_customer/{id}',
            'delete_url': '/delete_customer/{id}',
            'required_fields': ['name', 'email', 'phone'],
            'test_data': {
                'name': 'عميل اختبار',
                'email': 'customer@example.com',
                'phone': '0509876543'
            }
        },
        {
            'name': 'الفواتير',
            'base_url': '/invoices',
            'add_url': '/add_invoice',
            'view_url': '/view_invoice/{id}',
            'edit_url': '/edit_invoice/{id}',
            'delete_url': '/delete_invoice/{id}',
            'required_fields': ['customer_name', 'total_amount'],
            'test_data': {
                'customer_name': 'عميل اختبار',
                'total_amount': '1000'
            }
        },
        {
            'name': 'المنتجات',
            'base_url': '/inventory',
            'add_url': '/add_product',
            'view_url': '/view_product/{id}',
            'edit_url': '/edit_product/{id}',
            'delete_url': '/delete_product/{id}',
            'required_fields': ['name', 'quantity', 'price'],
            'test_data': {
                'name': 'منتج اختبار',
                'quantity': '10',
                'price': '100'
            }
        },
        {
            'name': 'الموردين',
            'base_url': '/suppliers',
            'add_url': '/add_supplier',
            'view_url': '/view_supplier/{id}',
            'edit_url': '/edit_supplier/{id}',
            'delete_url': '/delete_supplier/{id}',
            'required_fields': ['name', 'contact_info'],
            'test_data': {
                'name': 'مورد اختبار',
                'contact_info': 'معلومات الاتصال'
            }
        },
        {
            'name': 'الحضور',
            'base_url': '/attendance',
            'add_url': '/add_attendance',
            'view_url': '/view_attendance/{id}',
            'edit_url': '/edit_attendance/{id}',
            'delete_url': '/delete_attendance/{id}',
            'required_fields': ['employee_id', 'date'],
            'test_data': {
                'employee_id': '1',
                'date': '2025-07-28'
            }
        }
    ]
    
    # اختبار كل كيان
    for entity in entities:
        test_crud_operations(
            entity['name'],
            entity['base_url'],
            entity.get('view_url'),
            entity.get('edit_url'),
            entity.get('delete_url')
        )
        
        test_form_elements(
            entity['name'],
            entity['add_url'],
            entity['required_fields']
        )
        
        test_data_validation(
            entity['name'],
            entity['add_url'],
            entity.get('test_data')
        )
        
        time.sleep(1)  # تأخير بين الكيانات
    
    # تلخيص النتائج
    print("\n" + "=" * 80)
    print("📊 ملخص نتائج اختبار عمليات CRUD:")
    
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
    
    # تحليل النتائج حسب الكيان
    print("\n📋 تحليل النتائج حسب الكيان:")
    for entity in entities:
        entity_tests = [r for r in TEST_RESULTS if entity['name'] in r['test']]
        entity_passed = len([r for r in entity_tests if r['status'] == 'PASS'])
        entity_total = len(entity_tests)
        entity_rate = (entity_passed / entity_total) * 100 if entity_total > 0 else 0
        
        status_icon = "✅" if entity_rate >= 80 else "⚠️" if entity_rate >= 60 else "❌"
        print(f"   {status_icon} {entity['name']}: {entity_rate:.1f}% ({entity_passed}/{entity_total})")
    
    if success_rate >= 90:
        print("\n🎉 ممتاز! جميع عمليات CRUD تعمل بكفاءة عالية")
    elif success_rate >= 75:
        print("\n👍 جيد! معظم عمليات CRUD تعمل بشكل صحيح")
    elif success_rate >= 60:
        print("\n⚠️  مقبول! بعض عمليات CRUD تحتاج تحسين")
    else:
        print("\n❌ يحتاج إصلاح! مشاكل كثيرة في عمليات CRUD")
    
    # حفظ النتائج في ملف
    with open('crud_test_results.json', 'w', encoding='utf-8') as f:
        json.dump(TEST_RESULTS, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 تم حفظ النتائج التفصيلية في: crud_test_results.json")
    
    return success_rate

if __name__ == "__main__":
    try:
        success_rate = run_comprehensive_crud_test()
        exit(0 if success_rate >= 75 else 1)
    except KeyboardInterrupt:
        print("\n⏹️  تم إيقاف الاختبار بواسطة المستخدم")
        exit(1)
    except Exception as e:
        print(f"\n❌ خطأ عام في اختبار CRUD: {str(e)}")
        exit(1)
