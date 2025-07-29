#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار شامل لجميع الأزرار في نظام المحاسبة العربي
Comprehensive Button Testing for Arabic Accounting System
"""

import requests
from bs4 import BeautifulSoup
import time
import json
from datetime import datetime

class ButtonTester:
    def __init__(self):
        self.base_url = "http://127.0.0.1:5000"
        self.session = requests.Session()
        self.test_results = {
            "total_buttons": 0,
            "working_buttons": 0,
            "broken_buttons": 0,
            "redundant_buttons": 0,
            "screens_tested": 0,
            "detailed_results": {},
            "issues_found": [],
            "recommendations": []
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
            if response.status_code == 200 and "لوحة التحكم" in response.text:
                print("✅ تم تسجيل الدخول بنجاح")
                return True
            else:
                print("❌ فشل في تسجيل الدخول")
                return False
                
        except Exception as e:
            print(f"❌ خطأ في تسجيل الدخول: {str(e)}")
            return False
    
    def extract_buttons_from_page(self, url, page_name):
        """استخراج جميع الأزرار من صفحة معينة"""
        try:
            response = self.session.get(url)
            if response.status_code != 200:
                return []
                
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # البحث عن جميع أنواع الأزرار
            buttons = []
            
            # أزرار button
            for btn in soup.find_all('button'):
                button_info = {
                    'type': 'button',
                    'text': btn.get_text(strip=True),
                    'id': btn.get('id', ''),
                    'class': btn.get('class', []),
                    'onclick': btn.get('onclick', ''),
                    'data_attributes': {k: v for k, v in btn.attrs.items() if k.startswith('data-')},
                    'disabled': btn.get('disabled', False),
                    'form': btn.get('form', ''),
                    'page': page_name
                }
                buttons.append(button_info)
            
            # أزرار input type="button/submit"
            for inp in soup.find_all('input', type=['button', 'submit']):
                button_info = {
                    'type': 'input',
                    'text': inp.get('value', ''),
                    'id': inp.get('id', ''),
                    'class': inp.get('class', []),
                    'onclick': inp.get('onclick', ''),
                    'data_attributes': {k: v for k, v in inp.attrs.items() if k.startswith('data-')},
                    'disabled': inp.get('disabled', False),
                    'form': inp.get('form', ''),
                    'page': page_name
                }
                buttons.append(button_info)
            
            # روابط تعمل كأزرار
            for link in soup.find_all('a', class_=lambda x: x and ('btn' in ' '.join(x) if isinstance(x, list) else 'btn' in x)):
                button_info = {
                    'type': 'link',
                    'text': link.get_text(strip=True),
                    'id': link.get('id', ''),
                    'class': link.get('class', []),
                    'href': link.get('href', ''),
                    'onclick': link.get('onclick', ''),
                    'data_attributes': {k: v for k, v in link.attrs.items() if k.startswith('data-')},
                    'page': page_name
                }
                buttons.append(button_info)
                
            return buttons
            
        except Exception as e:
            print(f"❌ خطأ في استخراج الأزرار من {page_name}: {str(e)}")
            return []
    
    def test_button_functionality(self, button, page_url):
        """اختبار وظيفة زر معين"""
        issues = []
        working = True
        
        try:
            # فحص النص
            if not button['text'] or button['text'].strip() == '':
                issues.append("الزر لا يحتوي على نص واضح")
                working = False
            
            # فحص الـ ID
            if not button['id']:
                issues.append("الزر لا يحتوي على ID")
            
            # فحص الوظيفة
            if button['type'] == 'link':
                if not button['href'] or button['href'] == '#':
                    if not button['onclick'] and not button['data_attributes']:
                        issues.append("الرابط لا يحتوي على وجهة أو وظيفة")
                        working = False
            
            elif button['type'] in ['button', 'input']:
                if not button['onclick'] and not button['data_attributes'] and not button['form']:
                    issues.append("الزر لا يحتوي على وظيفة واضحة")
                    working = False
            
            # فحص التعطيل
            if button.get('disabled'):
                issues.append("الزر معطل")
                working = False
            
            # فحص التكرار
            button_signature = f"{button['text']}_{button['id']}_{button.get('onclick', '')}"
            
            return {
                'working': working,
                'issues': issues,
                'signature': button_signature
            }
            
        except Exception as e:
            return {
                'working': False,
                'issues': [f"خطأ في الاختبار: {str(e)}"],
                'signature': ''
            }
    
    def test_screen_buttons(self, url, screen_name):
        """اختبار جميع أزرار شاشة معينة"""
        print(f"\n🔍 اختبار أزرار شاشة: {screen_name}")
        print("=" * 50)
        
        buttons = self.extract_buttons_from_page(url, screen_name)
        screen_results = {
            'total_buttons': len(buttons),
            'working_buttons': 0,
            'broken_buttons': 0,
            'redundant_buttons': 0,
            'button_details': [],
            'issues': [],
            'recommendations': []
        }
        
        button_signatures = {}
        
        for i, button in enumerate(buttons, 1):
            print(f"  {i}. اختبار الزر: '{button['text']}'")
            
            test_result = self.test_button_functionality(button, url)
            
            # فحص التكرار
            signature = test_result['signature']
            if signature in button_signatures:
                screen_results['redundant_buttons'] += 1
                test_result['issues'].append("زر مكرر")
                button_signatures[signature] += 1
            else:
                button_signatures[signature] = 1
            
            button_detail = {
                'button': button,
                'test_result': test_result,
                'status': '✅ يعمل' if test_result['working'] else '❌ لا يعمل'
            }
            
            screen_results['button_details'].append(button_detail)
            
            if test_result['working']:
                screen_results['working_buttons'] += 1
                print(f"    ✅ يعمل بشكل صحيح")
            else:
                screen_results['broken_buttons'] += 1
                print(f"    ❌ لا يعمل - المشاكل: {', '.join(test_result['issues'])}")
                screen_results['issues'].extend(test_result['issues'])
        
        # إضافة توصيات
        if screen_results['redundant_buttons'] > 0:
            screen_results['recommendations'].append(f"حذف {screen_results['redundant_buttons']} زر مكرر")
        
        if screen_results['broken_buttons'] > 0:
            screen_results['recommendations'].append(f"إصلاح {screen_results['broken_buttons']} زر لا يعمل")
        
        # طباعة ملخص الشاشة
        print(f"\n📊 ملخص شاشة {screen_name}:")
        print(f"  إجمالي الأزرار: {screen_results['total_buttons']}")
        print(f"  الأزرار العاملة: {screen_results['working_buttons']} ✅")
        print(f"  الأزرار المعطلة: {screen_results['broken_buttons']} ❌")
        print(f"  الأزرار المكررة: {screen_results['redundant_buttons']} 🔄")
        
        success_rate = (screen_results['working_buttons'] / screen_results['total_buttons'] * 100) if screen_results['total_buttons'] > 0 else 0
        print(f"  معدل النجاح: {success_rate:.1f}%")
        
        return screen_results
    
    def run_comprehensive_test(self):
        """تشغيل اختبار شامل لجميع الشاشات"""
        print("🚀 بدء الاختبار الشامل لجميع الأزرار في النظام")
        print("=" * 60)
        
        # تسجيل الدخول
        if not self.login():
            return False
        
        # قائمة الشاشات للاختبار
        screens = [
            ("/", "الشاشة الرئيسية"),
            ("/sales", "شاشة المبيعات"),
            ("/purchases", "شاشة المشتريات"),
            ("/analytics", "شاشة التحليلات"),
            ("/vat", "شاشة ضريبة القيمة المضافة"),
            ("/payroll", "شاشة الرواتب"),
            ("/reports", "شاشة التقارير المالية"),
            ("/settings", "شاشة الإعدادات")
        ]
        
        # اختبار كل شاشة
        for url_path, screen_name in screens:
            full_url = f"{self.base_url}{url_path}"
            screen_result = self.test_screen_buttons(full_url, screen_name)
            
            self.test_results['detailed_results'][screen_name] = screen_result
            self.test_results['total_buttons'] += screen_result['total_buttons']
            self.test_results['working_buttons'] += screen_result['working_buttons']
            self.test_results['broken_buttons'] += screen_result['broken_buttons']
            self.test_results['redundant_buttons'] += screen_result['redundant_buttons']
            self.test_results['screens_tested'] += 1
            
            self.test_results['issues_found'].extend(screen_result['issues'])
            self.test_results['recommendations'].extend(screen_result['recommendations'])
        
        return True
    
    def generate_report(self):
        """إنشاء تقرير شامل"""
        print("\n" + "=" * 60)
        print("📋 التقرير الشامل لاختبار الأزرار")
        print("=" * 60)
        
        print(f"\n📊 الإحصائيات العامة:")
        print(f"  عدد الشاشات المختبرة: {self.test_results['screens_tested']}")
        print(f"  إجمالي الأزرار: {self.test_results['total_buttons']}")
        print(f"  الأزرار العاملة: {self.test_results['working_buttons']} ✅")
        print(f"  الأزرار المعطلة: {self.test_results['broken_buttons']} ❌")
        print(f"  الأزرار المكررة: {self.test_results['redundant_buttons']} 🔄")
        
        overall_success = (self.test_results['working_buttons'] / self.test_results['total_buttons'] * 100) if self.test_results['total_buttons'] > 0 else 0
        print(f"  معدل النجاح الإجمالي: {overall_success:.1f}%")
        
        print(f"\n🔧 المشاكل المكتشفة ({len(set(self.test_results['issues_found']))}):")
        for issue in set(self.test_results['issues_found']):
            count = self.test_results['issues_found'].count(issue)
            print(f"  - {issue} ({count} مرة)")
        
        print(f"\n💡 التوصيات ({len(set(self.test_results['recommendations']))}):")
        for recommendation in set(self.test_results['recommendations']):
            print(f"  - {recommendation}")
        
        # حفظ التقرير في ملف
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'test_results': self.test_results
        }
        
        with open('button_test_report.json', 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 تم حفظ التقرير المفصل في: button_test_report.json")
        
        return self.test_results

if __name__ == "__main__":
    tester = ButtonTester()
    
    print("🔧 اختبار شامل لجميع الأزرار في نظام المحاسبة العربي")
    print("=" * 60)
    
    if tester.run_comprehensive_test():
        results = tester.generate_report()
        
        if results['broken_buttons'] == 0 and results['redundant_buttons'] == 0:
            print("\n🎉 ممتاز! جميع الأزرار تعمل بشكل صحيح ولا توجد أزرار مكررة")
        else:
            print(f"\n⚠️  يحتاج النظام إلى إصلاحات:")
            print(f"   - إصلاح {results['broken_buttons']} زر معطل")
            print(f"   - حذف {results['redundant_buttons']} زر مكرر")
    else:
        print("❌ فشل في تشغيل الاختبار")
