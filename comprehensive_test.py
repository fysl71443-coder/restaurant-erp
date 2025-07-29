#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار شامل لنظام إدارة الموظفين
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

def test_page_load(url, page_name):
    """اختبار تحميل الصفحة"""
    try:
        response = requests.get(f"{BASE_URL}{url}", timeout=10)
        if response.status_code == 200:
            log_test(f"تحميل صفحة {page_name}", "PASS", f"كود الاستجابة: {response.status_code}")
            return True
        else:
            log_test(f"تحميل صفحة {page_name}", "FAIL", f"كود الاستجابة: {response.status_code}")
            return False
    except Exception as e:
        log_test(f"تحميل صفحة {page_name}", "FAIL", f"خطأ: {str(e)}")
        return False

def test_search_functionality():
    """اختبار وظائف البحث"""
    try:
        # اختبار صفحة الموظفين مع البحث
        response = requests.get(f"{BASE_URL}/employees")
        if response.status_code == 200:
            # التحقق من وجود عناصر البحث في HTML
            html_content = response.text
            search_elements = [
                'id="searchInput"',
                'id="departmentFilter"',
                'id="statusFilter"',
                'id="contractFilter"'
            ]
            
            all_found = all(element in html_content for element in search_elements)
            if all_found:
                log_test("عناصر البحث والتصفية", "PASS", "جميع عناصر البحث موجودة")
            else:
                log_test("عناصر البحث والتصفية", "FAIL", "بعض عناصر البحث مفقودة")
        else:
            log_test("عناصر البحث والتصفية", "FAIL", "فشل في تحميل الصفحة")
    except Exception as e:
        log_test("عناصر البحث والتصفية", "FAIL", f"خطأ: {str(e)}")

def test_form_functionality():
    """اختبار وظائف النماذج"""
    try:
        # اختبار صفحة إضافة موظف
        response = requests.get(f"{BASE_URL}/add_employee")
        if response.status_code == 200:
            html_content = response.text
            
            # التحقق من وجود عناصر النموذج المتقدمة
            form_elements = [
                'id="employeeForm"',
                'class="save-btn"',
                'class="undo-btn"',
                'forms.js'
            ]
            
            all_found = all(element in html_content for element in form_elements)
            if all_found:
                log_test("عناصر النموذج المتقدمة", "PASS", "جميع عناصر النموذج موجودة")
            else:
                log_test("عناصر النموذج المتقدمة", "FAIL", "بعض عناصر النموذج مفقودة")
        else:
            log_test("عناصر النموذج المتقدمة", "FAIL", "فشل في تحميل الصفحة")
    except Exception as e:
        log_test("عناصر النموذج المتقدمة", "FAIL", f"خطأ: {str(e)}")

def test_attendance_functionality():
    """اختبار وظائف الحضور"""
    try:
        # اختبار صفحة الحضور
        response = requests.get(f"{BASE_URL}/attendance")
        if response.status_code == 200:
            html_content = response.text
            
            # التحقق من وجود عناصر الحضور
            attendance_elements = [
                'id="attendanceTable"',
                'id="quickAttendanceForm"',
                'id="currentTime"',
                'exportAttendance'
            ]
            
            all_found = all(element in html_content for element in attendance_elements)
            if all_found:
                log_test("عناصر إدارة الحضور", "PASS", "جميع عناصر الحضور موجودة")
            else:
                log_test("عناصر إدارة الحضور", "FAIL", "بعض عناصر الحضور مفقودة")
        else:
            log_test("عناصر إدارة الحضور", "FAIL", "فشل في تحميل الصفحة")
    except Exception as e:
        log_test("عناصر إدارة الحضور", "FAIL", f"خطأ: {str(e)}")

