#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار شامل لشاشة ضريبة القيمة المضافة
يختبر جميع العناصر والوظائف في شاشة ضريبة القيمة المضافة
"""

import requests
import time
from bs4 import BeautifulSoup
import json

class VATTester:
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
    
    def test_vat_page_access(self):
        """اختبار الوصول لشاشة ضريبة القيمة المضافة"""
        try:
            response = self.session.get(f"{self.base_url}/vat")
            
            if response.status_code == 200:
                self.log_test("الوصول لشاشة ضريبة القيمة المضافة", True, "تم تحميل الصفحة بنجاح")
                return response.text
            else:
                self.log_test("الوصول لشاشة ضريبة القيمة المضافة", False, f"كود الحالة: {response.status_code}")
                return None
                
        except Exception as e:
            self.log_test("الوصول لشاشة ضريبة القيمة المضافة", False, f"خطأ: {str(e)}")
            return None
    
    def test_vat_page_elements(self, html_content):
        """اختبار عناصر شاشة ضريبة القيمة المضافة"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # اختبار وجود العنوان
        titles = soup.find_all(['h1', 'h2', 'h3'])
        title_found = any("ضريبة القيمة المضافة" in title.text or "VAT" in title.text for title in titles)
        if title_found:
            self.log_test("عنوان شاشة ضريبة القيمة المضافة", True, "عنوان الضريبة موجود")
        else:
            self.log_test("عنوان شاشة ضريبة القيمة المضافة", False, "عنوان الضريبة غير موجود")
        
        # اختبار وجود بطاقات الإحصائيات
        stats_cards = soup.find_all('div', class_='stats-card')
        if len(stats_cards) >= 4:
            self.log_test("بطاقات إحصائيات الضريبة", True, f"تم العثور على {len(stats_cards)} بطاقة إحصائيات")
            
            # اختبار محتوى البطاقات
            expected_stats = ["إجمالي الضريبة المستحقة", "إجمالي الضريبة المدفوعة", "صافي الضريبة", "معدل الضريبة"]
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
            self.log_test("بطاقات إحصائيات الضريبة", False, f"عدد البطاقات غير كافي: {len(stats_cards)}")
    
    def test_vat_calculations(self, html_content):
        """اختبار حاسبة الضريبة"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # البحث عن حاسبة الضريبة
        calculator_inputs = soup.find_all('input', {'type': 'number'})
        if len(calculator_inputs) >= 2:
            self.log_test("حاسبة الضريبة", True, f"تم العثور على {len(calculator_inputs)} حقل إدخال رقمي")
        else:
            self.log_test("حاسبة الضريبة", False, f"عدد حقول الإدخال غير كافي: {len(calculator_inputs)}")
        
        # البحث عن أزرار الحساب
        calc_buttons = soup.find_all('button')
        calc_button_found = any("حساب" in btn.text for btn in calc_buttons)
        if calc_button_found:
            self.log_test("زر حساب الضريبة", True, "زر الحساب موجود")
        else:
            self.log_test("زر حساب الضريبة", False, "زر الحساب غير موجود")
    
    def test_vat_reports(self, html_content):
        """اختبار تقارير الضريبة"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # اختبار وجود جداول التقارير
        tables = soup.find_all('table')
        if len(tables) >= 1:
            self.log_test("جداول تقارير الضريبة", True, f"تم العثور على {len(tables)} جدول")
            
            # اختبار رؤوس الجداول
            table_headers = []
            for table in tables:
                headers = table.find_all(['th', 'td'])
                for header in headers:
                    table_headers.append(header.text.strip())
            
            expected_headers = ["الفاتورة", "التاريخ", "المبلغ", "الضريبة", "الإجمالي"]
            for header in expected_headers:
                if any(header in found for found in table_headers):
                    self.log_test(f"عمود: {header}", True, "موجود في الجدول")
                else:
                    self.log_test(f"عمود: {header}", False, "غير موجود في الجدول")
        else:
            self.log_test("جداول تقارير الضريبة", False, "لا يوجد جداول")
    
    def test_vat_settings(self, html_content):
        """اختبار إعدادات الضريبة"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # البحث عن إعدادات معدل الضريبة
        rate_inputs = soup.find_all('input', {'type': ['number', 'text']})
        settings_found = False
        for input_field in rate_inputs:
            if input_field.get('name') and 'rate' in input_field.get('name', '').lower():
                settings_found = True
                break
        
        if settings_found:
            self.log_test("إعدادات معدل الضريبة", True, "حقل معدل الضريبة موجود")
        else:
            self.log_test("إعدادات معدل الضريبة", False, "حقل معدل الضريبة غير موجود")
    
    def test_vat_buttons(self, html_content):
        """اختبار أزرار الضريبة"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # اختبار وجود أزرار الإجراءات
        action_buttons = soup.find_all('button') + soup.find_all('a', class_='btn')
        button_texts = [btn.text.strip() for btn in action_buttons]
        
        expected_buttons = ["تصدير التقرير", "طباعة", "حساب الضريبة", "حفظ الإعدادات"]
        for button in expected_buttons:
            if any(button in text for text in button_texts):
                self.log_test(f"زر: {button}", True, "موجود في الصفحة")
            else:
                self.log_test(f"زر: {button}", False, "غير موجود في الصفحة")
    
    def test_vat_charts(self, html_content):
        """اختبار الرسوم البيانية للضريبة"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # اختبار وجود Chart.js
        if "Chart" in html_content or "chart.js" in html_content:
            self.log_test("مكتبة Chart.js للضريبة", True, "مكتبة الرسوم البيانية موجودة")
        else:
            self.log_test("مكتبة Chart.js للضريبة", False, "مكتبة الرسوم البيانية غير موجودة")
        
        # اختبار وجود الرسوم البيانية
        charts = soup.find_all('canvas')
        if len(charts) >= 2:
            self.log_test("الرسوم البيانية للضريبة", True, f"تم العثور على {len(charts)} رسم بياني")
        else:
            self.log_test("الرسوم البيانية للضريبة", False, f"عدد الرسوم البيانية غير كافي: {len(charts)}")
    
    def test_responsive_design(self, html_content):
        """اختبار التصميم المتجاوب"""
        # اختبار وجود Bootstrap classes في النص
        bootstrap_indicators = ['col-lg-', 'col-md-', 'row', 'container', 'd-flex']
        found_classes = []
        
        for class_name in bootstrap_indicators:
            if class_name in html_content:
                found_classes.append(class_name)
        
        if len(found_classes) >= 3:
            self.log_test("التصميم المتجاوب للضريبة", True, f"يستخدم Bootstrap classes: {', '.join(found_classes)}")
        else:
            self.log_test("التصميم المتجاوب للضريبة", False, f"عدد Bootstrap classes غير كافي: {found_classes}")
    
    def test_vat_forms(self, html_content):
        """اختبار نماذج الضريبة"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # اختبار وجود النماذج
        forms = soup.find_all('form')
        if len(forms) >= 1:
            self.log_test("نماذج الضريبة", True, f"تم العثور على {len(forms)} نموذج")
            
            # اختبار حقول النماذج
            form_inputs = soup.find_all(['input', 'select', 'textarea'])
            if len(form_inputs) >= 5:
                self.log_test("حقول النماذج", True, f"تم العثور على {len(form_inputs)} حقل")
            else:
                self.log_test("حقول النماذج", False, f"عدد الحقول غير كافي: {len(form_inputs)}")
        else:
            self.log_test("نماذج الضريبة", False, "لا توجد نماذج")
    
    def run_all_tests(self):
        """تشغيل جميع الاختبارات"""
        print("🧪 بدء اختبار شاشة ضريبة القيمة المضافة الشامل")
        print("=" * 50)
        
        # تسجيل الدخول
        if not self.login():
            print("❌ فشل في تسجيل الدخول - توقف الاختبار")
            return False
        
        # اختبار الوصول لشاشة الضريبة
        html_content = self.test_vat_page_access()
        if not html_content:
            print("❌ فشل في الوصول لشاشة الضريبة - توقف الاختبار")
            return False
        
        # اختبار عناصر الشاشة
        self.test_vat_page_elements(html_content)
        
        # اختبار حاسبة الضريبة
        self.test_vat_calculations(html_content)
        
        # اختبار تقارير الضريبة
        self.test_vat_reports(html_content)
        
        # اختبار إعدادات الضريبة
        self.test_vat_settings(html_content)
        
        # اختبار الأزرار
        self.test_vat_buttons(html_content)
        
        # اختبار الرسوم البيانية
        self.test_vat_charts(html_content)
        
        # اختبار التصميم المتجاوب
        self.test_responsive_design(html_content)
        
        # اختبار النماذج
        self.test_vat_forms(html_content)
        
        # عرض النتائج النهائية
        self.show_final_results()
        
        return True
    
    def show_final_results(self):
        """عرض النتائج النهائية"""
        print("\n" + "=" * 50)
        print("📊 نتائج اختبار شاشة ضريبة القيمة المضافة")
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
    tester = VATTester()
    tester.run_all_tests()
