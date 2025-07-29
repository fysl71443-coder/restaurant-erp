#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار شامل لشاشة الرواتب
يختبر جميع العناصر والوظائف في شاشة الرواتب
"""

import requests
import time
from bs4 import BeautifulSoup
import json

class PayrollTester:
    def __init__(self, base_url="http://127.0.0.1:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
        
    def log_test(self, test_name, status, details=""):
        """تسجيل نتيجة الاختبار"""
        result = {
            "test": test_name,
            "status": "✅ نجح" if status else "❌ فشل",
            "details": details
        }
        self.test_results.append(result)
        print(f"{result['status']} {test_name}")
        if details:
            print(f"   التفاصيل: {details}")
    
    def login(self):
        """تسجيل الدخول للنظام"""
        try:
            # الحصول على صفحة تسجيل الدخول
            login_page = self.session.get(f"{self.base_url}/login")
            if login_page.status_code != 200:
                self.log_test("الوصول لصفحة تسجيل الدخول", False, f"كود الحالة: {login_page.status_code}")
                return False
            
            # تسجيل الدخول
            login_data = {
                'username': 'admin',
                'password': 'admin123'
            }
            
            response = self.session.post(f"{self.base_url}/login", data=login_data)
            
            # التحقق من نجاح تسجيل الدخول
            if response.status_code == 200 and ("لوحة التحكم" in response.text or "dashboard" in response.url):
                self.log_test("تسجيل الدخول", True, "تم تسجيل الدخول بنجاح")
                return True
            else:
                self.log_test("تسجيل الدخول", False, f"فشل في تسجيل الدخول - كود: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("تسجيل الدخول", False, f"خطأ: {str(e)}")
            return False
    
    def test_payroll_page_access(self):
        """اختبار الوصول لشاشة الرواتب"""
        try:
            response = self.session.get(f"{self.base_url}/payroll")
            
            if response.status_code == 200:
                self.log_test("الوصول لشاشة الرواتب", True, "تم تحميل الصفحة بنجاح")
                return response.text
            else:
                self.log_test("الوصول لشاشة الرواتب", False, f"كود الحالة: {response.status_code}")
                return None
                
        except Exception as e:
            self.log_test("الوصول لشاشة الرواتب", False, f"خطأ: {str(e)}")
            return None
    
    def test_payroll_page_elements(self, html_content):
        """اختبار عناصر شاشة الرواتب"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # اختبار وجود العنوان
        titles = soup.find_all(['h1', 'h2', 'h3'])
        title_found = any("الرواتب" in title.text or "payroll" in title.text.lower() for title in titles)
        if title_found:
            self.log_test("عنوان شاشة الرواتب", True, "عنوان الرواتب موجود")
        else:
            self.log_test("عنوان شاشة الرواتب", False, "عنوان الرواتب غير موجود")
        
        # اختبار وجود بطاقات الإحصائيات
        stats_cards = soup.find_all('div', class_='stats-card')
        if len(stats_cards) >= 4:
            self.log_test("بطاقات إحصائيات الرواتب", True, f"تم العثور على {len(stats_cards)} بطاقة إحصائيات")
            
            # اختبار محتوى البطاقات
            expected_stats = ["إجمالي الرواتب", "عدد الموظفين", "متوسط الراتب", "إجمالي البدلات"]
            found_stats = []
            
            for card in stats_cards:
                label = card.find('div', class_='stats-label')
                if label:
                    found_stats.append(label.text.strip())
            
            for stat in expected_stats:
                if any(stat in found for found in found_stats):
                    self.log_test(f"إحصائية: {stat}", True, "موجودة في البطاقات")
                else:
                    self.log_test(f"إحصائية: {stat}", False, "غير موجودة في البطاقات")
        else:
            self.log_test("بطاقات إحصائيات الرواتب", False, f"عدد البطاقات غير كافي: {len(stats_cards)}")
    
    def test_payroll_tables(self, html_content):
        """اختبار جداول الرواتب"""
        soup = BeautifulSoup(html_content, 'html.parser')

        # اختبار وجود جداول الرواتب
        tables = soup.find_all('table')
        if len(tables) >= 1:
            self.log_test("جداول الرواتب", True, f"تم العثور على {len(tables)} جدول")

            # البحث عن الجدول الرئيسي للرواتب
            main_table = soup.find('table', {'id': 'payrollTable'})
            if not main_table:
                # البحث في أكبر جدول
                main_table = max(tables, key=lambda t: len(t.find_all(['th', 'td'])))

            # اختبار رؤوس الجدول الرئيسي
            table_headers = []
            if main_table:
                headers = main_table.find_all(['th', 'td'])
                for header in headers:
                    table_headers.append(header.text.strip())

            expected_headers = ["اسم الموظف", "الراتب الأساسي", "البدلات", "الخصومات", "صافي الراتب"]
            for header in expected_headers:
                if any(header in found for found in table_headers):
                    self.log_test(f"عمود: {header}", True, "موجود في الجدول")
                else:
                    self.log_test(f"عمود: {header}", False, "غير موجود في الجدول")
        else:
            self.log_test("جداول الرواتب", False, "لا يوجد جداول")
    
    def test_payroll_forms(self, html_content):
        """اختبار نماذج الرواتب"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # اختبار وجود النماذج
        forms = soup.find_all('form')
        if len(forms) >= 1:
            self.log_test("نماذج الرواتب", True, f"تم العثور على {len(forms)} نموذج")
            
            # اختبار حقول النماذج
            form_inputs = soup.find_all(['input', 'select', 'textarea'])
            if len(form_inputs) >= 5:
                self.log_test("حقول نماذج الرواتب", True, f"تم العثور على {len(form_inputs)} حقل")
            else:
                self.log_test("حقول نماذج الرواتب", False, f"عدد الحقول غير كافي: {len(form_inputs)}")
        else:
            self.log_test("نماذج الرواتب", False, "لا توجد نماذج")
    
    def test_payroll_buttons(self, html_content):
        """اختبار أزرار الرواتب"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # اختبار وجود أزرار الإجراءات
        action_buttons = soup.find_all('button') + soup.find_all('a', class_='btn')
        button_texts = [btn.text.strip() for btn in action_buttons]
        
        expected_buttons = ["إضافة راتب", "حساب الراتب", "تصدير كشف الرواتب", "طباعة", "إنشاء كشف راتب"]
        for button in expected_buttons:
            if any(button in text for text in button_texts):
                self.log_test(f"زر: {button}", True, "موجود في الصفحة")
            else:
                self.log_test(f"زر: {button}", False, "غير موجود في الصفحة")
    
    def test_payroll_charts(self, html_content):
        """اختبار الرسوم البيانية للرواتب"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # اختبار وجود Chart.js
        if "Chart" in html_content or "chart.js" in html_content:
            self.log_test("مكتبة Chart.js للرواتب", True, "مكتبة الرسوم البيانية موجودة")
        else:
            self.log_test("مكتبة Chart.js للرواتب", False, "مكتبة الرسوم البيانية غير موجودة")
        
        # اختبار وجود الرسوم البيانية
        charts = soup.find_all('canvas')
        if len(charts) >= 2:
            self.log_test("الرسوم البيانية للرواتب", True, f"تم العثور على {len(charts)} رسم بياني")
        else:
            self.log_test("الرسوم البيانية للرواتب", False, f"عدد الرسوم البيانية غير كافي: {len(charts)}")
    
    def test_employee_selection(self, html_content):
        """اختبار اختيار الموظفين"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # البحث عن قوائم اختيار الموظفين
        employee_selects = soup.find_all('select')
        employee_found = False
        for select in employee_selects:
            if select.get('name') and 'employee' in select.get('name', '').lower():
                employee_found = True
                break
            # البحث في الخيارات
            options = select.find_all('option')
            for option in options:
                if any(word in option.text for word in ["موظف", "employee"]):
                    employee_found = True
                    break
        
        if employee_found:
            self.log_test("اختيار الموظفين", True, "قائمة اختيار الموظفين موجودة")
        else:
            self.log_test("اختيار الموظفين", False, "قائمة اختيار الموظفين غير موجودة")
    
    def test_salary_calculation(self, html_content):
        """اختبار حساب الراتب"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # البحث عن حقول حساب الراتب
        salary_inputs = soup.find_all('input', {'type': 'number'})
        if len(salary_inputs) >= 3:
            self.log_test("حقول حساب الراتب", True, f"تم العثور على {len(salary_inputs)} حقل رقمي")
        else:
            self.log_test("حقول حساب الراتب", False, f"عدد الحقول الرقمية غير كافي: {len(salary_inputs)}")
        
        # البحث عن أزرار الحساب
        calc_buttons = soup.find_all('button')
        calc_button_found = any("حساب" in btn.text for btn in calc_buttons)
        if calc_button_found:
            self.log_test("زر حساب الراتب", True, "زر الحساب موجود")
        else:
            self.log_test("زر حساب الراتب", False, "زر الحساب غير موجود")
    
    def test_responsive_design(self, html_content):
        """اختبار التصميم المتجاوب"""
        # اختبار وجود Bootstrap classes في النص
        bootstrap_indicators = ['col-lg-', 'col-md-', 'row', 'container', 'd-flex']
        found_classes = []
        
        for class_name in bootstrap_indicators:
            if class_name in html_content:
                found_classes.append(class_name)
        
        if len(found_classes) >= 3:
            self.log_test("التصميم المتجاوب للرواتب", True, f"يستخدم Bootstrap classes: {', '.join(found_classes)}")
        else:
            self.log_test("التصميم المتجاوب للرواتب", False, f"عدد Bootstrap classes غير كافي: {found_classes}")
    
    def test_payroll_filters(self, html_content):
        """اختبار مرشحات الرواتب"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # البحث عن مرشحات التاريخ
        date_inputs = soup.find_all('input', {'type': 'date'})
        if len(date_inputs) >= 1:
            self.log_test("مرشحات التاريخ للرواتب", True, f"تم العثور على {len(date_inputs)} مرشح تاريخ")
        else:
            self.log_test("مرشحات التاريخ للرواتب", False, f"عدد مرشحات التاريخ غير كافي: {len(date_inputs)}")
        
        # البحث عن مرشحات الأقسام
        dept_selects = soup.find_all('select')
        dept_found = False
        for select in dept_selects:
            options = select.find_all('option')
            for option in options:
                if any(dept in option.text for dept in ["قسم", "إدارة", "department"]):
                    dept_found = True
                    break
        
        if dept_found:
            self.log_test("مرشحات الأقسام", True, "تم العثور على مرشحات الأقسام")
        else:
            self.log_test("مرشحات الأقسام", False, "لا توجد مرشحات أقسام")
    
    def run_all_tests(self):
        """تشغيل جميع الاختبارات"""
        print("🧪 بدء اختبار شاشة الرواتب الشامل")
        print("=" * 50)
        
        # تسجيل الدخول
        if not self.login():
            print("❌ فشل في تسجيل الدخول - توقف الاختبار")
            return False
        
        # اختبار الوصول لشاشة الرواتب
        html_content = self.test_payroll_page_access()
        if not html_content:
            print("❌ فشل في الوصول لشاشة الرواتب - توقف الاختبار")
            return False
        
        # اختبار عناصر الشاشة
        self.test_payroll_page_elements(html_content)
        
        # اختبار الجداول
        self.test_payroll_tables(html_content)
        
        # اختبار النماذج
        self.test_payroll_forms(html_content)
        
        # اختبار الأزرار
        self.test_payroll_buttons(html_content)
        
        # اختبار الرسوم البيانية
        self.test_payroll_charts(html_content)
        
        # اختبار اختيار الموظفين
        self.test_employee_selection(html_content)
        
        # اختبار حساب الراتب
        self.test_salary_calculation(html_content)
        
        # اختبار التصميم المتجاوب
        self.test_responsive_design(html_content)
        
        # اختبار المرشحات
        self.test_payroll_filters(html_content)
        
        # عرض النتائج النهائية
        self.show_final_results()
        
        return True
    
    def show_final_results(self):
        """عرض النتائج النهائية"""
        print("\n" + "=" * 50)
        print("📊 نتائج اختبار شاشة الرواتب")
        print("=" * 50)
        
        passed = sum(1 for result in self.test_results if "✅" in result['status'])
        failed = sum(1 for result in self.test_results if "❌" in result['status'])
        total = len(self.test_results)
        
        print(f"إجمالي الاختبارات: {total}")
        print(f"نجح: {passed}")
        print(f"فشل: {failed}")
        print(f"معدل النجاح: {(passed/total)*100:.1f}%")
        
        if failed > 0:
            print("\n❌ الاختبارات الفاشلة:")
            for result in self.test_results:
                if "❌" in result['status']:
                    print(f"  - {result['test']}: {result['details']}")
        
        print("\n" + "=" * 50)

if __name__ == "__main__":
    tester = PayrollTester()
    tester.run_all_tests()
