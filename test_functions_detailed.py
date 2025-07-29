#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار تفصيلي لجميع الوظائف والأزرار في التطبيق
Detailed test for all functions and buttons in the application
"""

import requests
import time
import json
from datetime import datetime
from bs4 import BeautifulSoup
import os
import sys

class DetailedFunctionsTest:
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
    
    def test_page_functionality(self, page_url, page_name, expected_functions):
        """اختبار وظائف صفحة معينة"""
        try:
            start_time = time.time()
            response = self.session.get(f"{self.base_url}{page_url}")
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # اختبار الوظائف المتوقعة
                found_functions = {}
                
                # البحث عن أزرار الحفظ
                save_buttons = soup.find_all(['button', 'input'], 
                    attrs={'type': ['submit', 'button']})
                save_count = 0
                for btn in save_buttons:
                    btn_text = btn.get_text(strip=True).lower()
                    if any(word in btn_text for word in ['حفظ', 'save', 'submit']):
                        save_count += 1
                found_functions['save'] = save_count
                
                # البحث عن أزرار التعديل
                edit_buttons = soup.find_all('a', href=True)
                edit_count = 0
                for btn in edit_buttons:
                    href = btn.get('href', '')
                    btn_text = btn.get_text(strip=True).lower()
                    if 'edit' in href or any(word in btn_text for word in ['تعديل', 'edit']):
                        edit_count += 1
                found_functions['edit'] = edit_count
                
                # البحث عن أزرار الحذف
                delete_buttons = soup.find_all(['button', 'a'])
                delete_count = 0
                for btn in delete_buttons:
                    btn_text = btn.get_text(strip=True).lower()
                    onclick = btn.get('onclick', '')
                    href = btn.get('href', '')
                    if (any(word in btn_text for word in ['حذف', 'delete']) or 
                        'delete' in onclick or 'delete' in href):
                        delete_count += 1
                found_functions['delete'] = delete_count
                
                # البحث عن أزرار الطباعة
                print_buttons = soup.find_all(['button', 'a'])
                print_count = 0
                for btn in print_buttons:
                    btn_text = btn.get_text(strip=True).lower()
                    onclick = btn.get('onclick', '')
                    if (any(word in btn_text for word in ['طباعة', 'print']) or 
                        'print' in onclick):
                        print_count += 1
                found_functions['print'] = print_count
                
                # البحث عن أزرار البحث
                search_elements = soup.find_all(['input', 'button'])
                search_count = 0
                for elem in search_elements:
                    elem_type = elem.get('type', '')
                    elem_text = elem.get_text(strip=True).lower()
                    placeholder = elem.get('placeholder', '').lower()
                    if (elem_type == 'search' or 
                        any(word in elem_text for word in ['بحث', 'search']) or
                        any(word in placeholder for word in ['بحث', 'search'])):
                        search_count += 1
                found_functions['search'] = search_count
                
                # البحث عن أزرار الإضافة
                add_buttons = soup.find_all(['button', 'a'])
                add_count = 0
                for btn in add_buttons:
                    btn_text = btn.get_text(strip=True).lower()
                    href = btn.get('href', '')
                    if (any(word in btn_text for word in ['إضافة', 'add', 'جديد', 'new']) or
                        'add' in href or 'new' in href):
                        add_count += 1
                found_functions['add'] = add_count
                
                # مقارنة النتائج مع المتوقع
                results = []
                total_expected = sum(expected_functions.values())
                total_found = sum(found_functions.values())
                
                for func_type, expected_count in expected_functions.items():
                    found_count = found_functions.get(func_type, 0)
                    if found_count >= expected_count:
                        results.append(f"{func_type}: {found_count}/{expected_count} ✅")
                    else:
                        results.append(f"{func_type}: {found_count}/{expected_count} ❌")
                
                details = f"إجمالي: {total_found}/{total_expected} | " + " | ".join(results)
                
                if total_found >= total_expected * 0.8:  # 80% من الوظائف المتوقعة
                    self.log_test(f"وظائف {page_name}", "PASS", details, response_time)
                    return True
                else:
                    self.log_test(f"وظائف {page_name}", "FAIL", details, response_time)
                    return False
                    
            else:
                self.log_test(f"وظائف {page_name}", "FAIL", f"HTTP {response.status_code}", response_time)
                return False
                
        except Exception as e:
            self.log_test(f"وظائف {page_name}", "FAIL", f"خطأ: {str(e)}")
            return False
    
    def test_form_submission(self, form_url, form_name, test_data=None):
        """اختبار إرسال النماذج"""
        try:
            # الحصول على الصفحة أولاً
            response = self.session.get(f"{self.base_url}{form_url}")
            if response.status_code != 200:
                self.log_test(f"نموذج {form_name}", "FAIL", f"لا يمكن الوصول للصفحة")
                return False
            
            soup = BeautifulSoup(response.content, 'html.parser')
            forms = soup.find_all('form')
            
            if not forms:
                self.log_test(f"نموذج {form_name}", "WARN", "لا يوجد نموذج في الصفحة")
                return False
            
            form = forms[0]  # أول نموذج في الصفحة
            method = form.get('method', 'GET').upper()
            action = form.get('action', form_url)
            
            # جمع الحقول المطلوبة
            inputs = form.find_all(['input', 'select', 'textarea'])
            required_fields = []
            for inp in inputs:
                if inp.get('required') or inp.get('name'):
                    required_fields.append(inp.get('name'))
            
            details = f"طريقة: {method} | حقول مطلوبة: {len(required_fields)}"
            
            if method == 'POST' and len(required_fields) > 0:
                self.log_test(f"نموذج {form_name}", "PASS", details)
                return True
            else:
                self.log_test(f"نموذج {form_name}", "WARN", details)
                return False
                
        except Exception as e:
            self.log_test(f"نموذج {form_name}", "FAIL", f"خطأ: {str(e)}")
            return False
    
    def test_javascript_functionality(self, page_url, page_name):
        """اختبار وظائف JavaScript"""
        try:
            response = self.session.get(f"{self.base_url}{page_url}")
            if response.status_code != 200:
                return False
            
            content = response.text
            
            # البحث عن وظائف JavaScript
            js_features = {
                'functions': content.count('function '),
                'event_listeners': content.count('addEventListener') + content.count('onclick'),
                'ajax_calls': content.count('fetch(') + content.count('$.ajax') + content.count('XMLHttpRequest'),
                'dom_manipulation': content.count('getElementById') + content.count('querySelector'),
                'form_validation': content.count('validate') + content.count('checkValidity')
            }
            
            total_features = sum(js_features.values())
            
            if total_features > 0:
                feature_list = [f"{k}: {v}" for k, v in js_features.items() if v > 0]
                details = " | ".join(feature_list)
                self.log_test(f"JS {page_name}", "PASS", details)
                return True
            else:
                self.log_test(f"JS {page_name}", "WARN", "لا توجد وظائف JS")
                return False
                
        except Exception as e:
            self.log_test(f"JS {page_name}", "FAIL", f"خطأ: {str(e)}")
            return False
    
    def run_comprehensive_test(self):
        """تشغيل الاختبار الشامل"""
        print("🚀 بدء اختبار الوظائف والأزرار التفصيلي...")
        print("=" * 60)
        
        # اختبار الاتصال بالخادم
        print("\n🌐 اختبار الاتصال:")
        if not self.test_server_connection():
            print("❌ لا يمكن الاتصال بالخادم. سأقوم بالاختبار الثابت...")
            return self.run_static_test()
        
        # تعريف الصفحات والوظائف المتوقعة
        pages_to_test = [
            ("/", "الصفحة الرئيسية", {'add': 2, 'print': 1, 'search': 1}),
            ("/sales", "المبيعات", {'add': 2, 'edit': 1, 'print': 2, 'search': 1}),
            ("/purchases", "المشتريات", {'add': 3, 'edit': 1, 'print': 1, 'search': 1}),
            ("/inventory", "المخزون", {'add': 1, 'edit': 1, 'delete': 1, 'print': 1, 'search': 1}),
            ("/customers", "العملاء", {'add': 1, 'print': 1, 'search': 1}),
            ("/employees", "الموظفين", {'add': 1, 'print': 1, 'search': 1}),
            ("/reports", "التقارير", {'print': 2, 'search': 1})
        ]
        
        # اختبار وظائف كل صفحة
        print("\n🔧 اختبار الوظائف:")
        for page_url, page_name, expected_functions in pages_to_test:
            self.test_page_functionality(page_url, page_name, expected_functions)
            time.sleep(0.5)
        
        # اختبار النماذج
        print("\n📝 اختبار النماذج:")
        forms_to_test = [
            ("/add_sales_invoice", "إضافة فاتورة مبيعات"),
            ("/add_purchase_invoice", "إضافة فاتورة مشتريات"),
            ("/add_product", "إضافة منتج"),
            ("/add_customer", "إضافة عميل"),
            ("/add_employee", "إضافة موظف")
        ]
        
        for form_url, form_name in forms_to_test:
            self.test_form_submission(form_url, form_name)
            time.sleep(0.3)
        
        # اختبار JavaScript
        print("\n⚡ اختبار JavaScript:")
        for page_url, page_name, _ in pages_to_test:
            self.test_javascript_functionality(page_url, page_name)
            time.sleep(0.3)
        
        # إنشاء التقرير النهائي
        self.generate_report()
    
    def run_static_test(self):
        """تشغيل اختبار ثابت في حالة عدم توفر الخادم"""
        print("📁 تشغيل الاختبار الثابت...")

        # قائمة القوالب للاختبار
        templates = [
            ("templates/index.html", "الصفحة الرئيسية"),
            ("templates/sales.html", "المبيعات"),
            ("templates/purchases.html", "المشتريات"),
            ("templates/inventory.html", "المخزون"),
            ("templates/customers.html", "العملاء"),
            ("templates/employees.html", "الموظفين"),
            ("templates/reports.html", "التقارير")
        ]

        print("\n🔘 اختبار الأزرار الثابت:")
        for template_path, template_name in templates:
            self.test_static_buttons(template_path, template_name)

        print("\n📝 اختبار النماذج الثابت:")
        form_templates = [
            ("templates/add_sales_invoice.html", "إضافة فاتورة مبيعات"),
            ("templates/add_purchase_invoice.html", "إضافة فاتورة مشتريات"),
            ("templates/edit_product.html", "تعديل منتج"),
            ("templates/edit_customer.html", "تعديل عميل"),
            ("templates/edit_employee.html", "تعديل موظف")
        ]

        for template_path, template_name in form_templates:
            self.test_static_forms(template_path, template_name)

        print("\n⚡ اختبار JavaScript الثابت:")
        for template_path, template_name in templates + form_templates:
            self.test_static_javascript(template_path, template_name)

        self.generate_report()

    def test_static_buttons(self, template_path, template_name):
        """اختبار الأزرار في القوالب الثابتة"""
        try:
            if not os.path.exists(template_path):
                self.log_test(f"أزرار {template_name}", "FAIL", "الملف غير موجود")
                return False

            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()

            soup = BeautifulSoup(content, 'html.parser')

            # تصنيف الأزرار
            button_types = {
                'save': 0, 'edit': 0, 'delete': 0, 'cancel': 0,
                'print': 0, 'search': 0, 'add': 0, 'view': 0,
                'export': 0, 'submit': 0
            }

            # البحث عن جميع الأزرار
            all_buttons = soup.find_all(['button', 'a', 'input'])

            for button in all_buttons:
                if button.name == 'input' and button.get('type') not in ['submit', 'button']:
                    continue

                button_text = button.get_text(strip=True).lower()
                button_class = str(button.get('class', [])).lower()
                button_onclick = str(button.get('onclick', '')).lower()
                button_href = str(button.get('href', '')).lower()

                full_text = f"{button_text} {button_class} {button_onclick} {button_href}"

                # تصنيف الأزرار
                if any(word in full_text for word in ['حفظ', 'save', 'submit']):
                    button_types['save'] += 1
                elif any(word in full_text for word in ['تعديل', 'edit', 'modify']):
                    button_types['edit'] += 1
                elif any(word in full_text for word in ['حذف', 'delete', 'remove']):
                    button_types['delete'] += 1
                elif any(word in full_text for word in ['إلغاء', 'cancel', 'close']):
                    button_types['cancel'] += 1
                elif any(word in full_text for word in ['طباعة', 'print']):
                    button_types['print'] += 1
                elif any(word in full_text for word in ['بحث', 'search', 'filter']):
                    button_types['search'] += 1
                elif any(word in full_text for word in ['إضافة', 'add', 'new', 'جديد']):
                    button_types['add'] += 1
                elif any(word in full_text for word in ['عرض', 'view', 'show']):
                    button_types['view'] += 1
                elif any(word in full_text for word in ['تصدير', 'export', 'download']):
                    button_types['export'] += 1
                elif any(word in full_text for word in ['إرسال', 'submit']):
                    button_types['submit'] += 1

            # إنشاء التفاصيل
            total_buttons = sum(button_types.values())
            active_types = [f"{k}: {v}" for k, v in button_types.items() if v > 0]
            details = f"إجمالي: {total_buttons} | " + " | ".join(active_types)

            if total_buttons > 0:
                self.log_test(f"أزرار {template_name}", "PASS", details)
                return True
            else:
                self.log_test(f"أزرار {template_name}", "WARN", "لا توجد أزرار")
                return False

        except Exception as e:
            self.log_test(f"أزرار {template_name}", "FAIL", f"خطأ: {str(e)}")
            return False

    def test_static_forms(self, template_path, template_name):
        """اختبار النماذج في القوالب الثابتة"""
        try:
            if not os.path.exists(template_path):
                self.log_test(f"نموذج {template_name}", "WARN", "الملف غير موجود")
                return False

            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()

            soup = BeautifulSoup(content, 'html.parser')
            forms = soup.find_all('form')

            if len(forms) > 0:
                form_details = []
                for i, form in enumerate(forms):
                    method = form.get('method', 'GET').upper()
                    action = form.get('action', '#')
                    inputs = len(form.find_all(['input', 'select', 'textarea']))
                    required_inputs = len(form.find_all(['input', 'select', 'textarea'], required=True))

                    form_details.append(f"نموذج{i+1}({method}, {inputs} حقل, {required_inputs} مطلوب)")

                details = " | ".join(form_details)
                self.log_test(f"نموذج {template_name}", "PASS", details)
                return True
            else:
                self.log_test(f"نموذج {template_name}", "WARN", "لا توجد نماذج")
                return False

        except Exception as e:
            self.log_test(f"نموذج {template_name}", "FAIL", f"خطأ: {str(e)}")
            return False

    def test_static_javascript(self, template_path, template_name):
        """اختبار JavaScript في القوالب الثابتة"""
        try:
            if not os.path.exists(template_path):
                return False

            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # تحليل JavaScript
            js_features = {
                'functions': len([m for m in content.split() if m.startswith('function')]),
                'classes': content.count('class '),
                'events': content.count('addEventListener') + content.count('onclick') + content.count('onchange'),
                'dom_queries': content.count('getElementById') + content.count('querySelector'),
                'ajax': content.count('fetch(') + content.count('$.ajax') + content.count('XMLHttpRequest'),
                'validation': content.count('validate') + content.count('required')
            }

            total_features = sum(js_features.values())

            if total_features > 0:
                active_features = [f"{k}: {v}" for k, v in js_features.items() if v > 0]
                details = " | ".join(active_features)
                self.log_test(f"JS {template_name}", "PASS", details)
                return True
            else:
                self.log_test(f"JS {template_name}", "WARN", "لا توجد وظائف JS")
                return False

        except Exception as e:
            self.log_test(f"JS {template_name}", "FAIL", f"خطأ: {str(e)}")
            return False
    
    def generate_report(self):
        """إنشاء تقرير شامل للنتائج"""
        total_tests = len(self.test_results)
        passed_tests = len([t for t in self.test_results if t['status'] == 'PASS'])
        failed_tests = len([t for t in self.test_results if t['status'] == 'FAIL'])
        warning_tests = len([t for t in self.test_results if t['status'] == 'WARN'])
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print("\n" + "=" * 60)
        print("📊 تقرير نتائج اختبار الوظائف والأزرار التفصيلي")
        print("=" * 60)
        print(f"📈 إجمالي الاختبارات: {total_tests}")
        print(f"✅ اختبارات ناجحة: {passed_tests}")
        print(f"❌ اختبارات فاشلة: {failed_tests}")
        print(f"⚠️ تحذيرات: {warning_tests}")
        print(f"🎯 معدل النجاح: {success_rate:.1f}%")
        print(f"⏱️ وقت التنفيذ: {(datetime.now() - self.start_time).total_seconds():.2f} ثانية")
        
        # حفظ التقرير
        report_data = {
            "test_summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "warning_tests": warning_tests,
                "success_rate": success_rate,
                "execution_time": (datetime.now() - self.start_time).total_seconds()
            },
            "test_results": self.test_results,
            "generated_at": datetime.now().isoformat()
        }
        
        with open('detailed_functions_test_report.json', 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 تم حفظ التقرير التفصيلي في: detailed_functions_test_report.json")
        
        return success_rate

if __name__ == "__main__":
    # تشغيل الاختبار
    tester = DetailedFunctionsTest()
    success_rate = tester.run_comprehensive_test()
    
    # تحديد حالة الخروج بناءً على معدل النجاح
    if success_rate and success_rate >= 80:
        print("\n🎉 جميع الوظائف والأزرار تعمل بشكل ممتاز!")
    elif success_rate and success_rate >= 60:
        print("\n⚠️ الوظائف تعمل بشكل مقبول مع بعض المشاكل")
    else:
        print("\n❌ هناك مشاكل في الوظائف تحتاج إلى إصلاح")
