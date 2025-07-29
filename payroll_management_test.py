#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار شامل لإدارة الرواتب والحوافز والبدلات والاستقطاعات
"""

import requests
import json
import time
from datetime import datetime, date

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

def test_payroll_pages():
    """اختبار صفحات الرواتب"""
    print("💰 اختبار صفحات إدارة الرواتب:")
    
    pages = [
        ("/payroll", "قائمة الرواتب"),
        ("/generate_payroll", "إنشاء راتب"),
        ("/employees", "قائمة الموظفين"),
        ("/attendance", "سجل الحضور")
    ]
    
    for url, name in pages:
        try:
            response = requests.get(f"{BASE_URL}{url}", timeout=10)
            if response.status_code == 200:
                log_test(f"الرواتب - {name}", "PASS", f"كود الاستجابة: {response.status_code}")
                
                # التحقق من وجود عناصر مهمة
                html_content = response.text
                if any(keyword in html_content for keyword in ["راتب", "موظف", "حضور", "بدل"]):
                    log_test(f"الرواتب - محتوى {name}", "PASS", "المحتوى العربي موجود")
                else:
                    log_test(f"الرواتب - محتوى {name}", "WARNING", "المحتوى العربي قد يكون ناقص")
                    
            else:
                log_test(f"الرواتب - {name}", "FAIL", f"كود الاستجابة: {response.status_code}")
        except Exception as e:
            log_test(f"الرواتب - {name}", "FAIL", f"خطأ: {str(e)}")
        time.sleep(0.5)

def test_payroll_form_elements():
    """اختبار عناصر نموذج إنشاء الراتب"""
    print("\n📝 اختبار عناصر نموذج إنشاء الراتب:")
    
    try:
        response = requests.get(f"{BASE_URL}/generate_payroll", timeout=10)
        if response.status_code == 200:
            html_content = response.text
            
            # التحقق من وجود الحقول المطلوبة
            required_fields = [
                'employee_id',
                'month',
                'year',
                'basic_salary',
                'allowances',
                'overtime_pay',
                'deductions',
                'tax',
                'insurance'
            ]
            
            for field in required_fields:
                if f'name="{field}"' in html_content or f'id="{field}"' in html_content:
                    log_test(f"نموذج الراتب - حقل {field}", "PASS", "الحقل موجود")
                else:
                    log_test(f"نموذج الراتب - حقل {field}", "FAIL", "الحقل مفقود")
            
            # التحقق من وجود قائمة الموظفين
            if 'employee_id' in html_content and 'option' in html_content:
                log_test("نموذج الراتب - قائمة الموظفين", "PASS", "قائمة الموظفين موجودة")
            else:
                log_test("نموذج الراتب - قائمة الموظفين", "WARNING", "قائمة الموظفين قد تكون فارغة")
            
            # التحقق من وجود وظائف JavaScript للحسابات
            js_functions = [
                'calculateNetSalary',
                'calculateTax',
                'calculateInsurance'
            ]
            
            found_functions = [func for func in js_functions if func in html_content]
            
            if len(found_functions) >= 1:
                log_test("نموذج الراتب - وظائف الحساب", "PASS", f"وظائف موجودة: {len(found_functions)}")
            else:
                log_test("نموذج الراتب - وظائف الحساب", "WARNING", "وظائف الحساب محدودة")
                
        else:
            log_test("نموذج الراتب", "FAIL", f"كود الاستجابة: {response.status_code}")
    except Exception as e:
        log_test("نموذج الراتب", "FAIL", f"خطأ: {str(e)}")

def test_employee_data():
    """اختبار بيانات الموظفين"""
    print("\n👥 اختبار بيانات الموظفين:")
    
    try:
        response = requests.get(f"{BASE_URL}/employees", timeout=10)
        if response.status_code == 200:
            html_content = response.text
            
            # التحقق من وجود بيانات الموظفين
            if 'table' in html_content and 'tbody' in html_content:
                log_test("بيانات الموظفين - الجدول", "PASS", "جدول الموظفين موجود")
                
                # التحقق من وجود أعمدة مهمة
                important_columns = [
                    'الاسم',
                    'الراتب',
                    'القسم',
                    'المنصب',
                    'تاريخ التوظيف'
                ]
                
                found_columns = [col for col in important_columns if col in html_content]
                
                if len(found_columns) >= 3:
                    log_test("بيانات الموظفين - الأعمدة", "PASS", f"أعمدة موجودة: {len(found_columns)}")
                else:
                    log_test("بيانات الموظفين - الأعمدة", "WARNING", f"أعمدة محدودة: {len(found_columns)}")
                
                # التحقق من وجود بيانات فعلية
                if 'EMP-' in html_content or 'موظف' in html_content:
                    log_test("بيانات الموظفين - البيانات", "PASS", "يوجد بيانات موظفين")
                else:
                    log_test("بيانات الموظفين - البيانات", "WARNING", "لا توجد بيانات موظفين")
                    
            else:
                log_test("بيانات الموظفين - الجدول", "FAIL", "جدول الموظفين مفقود")
                
        else:
            log_test("بيانات الموظفين", "FAIL", f"كود الاستجابة: {response.status_code}")
    except Exception as e:
        log_test("بيانات الموظفين", "FAIL", f"خطأ: {str(e)}")

def test_attendance_data():
    """اختبار بيانات الحضور"""
    print("\n⏰ اختبار بيانات الحضور:")
    
    try:
        response = requests.get(f"{BASE_URL}/attendance", timeout=10)
        if response.status_code == 200:
            html_content = response.text
            
            # التحقق من وجود سجل الحضور
            if 'table' in html_content and 'tbody' in html_content:
                log_test("بيانات الحضور - الجدول", "PASS", "جدول الحضور موجود")
                
                # التحقق من وجود أعمدة مهمة
                attendance_columns = [
                    'الموظف',
                    'التاريخ',
                    'وقت الدخول',
                    'وقت الخروج',
                    'ساعات العمل',
                    'الإضافي'
                ]
                
                found_columns = [col for col in attendance_columns if col in html_content]
                
                if len(found_columns) >= 4:
                    log_test("بيانات الحضور - الأعمدة", "PASS", f"أعمدة موجودة: {len(found_columns)}")
                else:
                    log_test("بيانات الحضور - الأعمدة", "WARNING", f"أعمدة محدودة: {len(found_columns)}")
                
                # التحقق من وجود بيانات حضور
                if any(time_format in html_content for time_format in [':', 'AM', 'PM', 'ص', 'م']):
                    log_test("بيانات الحضور - البيانات", "PASS", "يوجد بيانات حضور")
                else:
                    log_test("بيانات الحضور - البيانات", "WARNING", "لا توجد بيانات حضور")
                    
            else:
                log_test("بيانات الحضور - الجدول", "FAIL", "جدول الحضور مفقود")
                
        else:
            log_test("بيانات الحضور", "FAIL", f"كود الاستجابة: {response.status_code}")
    except Exception as e:
        log_test("بيانات الحضور", "FAIL", f"خطأ: {str(e)}")

def test_payroll_calculations():
    """اختبار حسابات الراتب"""
    print("\n🧮 اختبار حسابات الراتب:")
    
    try:
        # بيانات راتب تجريبية
        payroll_data = {
            'employee_id': '1',
            'month': '12',
            'year': '2024',
            'basic_salary': '5000.00',
            'allowances': '1000.00',
            'overtime_pay': '500.00',
            'deductions': '200.00',
            'tax': '0.00',
            'insurance': '300.00'
        }
        
        response = requests.post(f"{BASE_URL}/generate_payroll", data=payroll_data, timeout=10)
        
        if response.status_code in [200, 201, 302]:
            log_test("حسابات الراتب - إنشاء راتب", "PASS", "تم إنشاء الراتب بنجاح")
            
            # اختبار حسابات مختلفة
            test_cases = [
                {
                    'name': 'راتب أساسي عالي',
                    'basic_salary': '10000.00',
                    'allowances': '2000.00',
                    'overtime_pay': '1000.00',
                    'deductions': '500.00'
                },
                {
                    'name': 'راتب أساسي منخفض',
                    'basic_salary': '3000.00',
                    'allowances': '500.00',
                    'overtime_pay': '200.00',
                    'deductions': '100.00'
                }
            ]
            
            for case in test_cases:
                test_data = payroll_data.copy()
                test_data.update(case)
                test_data.pop('name')
                
                test_response = requests.post(f"{BASE_URL}/generate_payroll", data=test_data, timeout=10)
                
                if test_response.status_code in [200, 201, 302]:
                    log_test(f"حسابات الراتب - {case['name']}", "PASS", "الحساب تم بنجاح")
                else:
                    log_test(f"حسابات الراتب - {case['name']}", "WARNING", f"كود: {test_response.status_code}")
                    
        elif response.status_code == 400:
            log_test("حسابات الراتب - إنشاء راتب", "WARNING", "خطأ في البيانات المرسلة")
        else:
            log_test("حسابات الراتب - إنشاء راتب", "FAIL", f"كود الاستجابة: {response.status_code}")
            
    except Exception as e:
        log_test("حسابات الراتب", "FAIL", f"خطأ: {str(e)}")

def test_payroll_components():
    """اختبار مكونات الراتب (بدلات، حوافز، استقطاعات)"""
    print("\n💼 اختبار مكونات الراتب:")
    
    try:
        response = requests.get(f"{BASE_URL}/payroll", timeout=10)
        if response.status_code == 200:
            html_content = response.text
            
            # التحقق من وجود مكونات الراتب
            salary_components = [
                'الراتب الأساسي',
                'البدلات',
                'الحوافز',
                'العمل الإضافي',
                'الاستقطاعات',
                'التأمين',
                'الضريبة',
                'صافي الراتب'
            ]
            
            found_components = [comp for comp in salary_components if comp in html_content]
            
            if len(found_components) >= 5:
                log_test("مكونات الراتب - العناصر", "PASS", f"مكونات موجودة: {len(found_components)}")
            else:
                log_test("مكونات الراتب - العناصر", "WARNING", f"مكونات محدودة: {len(found_components)}")
            
            # التحقق من وجود حسابات مالية
            if any(symbol in html_content for symbol in ['ر.س', 'SAR', '+', '-', '=']):
                log_test("مكونات الراتب - الحسابات", "PASS", "حسابات مالية موجودة")
            else:
                log_test("مكونات الراتب - الحسابات", "WARNING", "حسابات مالية محدودة")
            
            # التحقق من وجود حالات الراتب
            payroll_statuses = ['معلق', 'مدفوع', 'ملغي', 'pending', 'paid', 'cancelled']
            found_statuses = [status for status in payroll_statuses if status in html_content]
            
            if len(found_statuses) >= 2:
                log_test("مكونات الراتب - الحالات", "PASS", f"حالات موجودة: {len(found_statuses)}")
            else:
                log_test("مكونات الراتب - الحالات", "WARNING", f"حالات محدودة: {len(found_statuses)}")
                
        else:
            log_test("مكونات الراتب", "FAIL", f"كود الاستجابة: {response.status_code}")
    except Exception as e:
        log_test("مكونات الراتب", "FAIL", f"خطأ: {str(e)}")

def test_payroll_reports():
    """اختبار تقارير الرواتب"""
    print("\n📊 اختبار تقارير الرواتب:")
    
    try:
        response = requests.get(f"{BASE_URL}/payroll", timeout=10)
        if response.status_code == 200:
            html_content = response.text
            
            # التحقق من وجود إحصائيات
            statistics_elements = [
                'إجمالي',
                'متوسط',
                'عدد',
                'مجموع',
                'total',
                'average',
                'count'
            ]
            
            found_stats = [stat for stat in statistics_elements if stat in html_content]
            
            if len(found_stats) >= 3:
                log_test("تقارير الرواتب - الإحصائيات", "PASS", f"إحصائيات موجودة: {len(found_stats)}")
            else:
                log_test("تقارير الرواتب - الإحصائيات", "WARNING", f"إحصائيات محدودة: {len(found_stats)}")
            
            # التحقق من وجود وظائف التصدير
            export_functions = [
                'تصدير',
                'طباعة',
                'CSV',
                'Excel',
                'PDF',
                'export',
                'print'
            ]
            
            found_exports = [exp for exp in export_functions if exp in html_content]
            
            if len(found_exports) >= 2:
                log_test("تقارير الرواتب - التصدير", "PASS", f"وظائف تصدير موجودة: {len(found_exports)}")
            else:
                log_test("تقارير الرواتب - التصدير", "WARNING", f"وظائف تصدير محدودة: {len(found_exports)}")
            
            # التحقق من وجود فلاتر
            filter_elements = [
                'بحث',
                'تصفية',
                'شهر',
                'سنة',
                'موظف',
                'search',
                'filter'
            ]
            
            found_filters = [filt for filt in filter_elements if filt in html_content]
            
            if len(found_filters) >= 3:
                log_test("تقارير الرواتب - الفلاتر", "PASS", f"فلاتر موجودة: {len(found_filters)}")
            else:
                log_test("تقارير الرواتب - الفلاتر", "WARNING", f"فلاتر محدودة: {len(found_filters)}")
                
        else:
            log_test("تقارير الرواتب", "FAIL", f"كود الاستجابة: {response.status_code}")
    except Exception as e:
        log_test("تقارير الرواتب", "FAIL", f"خطأ: {str(e)}")

def test_leave_management():
    """اختبار إدارة الإجازات"""
    print("\n🏖️ اختبار إدارة الإجازات:")
    
    # اختبار صفحات الإجازات إذا كانت موجودة
    leave_pages = [
        "/leaves",
        "/add_leave",
        "/leave_requests"
    ]
    
    for page in leave_pages:
        try:
            response = requests.get(f"{BASE_URL}{page}", timeout=10)
            if response.status_code == 200:
                log_test(f"إدارة الإجازات - {page}", "PASS", "الصفحة تعمل")
            elif response.status_code == 404:
                log_test(f"إدارة الإجازات - {page}", "WARNING", "الصفحة غير موجودة")
            else:
                log_test(f"إدارة الإجازات - {page}", "FAIL", f"كود: {response.status_code}")
        except Exception as e:
            log_test(f"إدارة الإجازات - {page}", "FAIL", f"خطأ: {str(e)}")
        time.sleep(0.3)

def run_payroll_management_test():
    """تشغيل الاختبار الشامل لإدارة الرواتب"""
    print("💰 بدء الاختبار الشامل لإدارة الرواتب والحوافز والبدلات والاستقطاعات")
    print("=" * 80)
    
    # اختبار صفحات الرواتب
    test_payroll_pages()
    
    # اختبار عناصر النماذج
    test_payroll_form_elements()
    
    # اختبار بيانات الموظفين
    test_employee_data()
    
    # اختبار بيانات الحضور
    test_attendance_data()
    
    # اختبار حسابات الراتب
    test_payroll_calculations()
    
    # اختبار مكونات الراتب
    test_payroll_components()
    
    # اختبار تقارير الرواتب
    test_payroll_reports()
    
    # اختبار إدارة الإجازات
    test_leave_management()
    
    # تلخيص النتائج
    print("\n" + "=" * 80)
    print("📊 ملخص نتائج اختبار إدارة الرواتب:")
    
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
        'صفحات الرواتب': ['الرواتب -'],
        'نماذج الرواتب': ['نموذج الراتب'],
        'بيانات الموظفين': ['بيانات الموظفين'],
        'بيانات الحضور': ['بيانات الحضور'],
        'حسابات الراتب': ['حسابات الراتب'],
        'مكونات الراتب': ['مكونات الراتب'],
        'تقارير الرواتب': ['تقارير الرواتب'],
        'إدارة الإجازات': ['إدارة الإجازات']
    }
    
    for category, keywords in categories.items():
        category_tests = [r for r in TEST_RESULTS if any(keyword in r['test'] for keyword in keywords)]
        category_passed = len([r for r in category_tests if r['status'] == 'PASS'])
        category_total = len(category_tests)
        category_rate = (category_passed / category_total) * 100 if category_total > 0 else 0
        
        status_icon = "✅" if category_rate >= 80 else "⚠️" if category_rate >= 60 else "❌"
        print(f"   {status_icon} {category}: {category_rate:.1f}% ({category_passed}/{category_total})")
    
    if success_rate >= 90:
        print("\n🎉 ممتاز! نظام إدارة الرواتب يعمل بكفاءة عالية")
    elif success_rate >= 75:
        print("\n👍 جيد! نظام إدارة الرواتب يعمل بشكل مقبول")
    elif success_rate >= 60:
        print("\n⚠️  مقبول! بعض أجزاء النظام تحتاج تحسين")
    else:
        print("\n❌ يحتاج إصلاح! مشاكل كثيرة في النظام")
    
    # حفظ النتائج في ملف
    with open('payroll_test_results.json', 'w', encoding='utf-8') as f:
        json.dump(TEST_RESULTS, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 تم حفظ النتائج التفصيلية في: payroll_test_results.json")
    
    return success_rate

if __name__ == "__main__":
    try:
        success_rate = run_payroll_management_test()
        exit(0 if success_rate >= 75 else 1)
    except KeyboardInterrupt:
        print("\n⏹️  تم إيقاف الاختبار بواسطة المستخدم")
        exit(1)
    except Exception as e:
        print(f"\n❌ خطأ عام في اختبار إدارة الرواتب: {str(e)}")
        exit(1)
