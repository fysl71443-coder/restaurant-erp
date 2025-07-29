#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import sys

class FinancialReportsTest:
    def __init__(self):
        self.base_url = "http://127.0.0.1:5000"
        self.session = requests.Session()
        self.test_results = []
        
    def log_test(self, test_name, success, details=""):
        """تسجيل نتيجة الاختبار"""
        status = "✅ نجح" if success else "❌ فشل"
        self.test_results.append({
            'name': test_name,
            'success': success,
            'details': details
        })
        print(f"{status} {test_name}")
        if details:
            print(f"   التفاصيل: {details}")
    
    def login(self):
        """تسجيل الدخول"""
        try:
            login_data = {
                'username': 'admin',
                'password': 'admin123'
            }
            response = self.session.post(f"{self.base_url}/login", data=login_data)
            if response.status_code == 200:
                # تحقق من وجود كلمات مفتاحية تدل على نجاح تسجيل الدخول
                if any(keyword in response.text.lower() for keyword in ['dashboard', 'لوحة التحكم', 'الرئيسية', 'admin']):
                    self.log_test("تسجيل الدخول", True, "تم تسجيل الدخول بنجاح")
                    return True
                else:
                    self.log_test("تسجيل الدخول", False, "فشل في التحقق من تسجيل الدخول")
                    return True  # نتابع الاختبار حتى لو لم نتأكد من تسجيل الدخول
            else:
                self.log_test("تسجيل الدخول", False, f"فشل تسجيل الدخول: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("تسجيل الدخول", False, f"خطأ: {str(e)}")
            return False
    
    def test_financial_reports_access(self):
        """اختبار الوصول لشاشة التقارير المالية"""
        try:
            response = self.session.get(f"{self.base_url}/reports")
            if response.status_code == 200:
                self.log_test("الوصول لشاشة التقارير المالية", True, "تم تحميل الصفحة بنجاح")
                return response.text
            else:
                self.log_test("الوصول لشاشة التقارير المالية", False, f"خطأ HTTP: {response.status_code}")
                return None
        except Exception as e:
            self.log_test("الوصول لشاشة التقارير المالية", False, f"خطأ: {str(e)}")
            return None
    
    def test_financial_reports_page_elements(self, html_content):
        """اختبار عناصر شاشة التقارير المالية"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # اختبار وجود العنوان
        titles = soup.find_all(['h1', 'h2', 'h3'])
        title_found = any("التقارير المالية" in title.text or "financial" in title.text.lower() or "reports" in title.text.lower() for title in titles)
        self.log_test("عنوان شاشة التقارير المالية", title_found, "عنوان التقارير المالية موجود" if title_found else "العنوان غير موجود")
        
        # اختبار وجود بطاقات الإحصائيات
        stats_cards = soup.find_all(['div'], class_=lambda x: x and ('card' in x or 'stats' in x))
        if len(stats_cards) >= 4:
            self.log_test("بطاقات إحصائيات التقارير المالية", True, f"تم العثور على {len(stats_cards)} بطاقة إحصائيات")
            
            # اختبار الإحصائيات المطلوبة
            expected_stats = ["إجمالي الإيرادات", "إجمالي المصروفات", "صافي الربح", "نسبة الربحية"]
            page_text = soup.get_text()
            for stat in expected_stats:
                if stat in page_text:
                    self.log_test(f"إحصائية: {stat}", True, "موجودة في البطاقات")
                else:
                    self.log_test(f"إحصائية: {stat}", False, "غير موجودة في البطاقات")
        else:
            self.log_test("بطاقات إحصائيات التقارير المالية", False, f"عدد البطاقات غير كافي: {len(stats_cards)}")
    
    def test_financial_reports_tables(self, html_content):
        """اختبار جداول التقارير المالية"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # اختبار وجود جداول التقارير
        tables = soup.find_all('table')
        if len(tables) >= 1:
            self.log_test("جداول التقارير المالية", True, f"تم العثور على {len(tables)} جدول")
            
            # البحث عن الجدول الرئيسي للتقارير
            main_table = soup.find('table', {'id': 'reportsTable'})
            if not main_table:
                # البحث في أكبر جدول
                main_table = max(tables, key=lambda t: len(t.find_all(['th', 'td'])))
            
            # اختبار رؤوس الجدول الرئيسي
            table_headers = []
            if main_table:
                headers = main_table.find_all(['th', 'td'])
                for header in headers:
                    table_headers.append(header.text.strip())
            
            expected_headers = ["نوع التقرير", "الفترة", "المبلغ", "النسبة", "التاريخ"]
            for header in expected_headers:
                if any(header in found for found in table_headers):
                    self.log_test(f"عمود: {header}", True, "موجود في الجدول")
                else:
                    self.log_test(f"عمود: {header}", False, "غير موجود في الجدول")
        else:
            self.log_test("جداول التقارير المالية", False, "لا يوجد جداول")
    
    def test_financial_reports_forms(self, html_content):
        """اختبار نماذج التقارير المالية"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # اختبار وجود النماذج
        forms = soup.find_all('form')
        if len(forms) >= 1:
            self.log_test("نماذج التقارير المالية", True, f"تم العثور على {len(forms)} نموذج")
            
            # اختبار حقول النماذج
            form_inputs = soup.find_all(['input', 'select', 'textarea'])
            if len(form_inputs) >= 8:
                self.log_test("حقول نماذج التقارير المالية", True, f"تم العثور على {len(form_inputs)} حقل")
            else:
                self.log_test("حقول نماذج التقارير المالية", False, f"عدد الحقول غير كافي: {len(form_inputs)}")
        else:
            self.log_test("نماذج التقارير المالية", False, "لا يوجد نماذج")
    
    def test_financial_reports_buttons(self, html_content):
        """اختبار أزرار التقارير المالية"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        expected_buttons = [
            "إنشاء تقرير",
            "تصدير التقرير", 
            "طباعة التقرير",
            "تحديث البيانات",
            "عرض التفاصيل"
        ]
        
        page_text = soup.get_text()
        for button in expected_buttons:
            if button in page_text:
                self.log_test(f"زر: {button}", True, "موجود في الصفحة")
            else:
                self.log_test(f"زر: {button}", False, "غير موجود في الصفحة")
    
    def test_financial_reports_charts(self, html_content):
        """اختبار الرسوم البيانية للتقارير المالية"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # اختبار وجود مكتبة Chart.js
        chart_scripts = soup.find_all('script', src=lambda x: x and 'chart' in x.lower())
        if chart_scripts:
            self.log_test("مكتبة Chart.js للتقارير المالية", True, "مكتبة الرسوم البيانية موجودة")
        else:
            self.log_test("مكتبة Chart.js للتقارير المالية", False, "مكتبة الرسوم البيانية غير موجودة")
        
        # اختبار وجود عناصر الرسوم البيانية
        chart_elements = soup.find_all('canvas')
        if len(chart_elements) >= 2:
            self.log_test("الرسوم البيانية للتقارير المالية", True, f"تم العثور على {len(chart_elements)} رسم بياني")
        else:
            self.log_test("الرسوم البيانية للتقارير المالية", False, f"عدد الرسوم البيانية غير كافي: {len(chart_elements)}")
    
    def test_date_filters(self, html_content):
        """اختبار مرشحات التاريخ"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        date_inputs = soup.find_all('input', type='date')
        month_selects = soup.find_all('select', id=lambda x: x and 'month' in x.lower())
        year_selects = soup.find_all('select', id=lambda x: x and 'year' in x.lower())
        
        total_date_filters = len(date_inputs) + len(month_selects) + len(year_selects)
        
        if total_date_filters >= 2:
            self.log_test("مرشحات التاريخ للتقارير المالية", True, f"تم العثور على {total_date_filters} مرشح تاريخ")
        else:
            self.log_test("مرشحات التاريخ للتقارير المالية", False, f"عدد مرشحات التاريخ غير كافي: {total_date_filters}")
    
    def test_report_types(self, html_content):
        """اختبار أنواع التقارير"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        expected_report_types = ["تقرير الأرباح والخسائر", "تقرير الميزانية العمومية", "تقرير التدفق النقدي", "تقرير المبيعات"]
        page_text = soup.get_text()
        
        found_types = 0
        for report_type in expected_report_types:
            if report_type in page_text:
                found_types += 1
        
        if found_types >= 3:
            self.log_test("أنواع التقارير المالية", True, f"تم العثور على {found_types} نوع تقرير")
        else:
            self.log_test("أنواع التقارير المالية", False, f"عدد أنواع التقارير غير كافي: {found_types}")
    
    def test_responsive_design(self, html_content):
        """اختبار التصميم المتجاوب"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        responsive_classes = ['col-lg-', 'col-md-', 'row', 'container', 'd-flex']
        page_html = str(soup)
        
        found_classes = [cls for cls in responsive_classes if cls in page_html]
        
        if len(found_classes) >= 4:
            self.log_test("التصميم المتجاوب للتقارير المالية", True, f"يستخدم Bootstrap classes: {', '.join(found_classes)}")
        else:
            self.log_test("التصميم المتجاوب للتقارير المالية", False, f"عدد فئات Bootstrap غير كافي: {len(found_classes)}")
    
    def run_all_tests(self):
        """تشغيل جميع الاختبارات"""
        print("🧪 بدء اختبار شاشة التقارير المالية الشامل")
        print("=" * 50)
        
        # تسجيل الدخول
        if not self.login():
            return
        
        # الحصول على محتوى الصفحة
        html_content = self.test_financial_reports_access()
        if not html_content:
            return
        
        # اختبار عناصر الشاشة
        self.test_financial_reports_page_elements(html_content)
        
        # اختبار الجداول
        self.test_financial_reports_tables(html_content)
        
        # اختبار النماذج
        self.test_financial_reports_forms(html_content)
        
        # اختبار الأزرار
        self.test_financial_reports_buttons(html_content)
        
        # اختبار الرسوم البيانية
        self.test_financial_reports_charts(html_content)
        
        # اختبار مرشحات التاريخ
        self.test_date_filters(html_content)
        
        # اختبار أنواع التقارير
        self.test_report_types(html_content)
        
        # اختبار التصميم المتجاوب
        self.test_responsive_design(html_content)
        
        # عرض النتائج النهائية
        self.show_results()
    
    def show_results(self):
        """عرض نتائج الاختبارات"""
        print("\n" + "=" * 50)
        print("📊 نتائج اختبار شاشة التقارير المالية")
        print("=" * 50)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print(f"إجمالي الاختبارات: {total_tests}")
        print(f"نجح: {passed_tests}")
        print(f"فشل: {failed_tests}")
        print(f"معدل النجاح: {success_rate:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ الاختبارات الفاشلة:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['name']}: {result['details']}")
        
        print("=" * 50)

if __name__ == "__main__":
    test = FinancialReportsTest()
    test.run_all_tests()
