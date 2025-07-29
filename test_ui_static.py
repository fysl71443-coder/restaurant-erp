#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار ثابت للتحسينات في واجهة المستخدم (UI/UX) - بدون خادم
Static UI/UX improvements test - without server
"""

import os
import json
from datetime import datetime
from bs4 import BeautifulSoup
import re

class StaticUITest:
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
    
    def test_css_files(self):
        """اختبار ملفات CSS الجديدة"""
        print("\n📁 اختبار ملفات CSS:")
        
        css_files = {
            "static/css/theme.css": "نظام الألوان والخطوط",
            "static/css/components.css": "مكونات واجهة المستخدم",
            "static/css/forms.css": "تنسيق النماذج",
            "static/css/print.css": "تنسيق الطباعة"
        }
        
        for css_file, description in css_files.items():
            try:
                if os.path.exists(css_file):
                    with open(css_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    # تحليل محتوى CSS
                    lines = len(content.split('\n'))
                    css_rules = len(re.findall(r'\{[^}]*\}', content))
                    css_variables = len(re.findall(r'--[\w-]+:', content))
                    
                    if lines > 50:  # ملف كبير بما فيه الكفاية
                        details = f"{description} - {lines} سطر، {css_rules} قاعدة، {css_variables} متغير"
                        self.log_test(f"CSS: {os.path.basename(css_file)}", "PASS", details)
                    else:
                        self.log_test(f"CSS: {os.path.basename(css_file)}", "FAIL", f"الملف صغير جداً ({lines} سطر)")
                else:
                    self.log_test(f"CSS: {os.path.basename(css_file)}", "FAIL", "الملف غير موجود")
            except Exception as e:
                self.log_test(f"CSS: {os.path.basename(css_file)}", "FAIL", f"خطأ: {str(e)}")
    
    def test_template_improvements(self):
        """اختبار تحسينات القوالب"""
        print("\n🎨 اختبار تحسينات القوالب:")
        
        templates_to_test = {
            "templates/base.html": "القالب الأساسي",
            "templates/index.html": "الصفحة الرئيسية",
            "templates/sales.html": "صفحة المبيعات",
            "templates/purchases.html": "صفحة المشتريات",
            "templates/inventory.html": "صفحة المخزون",
            "templates/customers.html": "صفحة العملاء",
            "templates/employees.html": "صفحة الموظفين",
            "templates/reports.html": "صفحة التقارير"
        }
        
        for template_file, description in templates_to_test.items():
            try:
                if os.path.exists(template_file):
                    with open(template_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    soup = BeautifulSoup(content, 'html.parser')
                    
                    # البحث عن العناصر الجديدة
                    stats_cards = len(soup.find_all(class_='stats-card'))
                    data_tables = len(soup.find_all(class_='data-table'))
                    quick_actions = len(soup.find_all(class_='quick-actions'))
                    
                    # البحث عن ملفات CSS الجديدة
                    theme_css = bool(soup.find('link', href=lambda x: x and 'theme.css' in x if x else False))
                    components_css = bool(soup.find('link', href=lambda x: x and 'components.css' in x if x else False))
                    
                    # البحث عن خط Cairo
                    cairo_font = bool(soup.find('link', href=lambda x: x and 'Cairo' in x if x else False))
                    
                    # البحث عن أيقونات Font Awesome
                    fa_icons = len(soup.find_all('i', class_=lambda x: x and 'fas' in str(x) if x else False))
                    
                    improvements = []
                    if stats_cards > 0:
                        improvements.append(f"بطاقات إحصائيات: {stats_cards}")
                    if data_tables > 0:
                        improvements.append(f"جداول بيانات: {data_tables}")
                    if quick_actions > 0:
                        improvements.append(f"إجراءات سريعة: {quick_actions}")
                    if theme_css:
                        improvements.append("theme.css ✅")
                    if components_css:
                        improvements.append("components.css ✅")
                    if cairo_font:
                        improvements.append("خط Cairo ✅")
                    if fa_icons > 0:
                        improvements.append(f"أيقونات: {fa_icons}")
                    
                    if len(improvements) > 0:
                        details = " | ".join(improvements)
                        self.log_test(f"قالب: {os.path.basename(template_file)}", "PASS", details)
                    else:
                        self.log_test(f"قالب: {os.path.basename(template_file)}", "FAIL", "لا توجد تحسينات مرئية")
                        
                else:
                    self.log_test(f"قالب: {os.path.basename(template_file)}", "FAIL", "الملف غير موجود")
                    
            except Exception as e:
                self.log_test(f"قالب: {os.path.basename(template_file)}", "FAIL", f"خطأ: {str(e)}")
    
    def test_responsive_design(self):
        """اختبار التصميم المتجاوب"""
        print("\n📱 اختبار التصميم المتجاوب:")
        
        templates = [
            "templates/index.html",
            "templates/sales.html", 
            "templates/purchases.html",
            "templates/inventory.html"
        ]
        
        for template_file in templates:
            try:
                if os.path.exists(template_file):
                    with open(template_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # البحث عن Bootstrap responsive classes
                    responsive_classes = [
                        'col-lg-', 'col-md-', 'col-sm-',
                        'container-fluid', 'd-flex', 'justify-content-',
                        'align-items-', 'mb-4', 'row'
                    ]
                    
                    found_classes = []
                    for cls in responsive_classes:
                        if cls in content:
                            count = content.count(cls)
                            found_classes.append(f"{cls}({count})")
                    
                    if len(found_classes) >= 4:  # على الأقل 4 أنواع من الـ classes المتجاوبة
                        details = " | ".join(found_classes[:6])  # أول 6 فقط
                        self.log_test(f"متجاوب: {os.path.basename(template_file)}", "PASS", details)
                    else:
                        self.log_test(f"متجاوب: {os.path.basename(template_file)}", "FAIL", f"classes قليلة: {len(found_classes)}")
                        
                else:
                    self.log_test(f"متجاوب: {os.path.basename(template_file)}", "FAIL", "الملف غير موجود")
                    
            except Exception as e:
                self.log_test(f"متجاوب: {os.path.basename(template_file)}", "FAIL", f"خطأ: {str(e)}")
    
    def test_arabic_support(self):
        """اختبار دعم اللغة العربية"""
        print("\n🔤 اختبار دعم اللغة العربية:")
        
        # اختبار القالب الأساسي
        try:
            if os.path.exists("templates/base.html"):
                with open("templates/base.html", 'r', encoding='utf-8') as f:
                    content = f.read()
                
                soup = BeautifulSoup(content, 'html.parser')
                
                # البحث عن خط Cairo
                cairo_font = bool(soup.find('link', href=lambda x: x and 'Cairo' in x if x else False))
                
                # البحث عن RTL support
                rtl_support = 'dir="rtl"' in content or 'lang="ar"' in content
                
                # البحث عن Bootstrap RTL
                bootstrap_rtl = 'bootstrap.rtl' in content or 'rtl' in content
                
                features = []
                if cairo_font:
                    features.append("خط Cairo ✅")
                if rtl_support:
                    features.append("RTL ✅")
                if bootstrap_rtl:
                    features.append("Bootstrap RTL ✅")
                
                if len(features) >= 2:
                    details = " | ".join(features)
                    self.log_test("دعم العربية", "PASS", details)
                else:
                    self.log_test("دعم العربية", "FAIL", f"ميزات قليلة: {len(features)}")
                    
            else:
                self.log_test("دعم العربية", "FAIL", "base.html غير موجود")
                
        except Exception as e:
            self.log_test("دعم العربية", "FAIL", f"خطأ: {str(e)}")
    
    def test_javascript_enhancements(self):
        """اختبار تحسينات JavaScript"""
        print("\n⚡ اختبار تحسينات JavaScript:")
        
        templates = [
            "templates/base.html",
            "templates/reports.html"
        ]
        
        for template_file in templates:
            try:
                if os.path.exists(template_file):
                    with open(template_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # البحث عن JavaScript functions
                    js_functions = re.findall(r'function\s+(\w+)', content)
                    js_classes = re.findall(r'class\s+(\w+)', content)
                    event_listeners = content.count('addEventListener') + content.count('onclick')
                    
                    features = []
                    if js_functions:
                        features.append(f"وظائف: {len(js_functions)}")
                    if js_classes:
                        features.append(f"classes: {len(js_classes)}")
                    if event_listeners > 0:
                        features.append(f"أحداث: {event_listeners}")
                    
                    if len(features) > 0:
                        details = " | ".join(features)
                        self.log_test(f"JS: {os.path.basename(template_file)}", "PASS", details)
                    else:
                        self.log_test(f"JS: {os.path.basename(template_file)}", "WARN", "لا توجد تحسينات JS")
                        
                else:
                    self.log_test(f"JS: {os.path.basename(template_file)}", "FAIL", "الملف غير موجود")
                    
            except Exception as e:
                self.log_test(f"JS: {os.path.basename(template_file)}", "FAIL", f"خطأ: {str(e)}")
    
    def run_comprehensive_test(self):
        """تشغيل الاختبار الشامل"""
        print("🚀 بدء اختبار التحسينات الثابت...")
        print("=" * 60)
        
        # تشغيل جميع الاختبارات
        self.test_css_files()
        self.test_template_improvements()
        self.test_responsive_design()
        self.test_arabic_support()
        self.test_javascript_enhancements()
        
        # إنشاء التقرير النهائي
        self.generate_report()
    
    def generate_report(self):
        """إنشاء تقرير شامل للنتائج"""
        total_tests = len(self.test_results)
        passed_tests = len([t for t in self.test_results if t['status'] == 'PASS'])
        failed_tests = len([t for t in self.test_results if t['status'] == 'FAIL'])
        warning_tests = len([t for t in self.test_results if t['status'] == 'WARN'])
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print("\n" + "=" * 60)
        print("📊 تقرير نتائج اختبار التحسينات الثابت")
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
        
        with open('static_ui_test_report.json', 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 تم حفظ التقرير في: static_ui_test_report.json")
        
        return success_rate

if __name__ == "__main__":
    # تشغيل الاختبار
    tester = StaticUITest()
    success_rate = tester.run_comprehensive_test()
    
    # تحديد النتيجة النهائية
    if success_rate and success_rate >= 90:
        print("\n🎉 جميع التحسينات تعمل بشكل ممتاز!")
    elif success_rate and success_rate >= 70:
        print("\n⚠️ معظم التحسينات تعمل بشكل جيد مع بعض المشاكل البسيطة")
    else:
        print("\n❌ هناك مشاكل تحتاج إلى إصلاح")
