#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار شامل للشاشة الرئيسية (Dashboard)
يختبر جميع العناصر والوظائف في الصفحة الرئيسية
"""

import requests
import time
from bs4 import BeautifulSoup
import json

class DashboardTester:
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
            if response.status_code == 200 and "لوحة التحكم" in response.text:
                self.log_test("تسجيل الدخول", True, "تم تسجيل الدخول بنجاح")
                return True
            else:
                self.log_test("تسجيل الدخول", False, f"فشل في تسجيل الدخول - كود: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("تسجيل الدخول", False, f"خطأ: {str(e)}")
            return False
    
    def test_dashboard_access(self):
        """اختبار الوصول للشاشة الرئيسية"""
        try:
            response = self.session.get(f"{self.base_url}/")
            
            if response.status_code == 200:
                self.log_test("الوصول للشاشة الرئيسية", True, "تم تحميل الصفحة بنجاح")
                return response.text
            else:
                self.log_test("الوصول للشاشة الرئيسية", False, f"كود الحالة: {response.status_code}")
                return None
                
        except Exception as e:
            self.log_test("الوصول للشاشة الرئيسية", False, f"خطأ: {str(e)}")
            return None
    
    def test_dashboard_elements(self, html_content):
        """اختبار عناصر الشاشة الرئيسية"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # اختبار وجود العنوان الرئيسي
        titles = soup.find_all('h2')
        title_found = any("لوحة التحكم" in title.text for title in titles)
        if title_found:
            self.log_test("العنوان الرئيسي", True, "عنوان لوحة التحكم موجود")
        else:
            self.log_test("العنوان الرئيسي", False, "عنوان لوحة التحكم غير موجود")
        
        # اختبار وجود بطاقات الإحصائيات
        stats_cards = soup.find_all('div', class_='stats-card')
        if len(stats_cards) >= 4:
            self.log_test("بطاقات الإحصائيات", True, f"تم العثور على {len(stats_cards)} بطاقة إحصائيات")
            
            # اختبار محتوى البطاقات
            expected_stats = ["إجمالي المبيعات", "إجمالي المشتريات", "صافي الربح", "عدد العملاء"]
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
            self.log_test("بطاقات الإحصائيات", False, f"عدد البطاقات غير كافي: {len(stats_cards)}")
        
        # اختبار وجود الرسوم البيانية
        charts = soup.find_all('canvas')
        if len(charts) >= 2:
            self.log_test("الرسوم البيانية", True, f"تم العثور على {len(charts)} رسم بياني")
        else:
            self.log_test("الرسوم البيانية", False, f"عدد الرسوم البيانية غير كافي: {len(charts)}")
        
        # اختبار وجود القائمة الجانبية
        sidebar = soup.find('div', class_='sidebar')
        if sidebar:
            self.log_test("القائمة الجانبية", True, "القائمة الجانبية موجودة")
            
            # اختبار روابط القائمة
            nav_links = sidebar.find_all('a')
            expected_links = ["المبيعات", "المشتريات", "التحليلات", "الرواتب", "التقارير"]
            
            for expected_link in expected_links:
                found = any(expected_link in link.text for link in nav_links)
                self.log_test(f"رابط: {expected_link}", found, "موجود في القائمة" if found else "غير موجود في القائمة")
        else:
            self.log_test("القائمة الجانبية", False, "القائمة الجانبية غير موجودة")
    
    def test_navigation_links(self):
        """اختبار روابط التنقل"""
        navigation_tests = [
            ("/sales", "المبيعات"),
            ("/purchases", "المشتريات"), 
            ("/analytics", "التحليلات"),
            ("/vat", "ضريبة القيمة المضافة"),
            ("/payroll", "الرواتب"),
            ("/reports", "التقارير")
        ]
        
        for url, name in navigation_tests:
            try:
                response = self.session.get(f"{self.base_url}{url}")
                if response.status_code == 200:
                    self.log_test(f"رابط {name}", True, f"يعمل بشكل صحيح - كود: {response.status_code}")
                else:
                    self.log_test(f"رابط {name}", False, f"لا يعمل - كود: {response.status_code}")
            except Exception as e:
                self.log_test(f"رابط {name}", False, f"خطأ: {str(e)}")
    
    def test_responsive_design(self, html_content):
        """اختبار التصميم المتجاوب"""
        # اختبار وجود Bootstrap classes في النص
        bootstrap_indicators = ['col-lg-', 'col-md-', 'row', 'container-fluid', 'd-flex']
        found_classes = []

        for class_name in bootstrap_indicators:
            if class_name in html_content:
                found_classes.append(class_name)

        if len(found_classes) >= 3:
            self.log_test("التصميم المتجاوب", True, f"يستخدم Bootstrap classes: {', '.join(found_classes)}")
        else:
            self.log_test("التصميم المتجاوب", False, f"عدد Bootstrap classes غير كافي: {found_classes}")
    
    def run_all_tests(self):
        """تشغيل جميع الاختبارات"""
        print("🧪 بدء اختبار الشاشة الرئيسية الشامل")
        print("=" * 50)
        
        # تسجيل الدخول
        if not self.login():
            print("❌ فشل في تسجيل الدخول - توقف الاختبار")
            return False
        
        # اختبار الوصول للشاشة الرئيسية
        html_content = self.test_dashboard_access()
        if not html_content:
            print("❌ فشل في الوصول للشاشة الرئيسية - توقف الاختبار")
            return False
        
        # اختبار عناصر الشاشة
        self.test_dashboard_elements(html_content)
        
        # اختبار روابط التنقل
        self.test_navigation_links()
        
        # اختبار التصميم المتجاوب
        self.test_responsive_design(html_content)
        
        # عرض النتائج النهائية
        self.show_final_results()
        
        return True
    
    def show_final_results(self):
        """عرض النتائج النهائية"""
        print("\n" + "=" * 50)
        print("📊 نتائج اختبار الشاشة الرئيسية")
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
    tester = DashboardTester()
    tester.run_all_tests()
