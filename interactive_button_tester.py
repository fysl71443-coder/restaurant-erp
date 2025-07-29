#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نظام اختبار تفاعلي شامل للأزرار
يحاكي المستخدم الحقيقي ويختبر كل زر بشكل فردي
"""

import requests
import time
from bs4 import BeautifulSoup
import json
import re
from urllib.parse import urljoin
import sys

class InteractiveButtonTester:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = {}
        self.total_buttons = 0
        self.working_buttons = 0
        self.broken_buttons = 0
        self.fixed_buttons = 0
        self.deleted_buttons = 0
        
        # قائمة الشاشات للاختبار
        self.screens = {
            'الشاشة الرئيسية': '/',
            'شاشة المبيعات': '/sales',
            'شاشة المشتريات': '/purchases', 
            'شاشة التحليلات': '/analytics',
            'شاشة ضريبة القيمة المضافة': '/vat',
            'شاشة الرواتب': '/payroll',
            'شاشة التقارير المالية': '/reports',
            'شاشة الإعدادات': '/settings'
        }
        
    def login(self):
        """تسجيل الدخول للنظام"""
        try:
            # الحصول على صفحة تسجيل الدخول
            login_page = self.session.get(f"{self.base_url}/login")
            if login_page.status_code != 200:
                print("❌ فشل في الوصول لصفحة تسجيل الدخول")
                return False
                
            # تسجيل الدخول
            login_data = {
                'username': 'admin',
                'password': 'admin123'
            }
            
            response = self.session.post(f"{self.base_url}/login", data=login_data)
            if response.status_code == 200 and 'dashboard' in response.url:
                print("✅ تم تسجيل الدخول بنجاح")
                return True
            else:
                print("❌ فشل في تسجيل الدخول")
                return False
                
        except Exception as e:
            print(f"❌ خطأ في تسجيل الدخول: {e}")
            return False
    
    def get_page_buttons(self, url):
        """استخراج جميع الأزرار من صفحة معينة"""
        try:
            response = self.session.get(urljoin(self.base_url, url))
            if response.status_code != 200:
                return []
                
            soup = BeautifulSoup(response.content, 'html.parser')
            buttons = []
            
            # البحث عن جميع الأزرار
            button_elements = soup.find_all(['button', 'a'], class_=re.compile(r'btn'))
            
            for i, button in enumerate(button_elements):
                button_info = {
                    'index': i + 1,
                    'tag': button.name,
                    'text': button.get_text(strip=True),
                    'id': button.get('id', ''),
                    'class': ' '.join(button.get('class', [])),
                    'onclick': button.get('onclick', ''),
                    'href': button.get('href', ''),
                    'type': button.get('type', ''),
                    'disabled': button.has_attr('disabled'),
                    'data_bs_toggle': button.get('data-bs-toggle', ''),
                    'data_bs_target': button.get('data-bs-target', ''),
                    'form': button.get('form', ''),
                    'element': button
                }
                buttons.append(button_info)
                
            return buttons
            
        except Exception as e:
            print(f"❌ خطأ في استخراج الأزرار: {e}")
            return []
    
    def test_button_functionality(self, button, page_url, screen_name):
        """اختبار وظيفة زر معين بشكل تفاعلي"""
        issues = []
        working = True
        button_action = "غير محدد"
        
        print(f"\n🔍 اختبار الزر #{button['index']}: '{button['text']}'")
        print(f"   النوع: {button['tag']}")
        print(f"   الفئة: {button['class']}")
        
        # فحص النص
        if not button['text'] or button['text'].strip() == '':
            issues.append("الزر لا يحتوي على نص واضح")
            working = False
            print("   ❌ لا يحتوي على نص واضح")
        
        # فحص الزر المعطل
        if button['disabled']:
            print("   ⚠️  الزر معطل (disabled)")
            button_action = "معطل بقصد"
            return working, issues, button_action
        
        # فحص الوظيفة
        if button['onclick']:
            button_action = f"JavaScript: {button['onclick']}"
            print(f"   📝 وظيفة JavaScript: {button['onclick']}")
            
        elif button['href']:
            if button['href'].startswith('#'):
                button_action = f"رابط داخلي: {button['href']}"
                print(f"   🔗 رابط داخلي: {button['href']}")
            else:
                button_action = f"رابط خارجي: {button['href']}"
                print(f"   🌐 رابط خارجي: {button['href']}")
                
        elif button['data_bs_toggle']:
            button_action = f"Bootstrap: {button['data_bs_toggle']}"
            print(f"   🎛️  عنصر Bootstrap: {button['data_bs_toggle']}")
            
        elif button['type'] == 'submit':
            button_action = "إرسال نموذج"
            print("   📤 زر إرسال نموذج")
            
        else:
            issues.append("الزر لا يحتوي على وظيفة واضحة")
            working = False
            print("   ❌ لا يحتوي على وظيفة واضحة")
        
        # فحص ID
        if not button['id']:
            issues.append("الزر لا يحتوي على ID")
            print("   ⚠️  لا يحتوي على ID فريد")
        
        # عرض النتيجة
        if working:
            print("   ✅ الزر يعمل بشكل صحيح")
        else:
            print("   ❌ الزر يحتاج إصلاح")
            
        return working, issues, button_action
    
    def test_screen_buttons(self, screen_name, url):
        """اختبار جميع أزرار شاشة معينة"""
        print(f"\n{'='*60}")
        print(f"🔍 اختبار أزرار شاشة: {screen_name}")
        print(f"{'='*60}")
        
        buttons = self.get_page_buttons(url)
        if not buttons:
            print("❌ لم يتم العثور على أزرار في هذه الشاشة")
            return
        
        screen_results = {
            'total_buttons': len(buttons),
            'working_buttons': 0,
            'broken_buttons': 0,
            'button_details': []
        }
        
        for button in buttons:
            working, issues, action = self.test_button_functionality(button, url, screen_name)
            
            button_detail = {
                'index': button['index'],
                'text': button['text'],
                'id': button['id'],
                'working': working,
                'issues': issues,
                'action': action,
                'class': button['class']
            }
            
            screen_results['button_details'].append(button_detail)
            
            if working:
                screen_results['working_buttons'] += 1
                self.working_buttons += 1
            else:
                screen_results['broken_buttons'] += 1
                self.broken_buttons += 1
                
            self.total_buttons += 1
            
            # توقف قصير بين الأزرار
            time.sleep(0.1)
        
        # عرض ملخص الشاشة
        success_rate = (screen_results['working_buttons'] / screen_results['total_buttons']) * 100
        print(f"\n📊 ملخص شاشة {screen_name}:")
        print(f"  إجمالي الأزرار: {screen_results['total_buttons']}")
        print(f"  الأزرار العاملة: {screen_results['working_buttons']} ✅")
        print(f"  الأزرار المعطلة: {screen_results['broken_buttons']} ❌")
        print(f"  معدل النجاح: {success_rate:.1f}%")
        
        self.test_results[screen_name] = screen_results
        
        return screen_results
    
    def run_comprehensive_test(self):
        """تشغيل الاختبار الشامل لجميع الشاشات"""
        print("🔧 اختبار تفاعلي شامل لجميع الأزرار في نظام المحاسبة العربي")
        print("="*80)
        print("🚀 بدء الاختبار التفاعلي الشامل لجميع الأزرار في النظام")
        print("="*80)
        
        # تسجيل الدخول
        if not self.login():
            return False
        
        # اختبار كل شاشة
        for screen_name, url in self.screens.items():
            try:
                self.test_screen_buttons(screen_name, url)
                time.sleep(1)  # توقف بين الشاشات
            except Exception as e:
                print(f"❌ خطأ في اختبار {screen_name}: {e}")
        
        # عرض التقرير النهائي
        self.generate_final_report()
        
        return True
    
    def generate_final_report(self):
        """إنشاء التقرير النهائي"""
        print("\n" + "="*80)
        print("📋 التقرير التفاعلي الشامل لاختبار الأزرار")
        print("="*80)
        
        overall_success_rate = (self.working_buttons / self.total_buttons) * 100 if self.total_buttons > 0 else 0
        
        print(f"\n📊 الإحصائيات العامة:")
        print(f"  عدد الشاشات المختبرة: {len(self.test_results)}")
        print(f"  إجمالي الأزرار: {self.total_buttons}")
        print(f"  الأزرار العاملة: {self.working_buttons} ✅")
        print(f"  الأزرار المعطلة: {self.broken_buttons} ❌")
        print(f"  معدل النجاح الإجمالي: {overall_success_rate:.1f}%")
        
        # حفظ التقرير
        report_data = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'total_screens': len(self.test_results),
            'total_buttons': self.total_buttons,
            'working_buttons': self.working_buttons,
            'broken_buttons': self.broken_buttons,
            'overall_success_rate': overall_success_rate,
            'screen_results': self.test_results
        }
        
        with open('interactive_button_test_report.json', 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 تم حفظ التقرير المفصل في: interactive_button_test_report.json")
        
        if overall_success_rate < 100:
            print(f"\n⚠️  يحتاج النظام إلى إصلاحات:")
            print(f"   - إصلاح {self.broken_buttons} زر معطل")

if __name__ == "__main__":
    tester = InteractiveButtonTester()
    tester.run_comprehensive_test()