def test_payroll_functionality():
    """اختبار وظائف الرواتب"""
    try:
        # اختبار صفحة الرواتب
        response = requests.get(f"{BASE_URL}/payroll")
        if response.status_code == 200:
            html_content = response.text
            
            # التحقق من وجود عناصر الرواتب
            payroll_elements = [
                'id="payrollTable"',
                'id="salaryChart"',
                'id="salaryComponentsChart"',
                'exportPayroll'
            ]
            
            all_found = all(element in html_content for element in payroll_elements)
            if all_found:
                log_test("عناصر إدارة الرواتب", "PASS", "جميع عناصر الرواتب موجودة")
            else:
                log_test("عناصر إدارة الرواتب", "FAIL", "بعض عناصر الرواتب مفقودة")
        else:
            log_test("عناصر إدارة الرواتب", "FAIL", "فشل في تحميل الصفحة")
    except Exception as e:
        log_test("عناصر إدارة الرواتب", "FAIL", f"خطأ: {str(e)}")

def test_charts_and_statistics():
    """اختبار الرسوم البيانية والإحصائيات"""
    try:
        # اختبار وجود Chart.js في الصفحات
        pages_with_charts = [
            ("/employees", "الموظفين"),
            ("/attendance", "الحضور"),
            ("/payroll", "الرواتب")
        ]
        
        charts_working = True
        for url, page_name in pages_with_charts:
            response = requests.get(f"{BASE_URL}{url}")
            if response.status_code == 200:
                html_content = response.text
                if "chart.js" in html_content.lower():
                    log_test(f"رسوم بيانية - {page_name}", "PASS", "Chart.js محمل")
                else:
                    log_test(f"رسوم بيانية - {page_name}", "FAIL", "Chart.js غير محمل")
                    charts_working = False
            else:
                charts_working = False
        
        if charts_working:
            log_test("الرسوم البيانية العامة", "PASS", "جميع الرسوم البيانية تعمل")
        else:
            log_test("الرسوم البيانية العامة", "FAIL", "مشاكل في الرسوم البيانية")
            
    except Exception as e:
        log_test("الرسوم البيانية العامة", "FAIL", f"خطأ: {str(e)}")

def test_export_functionality():
    """اختبار وظائف التصدير"""
    try:
        # اختبار وجود وظائف التصدير في الصفحات
        pages_with_export = [
            ("/employees", "الموظفين", "exportEmployees"),
            ("/attendance", "الحضور", "exportAttendance"),
            ("/payroll", "الرواتب", "exportPayroll")
        ]
        
        export_working = True
        for url, page_name, export_function in pages_with_export:
            response = requests.get(f"{BASE_URL}{url}")
            if response.status_code == 200:
                html_content = response.text
                if export_function in html_content:
                    log_test(f"تصدير - {page_name}", "PASS", f"وظيفة {export_function} موجودة")
                else:
                    log_test(f"تصدير - {page_name}", "FAIL", f"وظيفة {export_function} مفقودة")
                    export_working = False
            else:
                export_working = False
        
        if export_working:
            log_test("وظائف التصدير العامة", "PASS", "جميع وظائف التصدير متاحة")
        else:
            log_test("وظائف التصدير العامة", "FAIL", "مشاكل في وظائف التصدير")
            
    except Exception as e:
        log_test("وظائف التصدير العامة", "FAIL", f"خطأ: {str(e)}")

def test_arabic_support():
    """اختبار دعم اللغة العربية"""
    try:
        response = requests.get(f"{BASE_URL}/employees")
        if response.status_code == 200:
            html_content = response.text
            
            # التحقق من وجود النصوص العربية والتنسيق
            arabic_elements = [
                'dir="rtl"',
                'lang="ar"',
                'إدارة الموظفين',
                'bootstrap.rtl.min.css'
            ]
            
            all_found = all(element in html_content for element in arabic_elements)
            if all_found:
                log_test("دعم اللغة العربية", "PASS", "تنسيق RTL ونصوص عربية صحيحة")
            else:
                log_test("دعم اللغة العربية", "FAIL", "مشاكل في دعم العربية")
        else:
            log_test("دعم اللغة العربية", "FAIL", "فشل في تحميل الصفحة")
    except Exception as e:
        log_test("دعم اللغة العربية", "FAIL", f"خطأ: {str(e)}")

