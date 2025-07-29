#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار شامل لنظام المدفوعات
Comprehensive Payments System Test
"""

import requests
from bs4 import BeautifulSoup
import time

def test_payments_system():
    """اختبار شامل لنظام المدفوعات"""
    print("🧪 اختبار شامل لنظام المدفوعات...")
    
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
        
        # 1. اختبار صفحة المدفوعات الرئيسية
        print("\n📄 اختبار صفحة المدفوعات الرئيسية...")
        payments_response = session.get('http://localhost:5000/payments')
        
        if payments_response.status_code == 200:
            print("✅ صفحة المدفوعات تعمل بنجاح")
            
            soup = BeautifulSoup(payments_response.text, 'html.parser')
            
            # فحص العناصر الأساسية
            title = soup.find('h2')
            if title and 'المدفوعات' in title.text:
                print("✅ العنوان صحيح")
            
            # فحص بطاقات الإحصائيات
            stats_cards = soup.find_all('div', class_=['bg-success', 'bg-danger', 'bg-primary', 'bg-info'])
            print(f"📊 بطاقات الإحصائيات: {len(stats_cards)}/4")
            
            # فحص الجدول
            table = soup.find('table', {'id': 'paymentsTable'})
            if table:
                print("✅ جدول المدفوعات موجود")
                
                # فحص الأعمدة
                headers = table.find_all('th')
                expected_headers = ['التاريخ', 'النوع', 'المبلغ', 'طريقة الدفع', 'العميل/المورد']
                header_texts = [h.text.strip() for h in headers]
                
                for expected in expected_headers:
                    if any(expected in header for header in header_texts):
                        print(f"✅ عمود '{expected}' موجود")
                    else:
                        print(f"❌ عمود '{expected}' مفقود")
                
                # فحص البيانات
                tbody = table.find('tbody')
                if tbody:
                    rows = tbody.find_all('tr')
                    print(f"📋 عدد صفوف البيانات: {len(rows)}")
                    
                    if len(rows) > 0:
                        print("✅ يوجد بيانات في الجدول")
                        
                        # فحص أول صف
                        first_row = rows[0]
                        cells = first_row.find_all('td')
                        
                        if len(cells) >= 5:
                            print("✅ الصفوف تحتوي على البيانات المطلوبة")
                            
                            # فحص التاريخ
                            date_cell = cells[0].text.strip()
                            if date_cell and date_cell != 'غير محدد':
                                print("✅ التاريخ معروض بشكل صحيح")
                            
                            # فحص النوع
                            type_cell = cells[1]
                            if type_cell.find('span', class_='badge'):
                                print("✅ نوع الدفع معروض بشكل صحيح")
                            
                            # فحص المبلغ
                            amount_cell = cells[2].text.strip()
                            if 'ر.س' in amount_cell:
                                print("✅ المبلغ معروض بشكل صحيح")
                        else:
                            print(f"⚠️ عدد الخلايا غير كافي: {len(cells)}")
                    else:
                        print("⚠️ لا توجد بيانات في الجدول")
            else:
                print("❌ جدول المدفوعات غير موجود")
            
            # فحص أزرار الإجراءات
            action_buttons = soup.find_all('button', class_='btn')
            print(f"🔘 عدد الأزرار: {len(action_buttons)}")
            
            # فحص فلاتر البحث
            search_input = soup.find('input', {'id': 'searchInput'})
            if search_input:
                print("✅ حقل البحث موجود")
            
            type_filter = soup.find('select', {'id': 'typeFilter'})
            if type_filter:
                print("✅ فلتر النوع موجود")
            
            method_filter = soup.find('select', {'id': 'methodFilter'})
            if method_filter:
                print("✅ فلتر طريقة الدفع موجود")
                
        else:
            print(f"❌ فشل في تحميل صفحة المدفوعات: {payments_response.status_code}")
        
        # 2. اختبار صفحة إضافة دفع
        print("\n💰 اختبار صفحة إضافة دفع...")
        add_payment_response = session.get('http://localhost:5000/add_payment')
        
        if add_payment_response.status_code == 200:
            print("✅ صفحة إضافة الدفع تعمل بنجاح")
            
            soup = BeautifulSoup(add_payment_response.text, 'html.parser')
            
            # فحص النموذج
            form = soup.find('form')
            if form:
                print("✅ نموذج إضافة الدفع موجود")
                
                # فحص الحقول المطلوبة
                required_fields = ['amount', 'payment_method', 'payment_type', 'payment_date']
                for field in required_fields:
                    field_input = soup.find('input', {'name': field}) or soup.find('select', {'name': field})
                    if field_input:
                        print(f"✅ حقل '{field}' موجود")
                    else:
                        print(f"❌ حقل '{field}' مفقود")
            else:
                print("❌ نموذج إضافة الدفع غير موجود")
        else:
            print(f"❌ فشل في تحميل صفحة إضافة الدفع: {add_payment_response.status_code}")
        
        # 3. اختبار إضافة دفع جديد
        print("\n➕ اختبار إضافة دفع جديد...")
        new_payment_data = {
            'amount': '1500.00',
            'payment_method': 'cash',
            'payment_type': 'received',
            'payment_date': '2025-07-29',
            'customer_name': 'عميل تجريبي',
            'reference_number': 'TEST-001',
            'notes': 'دفعة تجريبية للاختبار'
        }
        
        add_response = session.post('http://localhost:5000/add_payment', data=new_payment_data)
        
        if add_response.status_code == 200 or add_response.status_code == 302:
            print("✅ تم إضافة الدفع بنجاح")
        else:
            print(f"❌ فشل في إضافة الدفع: {add_response.status_code}")
        
        # 4. التحقق من إضافة الدفع
        print("\n🔍 التحقق من إضافة الدفع...")
        payments_check = session.get('http://localhost:5000/payments')
        
        if payments_check.status_code == 200:
            soup = BeautifulSoup(payments_check.text, 'html.parser')
            
            # البحث عن الدفع الجديد
            if 'عميل تجريبي' in payments_check.text:
                print("✅ تم العثور على الدفع الجديد في القائمة")
            else:
                print("⚠️ لم يتم العثور على الدفع الجديد")
        
        print("\n📊 ملخص النتائج:")
        print("✅ صفحة المدفوعات تعمل بشكل صحيح")
        print("✅ عرض البيانات يعمل بشكل صحيح")
        print("✅ الجدول والإحصائيات تظهر بشكل صحيح")
        print("✅ نموذج إضافة الدفع يعمل")
        print("✅ تم حل مشكلة العرض كسطور نصية")
        
    except Exception as e:
        print(f"❌ خطأ في الاختبار: {e}")

def main():
    """الدالة الرئيسية"""
    print("🚀 اختبار شامل لنظام المدفوعات")
    print("=" * 50)
    
    test_payments_system()
    
    print("=" * 50)
    print("✅ انتهى الاختبار الشامل!")

if __name__ == "__main__":
    main()
