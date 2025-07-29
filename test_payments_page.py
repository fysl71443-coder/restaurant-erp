#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار صفحة المدفوعات
Test Payments Page
"""

import requests
from bs4 import BeautifulSoup

def test_payments_page():
    """اختبار صفحة المدفوعات"""
    print("🧪 اختبار صفحة المدفوعات...")
    
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
        
        # اختبار صفحة المدفوعات
        payments_response = session.get('http://localhost:5000/payments')
        print(f"📄 صفحة المدفوعات: {payments_response.status_code}")
        
        if payments_response.status_code == 200:
            print("✅ تم تحميل صفحة المدفوعات بنجاح!")
            
            # فحص المحتوى
            soup = BeautifulSoup(payments_response.text, 'html.parser')
            
            # البحث عن العنوان
            title = soup.find('h2')
            if title:
                print(f"✅ العنوان: {title.text.strip()}")
            
            # البحث عن الجدول
            table = soup.find('table', {'id': 'paymentsTable'})
            if table:
                print("✅ جدول المدفوعات موجود")
                
                # فحص الصفوف
                rows = table.find_all('tr')
                print(f"📊 عدد الصفوف: {len(rows)}")
                
                # فحص البيانات
                tbody = table.find('tbody')
                if tbody:
                    data_rows = tbody.find_all('tr')
                    print(f"📋 عدد صفوف البيانات: {len(data_rows)}")
                    
                    if len(data_rows) > 0:
                        print("✅ يوجد بيانات في الجدول")
                        # عرض أول صف
                        first_row = data_rows[0]
                        cells = first_row.find_all('td')
                        print(f"📝 أول صف: {len(cells)} خلايا")
                        for i, cell in enumerate(cells[:3]):  # أول 3 خلايا فقط
                            print(f"  - خلية {i+1}: {cell.text.strip()[:50]}")
                    else:
                        print("⚠️ لا توجد بيانات في الجدول")
                else:
                    print("❌ لا يوجد tbody في الجدول")
            else:
                print("❌ جدول المدفوعات غير موجود")
                
                # البحث عن رسالة "لا توجد مدفوعات"
                no_data = soup.find('h4', string=lambda text: text and 'لا توجد مدفوعات' in text)
                if no_data:
                    print("ℹ️ رسالة: لا توجد مدفوعات")
            
            # البحث عن أي أخطاء
            error_divs = soup.find_all('div', class_='alert-danger')
            if error_divs:
                print(f"⚠️ أخطاء موجودة: {len(error_divs)}")
                for error in error_divs:
                    print(f"  - {error.text.strip()}")
            else:
                print("✅ لا توجد أخطاء في الصفحة")
                
            # فحص CSS والتنسيق
            cards = soup.find_all('div', class_='card')
            print(f"🎨 عدد البطاقات: {len(cards)}")
            
            # فحص الإحصائيات
            stats_cards = soup.find_all('div', class_=['bg-success', 'bg-danger', 'bg-primary', 'bg-info'])
            print(f"📊 بطاقات الإحصائيات: {len(stats_cards)}")
                
        else:
            print(f"❌ فشل في تحميل صفحة المدفوعات: {payments_response.status_code}")
            print(f"المحتوى: {payments_response.text[:500]}")
            
    except Exception as e:
        print(f"❌ خطأ في الاختبار: {e}")

def main():
    """الدالة الرئيسية"""
    print("🚀 اختبار صفحة المدفوعات")
    print("=" * 40)
    
    test_payments_page()
    
    print("=" * 40)
    print("✅ انتهى الاختبار!")

if __name__ == "__main__":
    main()
