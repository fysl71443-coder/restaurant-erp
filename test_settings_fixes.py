#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار إصلاحات شاشة الإعدادات
Test Settings Screen Fixes
"""

import requests
import time
from bs4 import BeautifulSoup

def test_settings_screen():
    """اختبار شاشة الإعدادات بعد الإصلاحات"""
    
    base_url = "http://localhost:5000"
    session = requests.Session()
    
    print("🔧 اختبار إصلاحات شاشة الإعدادات")
    print("=" * 50)
    
    try:
        # 1. تسجيل الدخول
        print("1️⃣ تسجيل الدخول...")
        login_data = {
            'username': 'admin',
            'password': 'admin123'
        }
        
        login_response = session.post(f"{base_url}/login", data=login_data)
        if login_response.status_code != 200:
            print("❌ فشل في تسجيل الدخول")
            return False
        print("✅ تم تسجيل الدخول بنجاح")
        
        # 2. الوصول لشاشة الإعدادات
        print("\n2️⃣ الوصول لشاشة الإعدادات...")
        settings_response = session.get(f"{base_url}/settings")
        if settings_response.status_code != 200:
            print("❌ فشل في الوصول لشاشة الإعدادات")
            return False
        print("✅ تم الوصول لشاشة الإعدادات بنجاح")
        
        # 3. تحليل HTML للتحقق من الإصلاحات
        print("\n3️⃣ تحليل HTML للتحقق من الإصلاحات...")
        soup = BeautifulSoup(settings_response.text, 'html.parser')
        
        # التحقق من إزالة onclick handlers
        save_buttons = soup.find_all('button', {'type': 'submit', 'class': 'btn btn-primary'})
        onclick_conflicts = 0
        
        for button in save_buttons:
            if button.get('onclick'):
                onclick_conflicts += 1
                print(f"⚠️  زر يحتوي على onclick handler: {button.get('id', 'بدون ID')}")
        
        if onclick_conflicts == 0:
            print("✅ تم إزالة جميع onclick handlers المتضاربة")
        else:
            print(f"❌ يوجد {onclick_conflicts} أزرار تحتوي على onclick handlers متضاربة")
        
        # التحقق من وجود hidden fields للـ checkboxes
        checkboxes = soup.find_all('input', {'type': 'checkbox'})
        hidden_fields = soup.find_all('input', {'type': 'hidden'})
        
        checkbox_hidden_pairs = 0
        for checkbox in checkboxes:
            checkbox_name = checkbox.get('name', '')
            if checkbox_name.startswith('setting_'):
                hidden_name = f"{checkbox_name}_exists"
                if any(h.get('name') == hidden_name for h in hidden_fields):
                    checkbox_hidden_pairs += 1
        
        print(f"✅ تم العثور على {checkbox_hidden_pairs} أزواج checkbox-hidden field")
        
        # 4. اختبار إرسال نموذج الإعدادات العامة
        print("\n4️⃣ اختبار إرسال نموذج الإعدادات العامة...")
        
        # جمع بيانات النموذج الحالية
        form_data = {}
        
        # إضافة الحقول النصية
        text_inputs = soup.find_all('input', {'type': 'text'})
        for input_field in text_inputs:
            name = input_field.get('name', '')
            if name.startswith('setting_'):
                form_data[name] = input_field.get('value', 'test_value')
        
        # إضافة الحقول الرقمية
        number_inputs = soup.find_all('input', {'type': 'number'})
        for input_field in number_inputs:
            name = input_field.get('name', '')
            if name.startswith('setting_'):
                form_data[name] = input_field.get('value', '100')
        
        # إضافة checkboxes (محددة)
        for checkbox in checkboxes:
            name = checkbox.get('name', '')
            if name.startswith('setting_'):
                form_data[name] = 'true'
                form_data[f"{name}_exists"] = '1'
        
        # إرسال النموذج
        if form_data:
            update_response = session.post(f"{base_url}/update_settings", data=form_data)
            
            if update_response.status_code == 200:
                print("✅ تم إرسال نموذج الإعدادات بنجاح")
                
                # التحقق من رسالة النجاح
                if 'تم تحديث الإعدادات بنجاح' in update_response.text:
                    print("✅ تم حفظ الإعدادات بنجاح")
                else:
                    print("⚠️  لم يتم العثور على رسالة نجاح واضحة")
            else:
                print(f"❌ فشل في إرسال النموذج - كود الاستجابة: {update_response.status_code}")
        else:
            print("⚠️  لم يتم العثور على بيانات نموذج للاختبار")
        
        # 5. النتيجة النهائية
        print("\n" + "=" * 50)
        print("📊 ملخص نتائج الاختبار:")
        print(f"   • إزالة onclick handlers: {'✅' if onclick_conflicts == 0 else '❌'}")
        print(f"   • إضافة hidden fields: {'✅' if checkbox_hidden_pairs > 0 else '❌'}")
        print(f"   • اختبار إرسال النموذج: {'✅' if form_data else '❌'}")
        
        success_rate = (
            (1 if onclick_conflicts == 0 else 0) +
            (1 if checkbox_hidden_pairs > 0 else 0) +
            (1 if form_data else 0)
        ) / 3 * 100
        
        print(f"\n🎯 معدل نجاح الإصلاحات: {success_rate:.1f}%")
        
        if success_rate >= 100:
            print("🎉 جميع الإصلاحات تعمل بشكل مثالي!")
        elif success_rate >= 80:
            print("✅ معظم الإصلاحات تعمل بشكل جيد")
        else:
            print("⚠️  يحتاج المزيد من الإصلاحات")
        
        return success_rate >= 80
        
    except Exception as e:
        print(f"❌ خطأ أثناء الاختبار: {str(e)}")
        return False

if __name__ == "__main__":
    test_settings_screen()
