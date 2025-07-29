#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار شامل للتحسينات في واجهة المستخدم (UI/UX)
Test comprehensive UI/UX improvements
"""

import requests
import time
import json
from datetime import datetime
from bs4 import BeautifulSoup
import os
import sys

class UIImprovementsTest:
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
    
    def test_css_files_exist(self):
        """اختبار وجود ملفات CSS الجديدة"""
        css_files = [
            "static/css/theme.css",
            "static/css/components.css",
            "static/css/forms.css",
            "static/css/print.css"
        ]
        
        for css_file in css_files:
            try:
                if os.path.exists(css_file):
                    with open(css_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if len(content) > 100:  # التأكد من أن الملف ليس فارغاً
                            self.log_test(f"CSS File: {css_file}", "PASS", f"حجم الملف: {len(content)} حرف")
                        else:
                            self.log_test(f"CSS File: {css_file}", "FAIL", "الملف فارغ أو صغير جداً")
                else:
                    self.log_test(f"CSS File: {css_file}", "FAIL", "الملف غير موجود")
            except Exception as e:
                self.log_test(f"CSS File: {css_file}", "FAIL", f"خطأ في قراءة الملف: {str(e)}")
    
    def test_page_loads(self, page_url, page_name):
        """اختبار تحميل الصفحة والتحقق من العناصر الجديدة"""
        try:
            start_time = time.time()
            response = self.session.get(f"{self.base_url}{page_url}")
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # التحقق من وجود ملفات CSS الجديدة
                theme_css = soup.find('link', href=lambda x: x and 'theme.css' in x)
                components_css = soup.find('link', href=lambda x: x and 'components.css' in x)
                
                # التحقق من وجود العناصر الجديدة
                stats_cards = soup.find_all(class_='stats-card')
                data_tables = soup.find_all(class_='data-table')
                quick_actions = soup.find_all(class_='quick-actions')
                
                details = []
                if theme_css:
                    details.append("✅ theme.css محمل")
                else:
                    details.append("❌ theme.css غير محمل")
                    
                if components_css:
                    details.append("✅ components.css محمل")
                else:
                    details.append("❌ components.css غير محمل")
                
                details.append(f"📊 بطاقات الإحصائيات: {len(stats_cards)}")
                details.append(f"📋 جداول البيانات: {len(data_tables)}")
                details.append(f"⚡ الإجراءات السريعة: {len(quick_actions)}")
                
                # التحقق من الخط العربي
                cairo_font = soup.find('link', href=lambda x: x and 'Cairo' in x if x else False)
                if cairo_font:
                    details.append("✅ خط Cairo محمل")
                else:
                    details.append("❌ خط Cairo غير محمل")
                
                self.log_test(f"صفحة {page_name}", "PASS", " | ".join(details), response_time)
                return True
            else:
                self.log_test(f"صفحة {page_name}", "FAIL", f"HTTP {response.status_code}", response_time)
                return False
                
        except Exception as e:
            self.log_test(f"صفحة {page_name}", "FAIL", f"خطأ: {str(e)}")
            return False
    
    def test_responsive_design(self, page_url, page_name):
        """اختبار التصميم المتجاوب"""
        try:
            response = self.session.get(f"{self.base_url}{page_url}")
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # التحقق من وجود Bootstrap classes للتصميم المتجاوب
                responsive_elements = []
                
                # البحث عن col-lg, col-md, col-sm classes
                for class_name in ['col-lg-', 'col-md-', 'col-sm-']:
                    elements = soup.find_all(class_=lambda x: x and class_name in str(x))
                    responsive_elements.extend(elements)
                
                # التحقق من وجود container-fluid
                container_fluid = soup.find_all(class_='container-fluid')
                
                details = [
                    f"عناصر متجاوبة: {len(responsive_elements)}",
                    f"حاويات مرنة: {len(container_fluid)}"
                ]
                
                if len(responsive_elements) > 0 and len(container_fluid) > 0:
                    self.log_test(f"التصميم المتجاوب - {page_name}", "PASS", " | ".join(details))
                    return True
                else:
                    self.log_test(f"التصميم المتجاوب - {page_name}", "FAIL", " | ".join(details))
                    return False
            else:
                self.log_test(f"التصميم المتجاوب - {page_name}", "FAIL", f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test(f"التصميم المتجاوب - {page_name}", "FAIL", f"خطأ: {str(e)}")
            return False
    
    def test_interactive_elements(self, page_url, page_name):
        """اختبار العناصر التفاعلية"""
        try:
            response = self.session.get(f"{self.base_url}{page_url}")
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # التحقق من وجود الأزرار التفاعلية
                buttons = soup.find_all('button')
                links = soup.find_all('a', class_=lambda x: x and 'btn' in str(x))
                
                # التحقق من وجود JavaScript للتفاعل
                scripts = soup.find_all('script')
                has_js_functions = False
                for script in scripts:
                    if script.string and ('function' in script.string or 'onclick' in str(soup)):
                        has_js_functions = True
                        break
                
                # التحقق من وجود أيقونات Font Awesome
                fa_icons = soup.find_all('i', class_=lambda x: x and 'fas' in str(x))
                
                details = [
                    f"أزرار: {len(buttons)}",
                    f"روابط تفاعلية: {len(links)}",
                    f"أيقونات: {len(fa_icons)}",
                    f"JavaScript: {'✅' if has_js_functions else '❌'}"
                ]
                
                if len(buttons) > 0 or len(links) > 0:
                    self.log_test(f"العناصر التفاعلية - {page_name}", "PASS", " | ".join(details))
                    return True
                else:
                    self.log_test(f"العناصر التفاعلية - {page_name}", "FAIL", " | ".join(details))
                    return False
                    
        except Exception as e:
            self.log_test(f"العناصر التفاعلية - {page_name}", "FAIL", f"خطأ: {str(e)}")
            return False
    
    def run_comprehensive_test(self):
        """تشغيل الاختبار الشامل"""
        print("🚀 بدء اختبار التحسينات في واجهة المستخدم...")
        print("=" * 60)
        
        # اختبار وجود ملفات CSS
        print("\n📁 اختبار ملفات CSS:")
        self.test_css_files_exist()
        
        # قائمة الصفحات للاختبار
        pages_to_test = [
            ("/", "الصفحة الرئيسية"),
            ("/sales", "المبيعات"),
            ("/purchases", "المشتريات"),
            ("/inventory", "المخزون"),
            ("/customers", "العملاء"),
            ("/employees", "الموظفين"),
            ("/reports", "التقارير")
        ]
        
        # اختبار تحميل الصفحات
        print("\n🌐 اختبار تحميل الصفحات:")
        for page_url, page_name in pages_to_test:
            self.test_page_loads(page_url, page_name)
            time.sleep(0.5)  # توقف قصير بين الاختبارات
        
        # اختبار التصميم المتجاوب
        print("\n📱 اختبار التصميم المتجاوب:")
        for page_url, page_name in pages_to_test:
            self.test_responsive_design(page_url, page_name)
            time.sleep(0.5)
        
        # اختبار العناصر التفاعلية
        print("\n🎯 اختبار العناصر التفاعلية:")
        for page_url, page_name in pages_to_test:
            self.test_interactive_elements(page_url, page_name)
            time.sleep(0.5)
        
        # إنشاء التقرير النهائي
        self.generate_report()
    
    def generate_report(self):
        """إنشاء تقرير شامل للنتائج"""
        total_tests = len(self.test_results)
        passed_tests = len([t for t in self.test_results if t['status'] == 'PASS'])
        failed_tests = len([t for t in self.test_results if t['status'] == 'FAIL'])
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print("\n" + "=" * 60)
        print("📊 تقرير نتائج اختبار التحسينات")
        print("=" * 60)
        print(f"📈 إجمالي الاختبارات: {total_tests}")
        print(f"✅ اختبارات ناجحة: {passed_tests}")
        print(f"❌ اختبارات فاشلة: {failed_tests}")
        print(f"🎯 معدل النجاح: {success_rate:.1f}%")
        print(f"⏱️ وقت التنفيذ: {(datetime.now() - self.start_time).total_seconds():.2f} ثانية")
        
        # حفظ التقرير في ملف JSON
        report_data = {
            "test_summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "success_rate": success_rate,
                "execution_time": (datetime.now() - self.start_time).total_seconds()
            },
            "test_results": self.test_results,
            "generated_at": datetime.now().isoformat()
        }
        
        with open('ui_improvements_test_report.json', 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 تم حفظ التقرير التفصيلي في: ui_improvements_test_report.json")
        
        return success_rate

if __name__ == "__main__":
    # تشغيل الاختبار
    tester = UIImprovementsTest()
    success_rate = tester.run_comprehensive_test()
    
    # تحديد حالة الخروج بناءً على معدل النجاح
    if success_rate >= 90:
        print("\n🎉 جميع التحسينات تعمل بشكل ممتاز!")
        sys.exit(0)
    elif success_rate >= 70:
        print("\n⚠️ معظم التحسينات تعمل بشكل جيد مع بعض المشاكل البسيطة")
        sys.exit(1)
    else:
        print("\n❌ هناك مشاكل كبيرة تحتاج إلى إصلاح")
        sys.exit(2)
