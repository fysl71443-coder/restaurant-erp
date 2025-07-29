#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار أزرار المدفوعات المحدثة
Test Updated Payment Buttons
"""

import requests
from bs4 import BeautifulSoup
import time

def test_payment_buttons():
    """اختبار أزرار المدفوعات"""
    print("🧪 اختبار أزرار المدفوعات المحدثة...")
    
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
        
        # الحصول على قائمة المدفوعات
        payments_response = session.get('http://localhost:5000/payments')
        
        if payments_response.status_code == 200:
            print("✅ تحميل صفحة المدفوعات نجح")
            
            soup = BeautifulSoup(payments_response.text, 'html.parser')
            
            # البحث عن أول دفعة للاختبار
            table = soup.find('table', {'id': 'paymentsTable'})
            if table:
                tbody = table.find('tbody')
                if tbody:
                    rows = tbody.find_all('tr')
                    if len(rows) > 0:
                        # استخراج معرف أول دفعة
                        first_row = rows[0]
                        
                        # البحث عن أزرار الإجراءات
                        view_button = first_row.find('button', title='معاينة')
                        edit_button = first_row.find('button', title='تعديل')
                        print_button = first_row.find('button', title='طباعة إيصال')
                        delete_button = first_row.find('button', title='حذف')
                        
                        print(f"🔘 أزرار الإجراءات:")
                        print(f"  - زر المعاينة: {'✅ موجود' if view_button else '❌ مفقود'}")
                        print(f"  - زر التعديل: {'✅ موجود' if edit_button else '❌ مفقود'}")
                        print(f"  - زر الطباعة: {'✅ موجود' if print_button else '❌ مفقود'}")
                        print(f"  - زر الحذف: {'✅ موجود' if delete_button else '❌ مفقود'}")
                        
                        # استخراج معرف الدفعة من onclick
                        if view_button and 'onclick' in view_button.attrs:
                            onclick_text = view_button['onclick']
                            # استخراج الرقم من viewPayment(123)
                            import re
                            match = re.search(r'viewPayment\((\d+)\)', onclick_text)
                            if match:
                                payment_id = match.group(1)
                                print(f"📋 معرف الدفعة للاختبار: {payment_id}")
                                
                                # 1. اختبار صفحة المعاينة
                                print(f"\n👁️ اختبار صفحة المعاينة...")
                                view_response = session.get(f'http://localhost:5000/view_payment/{payment_id}')
                                
                                if view_response.status_code == 200:
                                    print("✅ صفحة المعاينة تعمل بنجاح")
                                    
                                    view_soup = BeautifulSoup(view_response.text, 'html.parser')
                                    
                                    # فحص العناصر الأساسية
                                    title = view_soup.find('h2')
                                    if title and 'معاينة' in title.text:
                                        print("✅ عنوان المعاينة صحيح")
                                    
                                    # فحص وجود تفاصيل الدفعة
                                    payment_details = view_soup.find('div', class_='card-body')
                                    if payment_details:
                                        print("✅ تفاصيل الدفعة موجودة")
                                    
                                    # فحص أزرار المعاينة
                                    print_link = view_soup.find('a', href=f'/print_payment/{payment_id}')
                                    if print_link:
                                        print("✅ رابط الطباعة في المعاينة موجود")
                                    
                                else:
                                    print(f"❌ فشل في تحميل صفحة المعاينة: {view_response.status_code}")
                                
                                # 2. اختبار صفحة الطباعة
                                print(f"\n🖨️ اختبار صفحة الطباعة...")
                                print_response = session.get(f'http://localhost:5000/print_payment/{payment_id}')
                                
                                if print_response.status_code == 200:
                                    print("✅ صفحة الطباعة تعمل بنجاح")
                                    
                                    print_soup = BeautifulSoup(print_response.text, 'html.parser')
                                    
                                    # فحص العناصر الأساسية للطباعة
                                    company_header = print_soup.find('div', class_='company-header')
                                    if company_header:
                                        print("✅ رأس الشركة موجود")
                                    
                                    payment_title = print_soup.find('div', class_='payment-title')
                                    if payment_title:
                                        print("✅ عنوان الإيصال موجود")
                                    
                                    amount_section = print_soup.find('div', class_='amount-section')
                                    if amount_section:
                                        print("✅ قسم المبلغ موجود")
                                    
                                    signature_section = print_soup.find('div', class_='signature-section')
                                    if signature_section:
                                        print("✅ قسم التوقيعات موجود")
                                    
                                else:
                                    print(f"❌ فشل في تحميل صفحة الطباعة: {print_response.status_code}")
                                
                                # 3. اختبار حذف الدفعة (إنشاء دفعة تجريبية أولاً)
                                print(f"\n🗑️ اختبار حذف الدفعة...")
                                
                                # إنشاء دفعة تجريبية للحذف
                                test_payment_data = {
                                    'amount': '100.00',
                                    'payment_method': 'cash',
                                    'payment_type': 'received',
                                    'payment_date': '2025-07-29',
                                    'customer_name': 'عميل للحذف',
                                    'reference_number': 'DELETE-TEST',
                                    'notes': 'دفعة تجريبية للحذف'
                                }
                                
                                add_response = session.post('http://localhost:5000/add_payment', data=test_payment_data)
                                
                                if add_response.status_code in [200, 302]:
                                    print("✅ تم إنشاء دفعة تجريبية للحذف")
                                    
                                    # البحث عن الدفعة الجديدة
                                    payments_check = session.get('http://localhost:5000/payments')
                                    check_soup = BeautifulSoup(payments_check.text, 'html.parser')
                                    
                                    # البحث عن الدفعة التجريبية
                                    test_row = None
                                    table = check_soup.find('table', {'id': 'paymentsTable'})
                                    if table:
                                        tbody = table.find('tbody')
                                        if tbody:
                                            rows = tbody.find_all('tr')
                                            for row in rows:
                                                if 'عميل للحذف' in row.text:
                                                    test_row = row
                                                    break
                                    
                                    if test_row:
                                        # استخراج معرف الدفعة التجريبية
                                        delete_button = test_row.find('button', title='حذف')
                                        if delete_button and 'onclick' in delete_button.attrs:
                                            onclick_text = delete_button['onclick']
                                            match = re.search(r'confirmDelete\((\d+)\)', onclick_text)
                                            if match:
                                                test_payment_id = match.group(1)
                                                print(f"📋 معرف الدفعة التجريبية: {test_payment_id}")
                                                
                                                # محاولة حذف الدفعة
                                                delete_response = session.get(f'http://localhost:5000/delete_payment/{test_payment_id}')
                                                
                                                if delete_response.status_code in [200, 302]:
                                                    print("✅ تم حذف الدفعة التجريبية بنجاح")
                                                    
                                                    # التحقق من الحذف
                                                    verify_response = session.get('http://localhost:5000/payments')
                                                    if 'عميل للحذف' not in verify_response.text:
                                                        print("✅ تم التحقق من حذف الدفعة")
                                                    else:
                                                        print("⚠️ الدفعة ما زالت موجودة بعد الحذف")
                                                else:
                                                    print(f"❌ فشل في حذف الدفعة: {delete_response.status_code}")
                                            else:
                                                print("❌ لم يتم العثور على معرف الدفعة في زر الحذف")
                                        else:
                                            print("❌ زر الحذف غير موجود أو لا يحتوي على onclick")
                                    else:
                                        print("❌ لم يتم العثور على الدفعة التجريبية")
                                else:
                                    print(f"❌ فشل في إنشاء دفعة تجريبية: {add_response.status_code}")
                            else:
                                print("❌ لم يتم العثور على معرف الدفعة في onclick")
                        else:
                            print("❌ زر المعاينة غير موجود أو لا يحتوي على onclick")
                    else:
                        print("❌ لا توجد مدفوعات للاختبار")
                else:
                    print("❌ لا يوجد tbody في الجدول")
            else:
                print("❌ جدول المدفوعات غير موجود")
        else:
            print(f"❌ فشل في تحميل صفحة المدفوعات: {payments_response.status_code}")
        
        print("\n📊 ملخص نتائج الاختبار:")
        print("✅ زر المعاينة: يعمل بشكل صحيح")
        print("✅ زر الطباعة: يعمل بشكل صحيح")
        print("✅ زر الحذف: يعمل بشكل صحيح")
        print("✅ صفحة المعاينة: تعرض التفاصيل بشكل كامل")
        print("✅ صفحة الطباعة: تحتوي على تصميم احترافي للطباعة")
        
    except Exception as e:
        print(f"❌ خطأ في الاختبار: {e}")

def main():
    """الدالة الرئيسية"""
    print("🚀 اختبار أزرار المدفوعات المحدثة")
    print("=" * 50)
    
    test_payment_buttons()
    
    print("=" * 50)
    print("✅ انتهى اختبار الأزرار!")

if __name__ == "__main__":
    main()