def test_responsive_design():
    """اختبار التصميم المتجاوب"""
    try:
        response = requests.get(f"{BASE_URL}/employees")
        if response.status_code == 200:
            html_content = response.text
            
            # التحقق من وجود عناصر التصميم المتجاوب
            responsive_elements = [
                'class="container-fluid"',
                'class="row"',
                'class="col-md-',
                'class="table-responsive"',
                '@media'
            ]
            
            found_count = sum(1 for element in responsive_elements if element in html_content)
            if found_count >= 4:
                log_test("التصميم المتجاوب", "PASS", f"عناصر متجاوبة: {found_count}/5")
            else:
                log_test("التصميم المتجاوب", "WARNING", f"عناصر متجاوبة محدودة: {found_count}/5")
        else:
            log_test("التصميم المتجاوب", "FAIL", "فشل في تحميل الصفحة")
    except Exception as e:
        log_test("التصميم المتجاوب", "FAIL", f"خطأ: {str(e)}")

def run_comprehensive_test():
    """تشغيل الاختبار الشامل"""
    print("🚀 بدء الاختبار الشامل لنظام إدارة الموظفين")
    print("=" * 60)
    
    # اختبار تحميل الصفحات الأساسية
    print("\n📄 اختبار تحميل الصفحات:")
    pages = [
        ("/", "الصفحة الرئيسية"),
        ("/employees", "إدارة الموظفين"),
        ("/add_employee", "إضافة موظف"),
        ("/attendance", "إدارة الحضور"),
        ("/add_attendance", "تسجيل حضور"),
        ("/payroll", "إدارة الرواتب")
    ]
    
    for url, name in pages:
        test_page_load(url, name)
        time.sleep(0.5)  # تأخير قصير بين الطلبات
    
    # اختبار الوظائف المتخصصة
    print("\n🔍 اختبار وظائف البحث والتصفية:")
    test_search_functionality()
    
    print("\n📝 اختبار وظائف النماذج:")
    test_form_functionality()
    
    print("\n⏰ اختبار وظائف الحضور:")
    test_attendance_functionality()
    
    print("\n💰 اختبار وظائف الرواتب:")
    test_payroll_functionality()
    
    print("\n📊 اختبار الرسوم البيانية:")
    test_charts_and_statistics()
    
    print("\n📤 اختبار وظائف التصدير:")
    test_export_functionality()
    
    print("\n🌐 اختبار دعم اللغة العربية:")
    test_arabic_support()
    
    print("\n📱 اختبار التصميم المتجاوب:")
    test_responsive_design()
    
    # تلخيص النتائج
    print("\n" + "=" * 60)
    print("📊 ملخص نتائج الاختبار:")
    
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
        print("\n🎉 ممتاز! النظام يعمل بكفاءة عالية")
    elif success_rate >= 75:
        print("\n👍 جيد! النظام يعمل بشكل مقبول مع بعض التحسينات المطلوبة")
    else:
        print("\n⚠️  يحتاج تحسين! هناك مشاكل تحتاج إلى إصلاح")
    
    # حفظ النتائج في ملف
    with open('test_results.json', 'w', encoding='utf-8') as f:
        json.dump(TEST_RESULTS, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 تم حفظ النتائج التفصيلية في: test_results.json")
    
    return success_rate

if __name__ == "__main__":
    try:
        success_rate = run_comprehensive_test()
        exit(0 if success_rate >= 75 else 1)
    except KeyboardInterrupt:
        print("\n⏹️  تم إيقاف الاختبار بواسطة المستخدم")
        exit(1)
    except Exception as e:
        print(f"\n❌ خطأ عام في الاختبار: {str(e)}")
        exit(1)
