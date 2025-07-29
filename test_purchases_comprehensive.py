#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار شامل لشاشة المشتريات
يختبر جميع العناصر والوظائف في شاشة المشتريات
"""

import requests
import time
from bs4 import BeautifulSoup
import json

class PurchasesTester:
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
    
    def test_purchases_page_access(self):
        """اختبار الوصول لشاشة المشتريات"""
        try:
            response = self.session.get(f"{self.base_url}/purchases")
            
            if response.status_code == 200:
                self.log_test("الوصول لشاشة المشتريات", True, "تم تحميل الصفحة بنجاح")
                return response.text
            else:
                self.log_test("الوصول لشاشة المشتريات", False, f"كود الحالة: {response.status_code}")
                return None
                
        except Exception as e:
            self.log_test("الوصول لشاشة المشتريات", False, f"خطأ: {str(e)}")
            return None
    
    def test_purchases_page_elements(self, html_content):
        """اختبار عناصر شاشة المشتريات"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # اختبار وجود العنوان
        titles = soup.find_all(['h1', 'h2', 'h3'])
        title_found = any("المشتريات" in title.text for title in titles)
        if title_found:
            self.log_test("عنوان شاشة المشتريات", True, "عنوان المشتريات موجود")
        else:
            self.log_test("عنوان شاشة المشتريات", False, "عنوان المشتريات غير موجود")
        
        # اختبار وجود بطاقات الإحصائيات
        stats_cards = soup.find_all('div', class_='stats-card')
        if len(stats_cards) >= 3:
            self.log_test("بطاقات إحصائيات المشتريات", True, f"تم العثور على {len(stats_cards)} بطاقة إحصائيات")
            
            # اختبار محتوى البطاقات
            expected_stats = ["إجمالي المشتريات", "عدد الفواتير", "متوسط الفاتورة"]
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
            self.log_test("بطاقات إحصائيات المشتريات", False, f"عدد البطاقات غير كافي: {len(stats_cards)}")
        
        # اختبار وجود جدول الفواتير
        tables = soup.find_all('table')
        if len(tables) >= 1:
            self.log_test("جدول فواتير المشتريات", True, f"تم العثور على {len(tables)} جدول")
            
            # اختبار رؤوس الجدول
            table_headers = []
            for table in tables:
                headers = table.find_all(['th', 'td'])
                for header in headers:
                    table_headers.append(header.text.strip())
            
            expected_headers = ["رقم الفاتورة", "المورد", "التاريخ", "المبلغ"]
            for header in expected_headers:
                if any(header in found for found in table_headers):
                    self.log_test(f"عمود: {header}", True, "موجود في الجدول")
                else:
                    self.log_test(f"عمود: {header}", False, "غير موجود في الجدول")
        else:
            self.log_test("جدول فواتير المشتريات", False, "لا يوجد جداول")
        
        # اختبار وجود أزرار الإجراءات
        action_buttons = soup.find_all('button') + soup.find_all('a', class_='btn')
        button_texts = [btn.text.strip() for btn in action_buttons]
        
        expected_buttons = ["إضافة فاتورة", "بحث", "تصدير", "طباعة"]
        for button in expected_buttons:
            if any(button in text for text in button_texts):
                self.log_test(f"زر: {button}", True, "موجود في الصفحة")
            else:
                self.log_test(f"زر: {button}", False, "غير موجود في الصفحة")
    
    def test_purchases_charts(self, html_content):
        """اختبار الرسوم البيانية في شاشة المشتريات"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # اختبار وجود الرسوم البيانية
        charts = soup.find_all('canvas')
        if len(charts) >= 1:
            self.log_test("الرسوم البيانية للمشتريات", True, f"تم العثور على {len(charts)} رسم بياني")
        else:
            self.log_test("الرسوم البيانية للمشتريات", False, "لا توجد رسوم بيانية")
        
        # اختبار وجود Chart.js
        if "Chart" in html_content or "chart.js" in html_content:
            self.log_test("مكتبة Chart.js", True, "مكتبة الرسوم البيانية موجودة")
        else:
            self.log_test("مكتبة Chart.js", False, "مكتبة الرسوم البيانية غير موجودة")
    
    def test_add_purchase_invoice_functionality(self):
        """اختبار وظيفة إضافة فاتورة مشتريات جديدة"""
        try:
            # اختبار الوصول لصفحة إضافة فاتورة مشتريات
            response = self.session.get(f"{self.base_url}/add_purchase_invoice")
            
            if response.status_code == 200:
                self.log_test("صفحة إضافة فاتورة مشتريات", True, "يمكن الوصول للصفحة")
                
                # اختبار وجود النموذج
                soup = BeautifulSoup(response.text, 'html.parser')
                forms = soup.find_all('form')
                
                if forms:
                    self.log_test("نموذج إضافة فاتورة مشتريات", True, f"تم العثور على {len(forms)} نموذج")
                    
                    # اختبار حقول النموذج
                    form = forms[0]
                    inputs = form.find_all(['input', 'select', 'textarea'])
                    
                    expected_fields = ["supplier", "date", "amount", "product"]
                    found_fields = []
                    
                    for input_field in inputs:
                        name = input_field.get('name', '')
                        id_attr = input_field.get('id', '')
                        found_fields.extend([name, id_attr])
                    
                    for field in expected_fields:
                        if any(field in found for found in found_fields):
                            self.log_test(f"حقل: {field}", True, "موجود في النموذج")
                        else:
                            self.log_test(f"حقل: {field}", False, "غير موجود في النموذج")
                else:
                    self.log_test("نموذج إضافة فاتورة مشتريات", False, "لا يوجد نماذج في الصفحة")
            else:
                self.log_test("صفحة إضافة فاتورة مشتريات", False, f"كود الحالة: {response.status_code}")
                
        except Exception as e:
            self.log_test("صفحة إضافة فاتورة مشتريات", False, f"خطأ: {str(e)}")
    
    def test_search_functionality(self, html_content):
        """اختبار وظيفة البحث"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # البحث عن حقول البحث
        search_inputs = soup.find_all('input', {'type': 'search'}) + \
                       soup.find_all('input', {'placeholder': lambda x: x and 'بحث' in x}) + \
                       soup.find_all('input', {'name': lambda x: x and 'search' in x})
        
        if search_inputs:
            self.log_test("وظيفة البحث", True, f"تم العثور على {len(search_inputs)} حقل بحث")
        else:
            self.log_test("وظيفة البحث", False, "لا توجد حقول بحث")
    
    def test_responsive_design(self, html_content):
        """اختبار التصميم المتجاوب"""
        # اختبار وجود Bootstrap classes في النص
        bootstrap_indicators = ['col-lg-', 'col-md-', 'row', 'container', 'd-flex']
        found_classes = []
        
        for class_name in bootstrap_indicators:
            if class_name in html_content:
                found_classes.append(class_name)
        
        if len(found_classes) >= 3:
            self.log_test("التصميم المتجاوب للمشتريات", True, f"يستخدم Bootstrap classes: {', '.join(found_classes)}")
        else:
            self.log_test("التصميم المتجاوب للمشتريات", False, f"عدد Bootstrap classes غير كافي: {found_classes}")
    
    def run_all_tests(self):
        """تشغيل جميع الاختبارات"""
        print("🧪 بدء اختبار شاشة المشتريات الشامل")
        print("=" * 50)
        
        # تسجيل الدخول
        if not self.login():
            print("❌ فشل في تسجيل الدخول - توقف الاختبار")
            return False
        
        # اختبار الوصول لشاشة المشتريات
        html_content = self.test_purchases_page_access()
        if not html_content:
            print("❌ فشل في الوصول لشاشة المشتريات - توقف الاختبار")
            return False
        
        # اختبار عناصر الشاشة
        self.test_purchases_page_elements(html_content)
        
        # اختبار الرسوم البيانية
        self.test_purchases_charts(html_content)
        
        # اختبار وظيفة إضافة فاتورة
        self.test_add_purchase_invoice_functionality()
        
        # اختبار وظيفة البحث
        self.test_search_functionality(html_content)
        
        # اختبار التصميم المتجاوب
        self.test_responsive_design(html_content)
        
        # عرض النتائج النهائية
        self.show_final_results()
        
        return True
    
    def show_final_results(self):
        """عرض النتائج النهائية"""
        print("\n" + "=" * 50)
        print("📊 نتائج اختبار شاشة المشتريات")
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
    tester = PurchasesTester()
    tester.run_all_tests()
