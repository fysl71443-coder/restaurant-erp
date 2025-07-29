#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار شامل لشاشة التحليلات
يختبر جميع العناصر والوظائف في شاشة التحليلات
"""

import requests
import time
from bs4 import BeautifulSoup
import json

class AnalyticsTester:
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
    
    def test_analytics_page_access(self):
        """اختبار الوصول لشاشة التحليلات"""
        try:
            response = self.session.get(f"{self.base_url}/analytics")
            
            if response.status_code == 200:
                self.log_test("الوصول لشاشة التحليلات", True, "تم تحميل الصفحة بنجاح")
                return response.text
            else:
                self.log_test("الوصول لشاشة التحليلات", False, f"كود الحالة: {response.status_code}")
                return None
                
        except Exception as e:
            self.log_test("الوصول لشاشة التحليلات", False, f"خطأ: {str(e)}")
            return None
    
    def test_analytics_page_elements(self, html_content):
        """اختبار عناصر شاشة التحليلات"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # اختبار وجود العنوان
        titles = soup.find_all(['h1', 'h2', 'h3'])
        title_found = any("التحليلات" in title.text or "تحليلات" in title.text for title in titles)
        if title_found:
            self.log_test("عنوان شاشة التحليلات", True, "عنوان التحليلات موجود")
        else:
            self.log_test("عنوان شاشة التحليلات", False, "عنوان التحليلات غير موجود")
        
        # اختبار وجود بطاقات الإحصائيات الرئيسية
        stats_cards = soup.find_all('div', class_='stats-card')
        if len(stats_cards) >= 4:
            self.log_test("بطاقات إحصائيات التحليلات", True, f"تم العثور على {len(stats_cards)} بطاقة إحصائيات")
            
            # اختبار محتوى البطاقات
            expected_stats = ["إجمالي الإيرادات", "إجمالي المصروفات", "صافي الربح", "عدد العملاء"]
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
            self.log_test("بطاقات إحصائيات التحليلات", False, f"عدد البطاقات غير كافي: {len(stats_cards)}")
        
        # اختبار وجود الرسوم البيانية
        charts = soup.find_all('canvas')
        if len(charts) >= 3:
            self.log_test("الرسوم البيانية في التحليلات", True, f"تم العثور على {len(charts)} رسم بياني")
        else:
            self.log_test("الرسوم البيانية في التحليلات", False, f"عدد الرسوم البيانية غير كافي: {len(charts)}")
        
        # اختبار وجود جداول التحليلات
        tables = soup.find_all('table')
        if len(tables) >= 1:
            self.log_test("جداول التحليلات", True, f"تم العثور على {len(tables)} جدول")
            
            # اختبار رؤوس الجداول
            table_headers = []
            for table in tables:
                headers = table.find_all(['th', 'td'])
                for header in headers:
                    table_headers.append(header.text.strip())
            
            expected_headers = ["الفترة", "الإيرادات", "المصروفات", "الربح"]
            for header in expected_headers:
                if any(header in found for found in table_headers):
                    self.log_test(f"عمود: {header}", True, "موجود في الجدول")
                else:
                    self.log_test(f"عمود: {header}", False, "غير موجود في الجدول")
        else:
            self.log_test("جداول التحليلات", False, "لا يوجد جداول")
    
    def test_analytics_charts(self, html_content):
        """اختبار الرسوم البيانية في شاشة التحليلات"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # اختبار وجود Chart.js
        if "Chart" in html_content or "chart.js" in html_content:
            self.log_test("مكتبة Chart.js للتحليلات", True, "مكتبة الرسوم البيانية موجودة")
        else:
            self.log_test("مكتبة Chart.js للتحليلات", False, "مكتبة الرسوم البيانية غير موجودة")
        
        # اختبار أنواع الرسوم البيانية المختلفة
        chart_types = ["line", "bar", "pie", "doughnut"]
        for chart_type in chart_types:
            if chart_type in html_content.lower():
                self.log_test(f"رسم بياني من نوع {chart_type}", True, f"يوجد رسم بياني من نوع {chart_type}")
            else:
                self.log_test(f"رسم بياني من نوع {chart_type}", False, f"لا يوجد رسم بياني من نوع {chart_type}")
    
    def test_analytics_filters(self, html_content):
        """اختبار مرشحات التحليلات"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # البحث عن مرشحات التاريخ
        date_inputs = soup.find_all('input', {'type': 'date'})
        if len(date_inputs) >= 2:
            self.log_test("مرشحات التاريخ", True, f"تم العثور على {len(date_inputs)} مرشح تاريخ")
        else:
            self.log_test("مرشحات التاريخ", False, f"عدد مرشحات التاريخ غير كافي: {len(date_inputs)}")
        
        # البحث عن مرشحات الفترة
        period_selects = soup.find_all('select')
        period_found = False
        for select in period_selects:
            options = select.find_all('option')
            for option in options:
                if any(period in option.text for period in ["شهري", "سنوي", "يومي"]):
                    period_found = True
                    break
        
        if period_found:
            self.log_test("مرشحات الفترة", True, "تم العثور على مرشحات الفترة")
        else:
            self.log_test("مرشحات الفترة", False, "لا توجد مرشحات فترة")
    
    def test_analytics_buttons(self, html_content):
        """اختبار أزرار التحليلات"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # اختبار وجود أزرار الإجراءات
        action_buttons = soup.find_all('button') + soup.find_all('a', class_='btn')
        button_texts = [btn.text.strip() for btn in action_buttons]
        
        expected_buttons = ["تصدير التقرير", "طباعة", "تحديث البيانات", "عرض التفاصيل"]
        for button in expected_buttons:
            if any(button in text for text in button_texts):
                self.log_test(f"زر: {button}", True, "موجود في الصفحة")
            else:
                self.log_test(f"زر: {button}", False, "غير موجود في الصفحة")
    
    def test_responsive_design(self, html_content):
        """اختبار التصميم المتجاوب"""
        # اختبار وجود Bootstrap classes في النص
        bootstrap_indicators = ['col-lg-', 'col-md-', 'row', 'container', 'd-flex']
        found_classes = []
        
        for class_name in bootstrap_indicators:
            if class_name in html_content:
                found_classes.append(class_name)
        
        if len(found_classes) >= 3:
            self.log_test("التصميم المتجاوب للتحليلات", True, f"يستخدم Bootstrap classes: {', '.join(found_classes)}")
        else:
            self.log_test("التصميم المتجاوب للتحليلات", False, f"عدد Bootstrap classes غير كافي: {found_classes}")
    
    def test_data_visualization(self, html_content):
        """اختبار تصور البيانات"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # اختبار وجود مؤشرات الأداء الرئيسية (KPIs)
        kpi_indicators = soup.find_all('div', class_=['kpi', 'metric', 'indicator'])
        if len(kpi_indicators) >= 1:
            self.log_test("مؤشرات الأداء الرئيسية", True, f"تم العثور على {len(kpi_indicators)} مؤشر أداء")
        else:
            self.log_test("مؤشرات الأداء الرئيسية", False, "لا توجد مؤشرات أداء")
        
        # اختبار وجود عناصر تفاعلية
        interactive_elements = soup.find_all(['select', 'input', 'button'])
        if len(interactive_elements) >= 5:
            self.log_test("العناصر التفاعلية", True, f"تم العثور على {len(interactive_elements)} عنصر تفاعلي")
        else:
            self.log_test("العناصر التفاعلية", False, f"عدد العناصر التفاعلية غير كافي: {len(interactive_elements)}")
    
    def run_all_tests(self):
        """تشغيل جميع الاختبارات"""
        print("🧪 بدء اختبار شاشة التحليلات الشامل")
        print("=" * 50)
        
        # تسجيل الدخول
        if not self.login():
            print("❌ فشل في تسجيل الدخول - توقف الاختبار")
            return False
        
        # اختبار الوصول لشاشة التحليلات
        html_content = self.test_analytics_page_access()
        if not html_content:
            print("❌ فشل في الوصول لشاشة التحليلات - توقف الاختبار")
            return False
        
        # اختبار عناصر الشاشة
        self.test_analytics_page_elements(html_content)
        
        # اختبار الرسوم البيانية
        self.test_analytics_charts(html_content)
        
        # اختبار المرشحات
        self.test_analytics_filters(html_content)
        
        # اختبار الأزرار
        self.test_analytics_buttons(html_content)
        
        # اختبار التصميم المتجاوب
        self.test_responsive_design(html_content)
        
        # اختبار تصور البيانات
        self.test_data_visualization(html_content)
        
        # عرض النتائج النهائية
        self.show_final_results()
        
        return True
    
    def show_final_results(self):
        """عرض النتائج النهائية"""
        print("\n" + "=" * 50)
        print("📊 نتائج اختبار شاشة التحليلات")
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
    tester = AnalyticsTester()
    tester.run_all_tests()
