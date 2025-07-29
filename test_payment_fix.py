#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار إصلاح صفحة الدفع
Test Payment Page Fix
"""

import requests
from bs4 import BeautifulSoup

def test_payment_page():
    """اختبار صفحة الدفع"""
    print("🧪 اختبار صفحة الدفع...")
    
    try:
        # إنشاء جلسة
        session = requests.Session()
        
        # تسجيل الدخول
        login_data = {
            'username': 'admin',
            'password': 'admin123'
        }
        
        login_response = session.post('http://localhost:5000/login', data=login_data)
        print(f"✅ تسجيل الدخول: {login_response.status_code}")
        
        # اختبار صفحة إضافة دفعة
        payment_response = session.get('http://localhost:5000/add_payment')
        print(f"📄 صفحة إضافة الدفع: {payment_response.status_code}")
        
        if payment_response.status_code == 200:
            print("✅ تم تحميل صفحة الدفع بنجاح!")
            
            # فحص المحتوى
            soup = BeautifulSoup(payment_response.text, 'html.parser')
            
            # البحث عن حقل التاريخ
            date_input = soup.find('input', {'id': 'payment_date'})
            if date_input:
                print(f"✅ حقل التاريخ موجود: {date_input.get('value', 'بدون قيمة')}")
            else:
                print("❌ حقل التاريخ غير موجود")
            
            # البحث عن أي أخطاء في الصفحة
            error_divs = soup.find_all('div', class_='alert-danger')
            if error_divs:
                print(f"⚠️ أخطاء موجودة: {len(error_divs)}")
                for error in error_divs:
                    print(f"  - {error.text.strip()}")
            else:
                print("✅ لا توجد أخطاء في الصفحة")
                
        else:
            print(f"❌ فشل في تحميل صفحة الدفع: {payment_response.status_code}")
            print(f"المحتوى: {payment_response.text[:500]}")
            
    except Exception as e:
        print(f"❌ خطأ في الاختبار: {e}")

def main():
    """الدالة الرئيسية"""
    print("🚀 اختبار إصلاح مشكلة moment()")
    print("=" * 40)
    
    test_payment_page()
    
    print("=" * 40)
    print("✅ انتهى الاختبار!")

if __name__ == "__main__":
    main()
