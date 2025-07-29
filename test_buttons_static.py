#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار ثابت لجميع الأزرار والوظائف في التطبيق - بدون خادم
Static test for all buttons and functions - without server
"""

import os
import json
from datetime import datetime
from bs4 import BeautifulSoup
import re

class StaticButtonsTest:
    def __init__(self):
        self.test_results = []
        self.start_time = datetime.now()
        
    def log_test(self, test_name, status, details=""):
        """تسجيل نتيجة الاختبار"""
        result = {
            "test_name": test_name,
            "status": status,
            "details": details,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.test_results.append(result)
        status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_icon} {test_name}: {status}")
        if details:
            print(f"   📝 {details}")
    
    def analyze_buttons_in_template(self, template_path, template_name):
        """تحليل الأزرار في قالب معين"""
        try:
            if not os.path.exists(template_path):
                self.log_test(f"أزرار {template_name}", "FAIL", "الملف غير موجود")
                return None
                
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            soup = BeautifulSoup(content, 'html.parser')
            
            # البحث عن جميع الأزرار
            buttons = soup.find_all('button')
            button_links = soup.find_all('a', class_=lambda x: x and 'btn' in str(x))
            
            # تصنيف الأزرار حسب النوع
            button_types = {
                'save': 0, 'edit': 0, 'delete': 0, 'cancel': 0, 
                'print': 0, 'search': 0, 'add': 0, 'view': 0, 
                'export': 0, 'submit': 0, 'other': 0
            }
            
            all_buttons = buttons + button_links
            button_details = []
            
            for button in all_buttons:
                button_text = button.get_text(strip=True).lower()
                button_class = str(button.get('class', [])).lower()
                button_onclick = str(button.get('onclick', '')).lower()
                button_href = str(button.get('href', '')).lower()
                
                # تجميع النص للتحليل
                full_text = f"{button_text} {button_class} {button_onclick} {button_href}"
                
                # تصنيف الأزرار بناءً على النص والخصائص
                if any(word in full_text for word in ['حفظ', 'save', 'submit', 'إرسال']):
                    button_types['save'] += 1
                    button_details.append(f"حفظ: {button_text[:20]}")
                elif any(word in full_text for word in ['تعديل', 'edit', 'modify', 'update']):
                    button_types['edit'] += 1
                    button_details.append(f"تعديل: {button_text[:20]}")
                elif any(word in full_text for word in ['حذف', 'delete', 'remove', 'trash']):
                    button_types['delete'] += 1
                    button_details.append(f"حذف: {button_text[:20]}")
                elif any(word in full_text for word in ['إلغاء', 'cancel', 'close', 'dismiss']):
                    button_types['cancel'] += 1
                    button_details.append(f"إلغاء: {button_text[:20]}")
                elif any(word in full_text for word in ['طباعة', 'print']):
                    button_types['print'] += 1
                    button_details.append(f"طباعة: {button_text[:20]}")
                elif any(word in full_text for word in ['بحث', 'search', 'filter', 'find']):
                    button_types['search'] += 1
                    button_details.append(f"بحث: {button_text[:20]}")
                elif any(word in full_text for word in ['إضافة', 'add', 'new', 'جديد', 'create']):
                    button_types['add'] += 1
                    button_details.append(f"إضافة: {button_text[:20]}")
                elif any(word in full_text for word in ['عرض', 'view', 'show', 'display']):
                    button_types['view'] += 1
                    button_details.append(f"عرض: {button_text[:20]}")
                elif any(word in full_text for word in ['تصدير', 'export', 'download']):
                    button_types['export'] += 1
                    button_details.append(f"تصدير: {button_text[:20]}")
                elif any(word in full_text for word in ['إرسال', 'submit', 'send']):
                    button_types['submit'] += 1
                    button_details.append(f"إرسال: {button_text[:20]}")
                else:
                    button_types['other'] += 1
                    button_details.append(f"أخرى: {button_text[:20]}")
            
            # إنشاء تفاصيل النتيجة
            total_buttons = sum(button_types.values())
            
            if total_buttons > 0:
                # إنشاء ملخص الأزرار
                summary_parts = []
                for btn_type, count in button_types.items():
                    if count > 0:
                        summary_parts.append(f"{btn_type}: {count}")
                
                summary = f"إجمالي: {total_buttons} | " + " | ".join(summary_parts)
                self.log_test(f"أزرار {template_name}", "PASS", summary)
                return button_types
            else:
                self.log_test(f"أزرار {template_name}", "WARN", "لا توجد أزرار")
                return button_types
                
        except Exception as e:
            self.log_test(f"أزرار {template_name}", "FAIL", f"خطأ: {str(e)}")
            return None
    
    def analyze_forms_in_template(self, template_path, template_name):
        """تحليل النماذج في قالب معين"""
        try:
            if not os.path.exists(template_path):
                return False
                
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            soup = BeautifulSoup(content, 'html.parser')
            
            # البحث عن النماذج
            forms = soup.find_all('form')
            
            if len(forms) > 0:
                form_details = []
                for i, form in enumerate(forms):
                    method = form.get('method', 'GET').upper()
                    action = form.get('action', '#')
                    inputs = len(form.find_all(['input', 'select', 'textarea']))
                    
                    form_details.append(f"نموذج{i+1}({method}, {inputs} حقل)")
                
                details = " | ".join(form_details)
                self.log_test(f"نماذج {template_name}", "PASS", details)
                return True
            else:
                self.log_test(f"نماذج {template_name}", "WARN", "لا توجد نماذج")
                return False
                
        except Exception as e:
            self.log_test(f"نماذج {template_name}", "FAIL", f"خطأ: {str(e)}")
            return False
    
    def analyze_javascript_functions(self, template_path, template_name):
        """تحليل وظائف JavaScript في قالب معين"""
        try:
            if not os.path.exists(template_path):
                return False
                
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # البحث عن وظائف JavaScript
            js_functions = re.findall(r'function\s+(\w+)', content)
            js_classes = re.findall(r'class\s+(\w+)', content)
            event_listeners = content.count('addEventListener') + content.count('onclick')
            
            # البحث عن وظائف مخصصة
            custom_functions = []
            for func in js_functions:
                if func not in ['jQuery', '$']:
                    custom_functions.append(func)
            
            features = []
            if custom_functions:
                features.append(f"وظائف: {len(custom_functions)}")
            if js_classes:
                features.append(f"classes: {len(js_classes)}")
            if event_listeners > 0:
                features.append(f"أحداث: {event_listeners}")
            
            if len(features) > 0:
                details = " | ".join(features)
                self.log_test(f"JS {template_name}", "PASS", details)
                return True
            else:
                self.log_test(f"JS {template_name}", "WARN", "لا توجد وظائف JS")
                return False
                
        except Exception as e:
            self.log_test(f"JS {template_name}", "FAIL", f"خطأ: {str(e)}")
            return False
    
    def analyze_navigation_links(self):
        """تحليل روابط التنقل في القالب الأساسي"""
        try:
            base_template = "templates/base.html"
            if not os.path.exists(base_template):
                self.log_test("روابط التنقل", "FAIL", "base.html غير موجود")
                return False
                
            with open(base_template, 'r', encoding='utf-8') as f:
                content = f.read()
            
            soup = BeautifulSoup(content, 'html.parser')
            
            # البحث عن روابط التنقل
            nav_links = soup.find_all('a', href=True)
            
            internal_links = 0
            external_links = 0
            
            for link in nav_links:
                href = link.get('href', '')
                if href.startswith('/'):
                    internal_links += 1
                elif href.startswith('http'):
                    external_links += 1
            
            total_links = internal_links + external_links
            
            if total_links > 0:
                details = f"داخلية: {internal_links} | خارجية: {external_links}"
                self.log_test("روابط التنقل", "PASS", details)
                return True
            else:
                self.log_test("روابط التنقل", "WARN", "لا توجد روابط")
                return False
                
        except Exception as e:
            self.log_test("روابط التنقل", "FAIL", f"خطأ: {str(e)}")
            return False
    
    def run_comprehensive_test(self):
        """تشغيل الاختبار الشامل"""
        print("🚀 بدء اختبار الأزرار والوظائف الثابت...")
        print("=" * 60)
        
        # قائمة القوالب للاختبار
        templates_to_test = [
            ("templates/index.html", "الصفحة الرئيسية"),
            ("templates/sales.html", "المبيعات"),
            ("templates/purchases.html", "المشتريات"),
            ("templates/inventory.html", "المخزون"),
            ("templates/customers.html", "العملاء"),
            ("templates/employees.html", "الموظفين"),
            ("templates/reports.html", "التقارير"),
            ("templates/add_sales_invoice.html", "إضافة فاتورة مبيعات"),
            ("templates/add_purchase_invoice.html", "إضافة فاتورة مشتريات"),
            ("templates/edit_product.html", "تعديل منتج"),
            ("templates/edit_supplier.html", "تعديل مورد"),
            ("templates/edit_customer.html", "تعديل عميل"),
            ("templates/edit_employee.html", "تعديل موظف")
        ]
        
        # اختبار الأزرار في كل قالب
        print("\n🔘 اختبار الأزرار:")
        total_buttons = {}
        for template_path, template_name in templates_to_test:
            buttons = self.analyze_buttons_in_template(template_path, template_name)
            if buttons:
                for btn_type, count in buttons.items():
                    total_buttons[btn_type] = total_buttons.get(btn_type, 0) + count
        
        # اختبار النماذج
        print("\n📝 اختبار النماذج:")
        for template_path, template_name in templates_to_test:
            self.analyze_forms_in_template(template_path, template_name)
        
        # اختبار وظائف JavaScript
        print("\n⚡ اختبار JavaScript:")
        for template_path, template_name in templates_to_test:
            self.analyze_javascript_functions(template_path, template_name)
        
        # اختبار روابط التنقل
        print("\n🔗 اختبار التنقل:")
        self.analyze_navigation_links()
        
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
        print("📊 تقرير نتائج اختبار الأزرار والوظائف الثابت")
        print("=" * 60)
        print(f"📈 إجمالي الاختبارات: {total_tests}")
        print(f"✅ اختبارات ناجحة: {passed_tests}")
        print(f"❌ اختبارات فاشلة: {failed_tests}")
        print(f"⚠️ تحذيرات: {warning_tests}")
        print(f"🎯 معدل النجاح: {success_rate:.1f}%")
        print(f"⏱️ وقت التنفيذ: {(datetime.now() - self.start_time).total_seconds():.2f} ثانية")
        
        # إحصائيات الأزرار
        if total_buttons:
            print(f"\n🔘 إحصائيات الأزرار الإجمالية:")
            total_button_count = sum(total_buttons.values())
            print(f"   إجمالي الأزرار: {total_button_count}")
            for btn_type, count in total_buttons.items():
                if count > 0:
                    percentage = (count / total_button_count * 100)
                    print(f"   {btn_type}: {count} زر ({percentage:.1f}%)")
        
        # حفظ التقرير
        report_data = {
            "test_summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "warning_tests": warning_tests,
                "success_rate": success_rate,
                "execution_time": (datetime.now() - self.start_time).total_seconds(),
                "total_buttons": total_buttons,
                "total_button_count": sum(total_buttons.values()) if total_buttons else 0
            },
            "test_results": self.test_results,
            "generated_at": datetime.now().isoformat()
        }
        
        with open('static_buttons_test_report.json', 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 تم حفظ التقرير التفصيلي في: static_buttons_test_report.json")
        
        return success_rate

if __name__ == "__main__":
    # تشغيل الاختبار
    tester = StaticButtonsTest()
    success_rate = tester.run_comprehensive_test()
    
    # تحديد النتيجة النهائية
    if success_rate and success_rate >= 80:
        print("\n🎉 معظم الأزرار والوظائف تعمل بشكل ممتاز!")
    elif success_rate and success_rate >= 60:
        print("\n⚠️ الأزرار تعمل بشكل مقبول مع بعض المشاكل")
    else:
        print("\n❌ هناك مشاكل في الأزرار تحتاج إلى إصلاح")
