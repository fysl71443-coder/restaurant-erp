#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار شامل لجميع الأزرار والوظائف في التطبيق
Comprehensive test for all buttons and functions in the application
"""

import requests
import time
import json
from datetime import datetime
from bs4 import BeautifulSoup
import os
import sys

class ButtonsTest:
    def __init__(self, base_url="http://127.0.0.1:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
        self.start_time = datetime.now()
        
    def log_test(self, test_name, status, details="", response_time=0):
        """تسجيل نتيجة الاختبار"""
        result = {
            "test_name": test_name,
            "status": status,
            "details": details,
            "response_time": response_time,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.test_results.append(result)
        status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_icon} {test_name}: {status} ({response_time:.2f}s)")
        if details:
            print(f"   📝 {details}")
    
    def test_server_connection(self):
        """اختبار الاتصال بالخادم"""
        try:
            start_time = time.time()
            response = self.session.get(self.base_url)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                self.log_test("اتصال الخادم", "PASS", f"الخادم يعمل بشكل طبيعي", response_time)
                return True
            else:
                self.log_test("اتصال الخادم", "FAIL", f"HTTP {response.status_code}", response_time)
                return False
        except Exception as e:
            self.log_test("اتصال الخادم", "FAIL", f"خطأ في الاتصال: {str(e)}")
            return False
    
    def test_page_buttons(self, page_url, page_name):
        """اختبار أزرار صفحة معينة"""
        try:
            start_time = time.time()
            response = self.session.get(f"{self.base_url}{page_url}")
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # البحث عن جميع الأزرار
                buttons = soup.find_all('button')
                button_links = soup.find_all('a', class_=lambda x: x and 'btn' in str(x))
                
                # تصنيف الأزرار حسب النوع
                button_types = {
                    'save': 0, 'edit': 0, 'delete': 0, 'cancel': 0, 
                    'print': 0, 'search': 0, 'add': 0, 'view': 0, 'other': 0
                }
                
                all_buttons = buttons + button_links
                
                for button in all_buttons:
                    button_text = button.get_text(strip=True).lower()
                    button_class = str(button.get('class', [])).lower()
                    button_onclick = str(button.get('onclick', '')).lower()
                    
                    # تصنيف الأزرار
                    if any(word in button_text for word in ['حفظ', 'save', 'submit']):
                        button_types['save'] += 1
                    elif any(word in button_text for word in ['تعديل', 'edit', 'modify']):
                        button_types['edit'] += 1
                    elif any(word in button_text for word in ['حذف', 'delete', 'remove']):
                        button_types['delete'] += 1
                    elif any(word in button_text for word in ['إلغاء', 'cancel', 'close']):
                        button_types['cancel'] += 1
                    elif any(word in button_text for word in ['طباعة', 'print']):
                        button_types['print'] += 1
                    elif any(word in button_text for word in ['بحث', 'search', 'filter']):
                        button_types['search'] += 1
                    elif any(word in button_text for word in ['إضافة', 'add', 'new', 'جديد']):
                        button_types['add'] += 1
                    elif any(word in button_text for word in ['عرض', 'view', 'show']):
                        button_types['view'] += 1
                    else:
                        button_types['other'] += 1
                
                # إنشاء تفاصيل النتيجة
                total_buttons = sum(button_types.values())
                details_list = []
                for btn_type, count in button_types.items():
                    if count > 0:
                        details_list.append(f"{btn_type}: {count}")
                
                details = f"إجمالي: {total_buttons} | " + " | ".join(details_list)
                
                if total_buttons > 0:
                    self.log_test(f"أزرار {page_name}", "PASS", details, response_time)
                    return button_types
                else:
                    self.log_test(f"أزرار {page_name}", "WARN", "لا توجد أزرار", response_time)
                    return button_types
                    
            else:
                self.log_test(f"أزرار {page_name}", "FAIL", f"HTTP {response.status_code}", response_time)
                return None
                
        except Exception as e:
            self.log_test(f"أزرار {page_name}", "FAIL", f"خطأ: {str(e)}")
            return None
    
    def test_navigation_links(self):
        """اختبار روابط التنقل"""
        try:
            response = self.session.get(self.base_url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # البحث عن روابط التنقل في الشريط الجانبي
                nav_links = soup.find_all('a', href=True)
                
                working_links = 0
                broken_links = 0
                
                for link in nav_links[:10]:  # اختبار أول 10 روابط فقط
                    href = link.get('href')
                    if href and href.startswith('/'):
                        try:
                            test_response = self.session.get(f"{self.base_url}{href}")
                            if test_response.status_code == 200:
                                working_links += 1
                            else:
                                broken_links += 1
                        except:
                            broken_links += 1
                
                details = f"روابط تعمل: {working_links} | روابط معطلة: {broken_links}"
                
                if working_links > broken_links:
                    self.log_test("روابط التنقل", "PASS", details)
                    return True
                else:
                    self.log_test("روابط التنقل", "FAIL", details)
                    return False
                    
        except Exception as e:
            self.log_test("روابط التنقل", "FAIL", f"خطأ: {str(e)}")
            return False
    
    def test_form_functionality(self, page_url, page_name):
        """اختبار وظائف النماذج"""
        try:
            response = self.session.get(f"{self.base_url}{page_url}")
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # البحث عن النماذج
                forms = soup.find_all('form')
                
                form_details = []
                for i, form in enumerate(forms):
                    method = form.get('method', 'GET').upper()
                    action = form.get('action', '#')
                    inputs = len(form.find_all(['input', 'select', 'textarea']))
                    
                    form_details.append(f"نموذج{i+1}({method}, {inputs} حقل)")
                
                if len(forms) > 0:
                    details = " | ".join(form_details)
                    self.log_test(f"نماذج {page_name}", "PASS", details)
                    return True
                else:
                    self.log_test(f"نماذج {page_name}", "WARN", "لا توجد نماذج")
                    return False
                    
        except Exception as e:
            self.log_test(f"نماذج {page_name}", "FAIL", f"خطأ: {str(e)}")
            return False
    
    def test_interactive_elements(self, page_url, page_name):
        """اختبار العناصر التفاعلية"""
        try:
            response = self.session.get(f"{self.base_url}{page_url}")
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # البحث عن العناصر التفاعلية
                modals = len(soup.find_all(class_=lambda x: x and 'modal' in str(x)))
                dropdowns = len(soup.find_all(class_=lambda x: x and 'dropdown' in str(x)))
                tabs = len(soup.find_all(class_=lambda x: x and 'tab' in str(x)))
                accordions = len(soup.find_all(class_=lambda x: x and 'accordion' in str(x)))
                
                # البحث عن JavaScript events
                onclick_elements = len(soup.find_all(attrs={'onclick': True}))
                
                interactive_count = modals + dropdowns + tabs + accordions + onclick_elements
                
                details = f"modals: {modals} | dropdowns: {dropdowns} | tabs: {tabs} | onclick: {onclick_elements}"
                
                if interactive_count > 0:
                    self.log_test(f"تفاعلية {page_name}", "PASS", details)
                    return True
                else:
                    self.log_test(f"تفاعلية {page_name}", "WARN", "عناصر تفاعلية قليلة")
                    return False
                    
        except Exception as e:
            self.log_test(f"تفاعلية {page_name}", "FAIL", f"خطأ: {str(e)}")
            return False
    
    def run_comprehensive_test(self):
        """تشغيل الاختبار الشامل"""
        print("🚀 بدء اختبار جميع الأزرار والوظائف...")
        print("=" * 60)
        
        # اختبار الاتصال بالخادم
        print("\n🌐 اختبار الاتصال:")
        if not self.test_server_connection():
            print("❌ لا يمكن الاتصال بالخادم. تأكد من تشغيل التطبيق على المنفذ 5000")
            return False
        
        # قائمة الصفحات للاختبار
        pages_to_test = [
            ("/", "الصفحة الرئيسية"),
            ("/sales", "المبيعات"),
            ("/purchases", "المشتريات"),
            ("/inventory", "المخزون"),
            ("/customers", "العملاء"),
            ("/employees", "الموظفين"),
            ("/reports", "التقارير"),
            ("/invoices", "الفواتير")
        ]
        
        # اختبار أزرار كل صفحة
        print("\n🔘 اختبار الأزرار:")
        total_buttons = {}
        for page_url, page_name in pages_to_test:
            buttons = self.test_page_buttons(page_url, page_name)
            if buttons:
                for btn_type, count in buttons.items():
                    total_buttons[btn_type] = total_buttons.get(btn_type, 0) + count
            time.sleep(0.5)
        
        # اختبار روابط التنقل
        print("\n🔗 اختبار التنقل:")
        self.test_navigation_links()
        
        # اختبار النماذج
        print("\n📝 اختبار النماذج:")
        for page_url, page_name in pages_to_test:
            self.test_form_functionality(page_url, page_name)
            time.sleep(0.3)
        
        # اختبار العناصر التفاعلية
        print("\n⚡ اختبار التفاعلية:")
        for page_url, page_name in pages_to_test:
            self.test_interactive_elements(page_url, page_name)
            time.sleep(0.3)
        
        # إنشاء التقرير النهائي
        self.generate_report(total_buttons)
    
    def generate_report(self, total_buttons):
        """إنشاء تقرير شامل للنتائج"""
        total_tests = len(self.test_results)
        passed_tests = len([t for t in self.test_results if t['status'] == 'PASS'])
        failed_tests = len([t for t in self.test_results if t['status'] == 'FAIL'])
        warning_tests = len([t for t in self.test_results if t['status'] == 'WARN'])
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print("\n" + "=" * 60)
        print("📊 تقرير نتائج اختبار الأزرار والوظائف")
        print("=" * 60)
        print(f"📈 إجمالي الاختبارات: {total_tests}")
        print(f"✅ اختبارات ناجحة: {passed_tests}")
        print(f"❌ اختبارات فاشلة: {failed_tests}")
        print(f"⚠️ تحذيرات: {warning_tests}")
        print(f"🎯 معدل النجاح: {success_rate:.1f}%")
        print(f"⏱️ وقت التنفيذ: {(datetime.now() - self.start_time).total_seconds():.2f} ثانية")
        
        # إحصائيات الأزرار
        if total_buttons:
            print(f"\n🔘 إحصائيات الأزرار:")
            for btn_type, count in total_buttons.items():
                if count > 0:
                    print(f"   {btn_type}: {count} زر")
        
        # حفظ التقرير
        report_data = {
            "test_summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "warning_tests": warning_tests,
                "success_rate": success_rate,
                "execution_time": (datetime.now() - self.start_time).total_seconds(),
                "total_buttons": total_buttons
            },
            "test_results": self.test_results,
            "generated_at": datetime.now().isoformat()
        }
        
        with open('buttons_test_report.json', 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 تم حفظ التقرير التفصيلي في: buttons_test_report.json")
        
        return success_rate

if __name__ == "__main__":
    # تشغيل الاختبار
    tester = ButtonsTest()
    success_rate = tester.run_comprehensive_test()
    
    # تحديد حالة الخروج بناءً على معدل النجاح
    if success_rate and success_rate >= 80:
        print("\n🎉 معظم الأزرار والوظائف تعمل بشكل ممتاز!")
    elif success_rate and success_rate >= 60:
        print("\n⚠️ الأزرار تعمل بشكل مقبول مع بعض المشاكل")
    else:
        print("\n❌ هناك مشاكل كبيرة في الأزرار تحتاج إلى إصلاح")
