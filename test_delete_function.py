#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار وظيفة الحذف المباشر
Test Direct Delete Function
"""

import requests
from bs4 import BeautifulSoup

def test_delete_function():
    """اختبار وظيفة الحذف"""
    print("🧪 اختبار وظيفة الحذف المباشر...")
    
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
        
        # 1. إنشاء دفعة تجريبية للحذف
        print("\n➕ إنشاء دفعة تجريبية للحذف...")
        test_payment_data = {
            'amount': '999.99',
            'payment_method': 'cash',
            'payment_type': 'received',
            'payment_date': '2025-07-29',
            'customer_name': 'عميل تجريبي للحذف',
            'reference_number': 'DELETE-TEST-999',
            'notes': 'دفعة تجريبية للحذف - اختبار'
        }
        
        add_response = session.post('http://localhost:5000/add_payment', data=test_payment_data)
        print(f"📝 إضافة الدفعة: {add_response.status_code}")
        
        # 2. البحث عن الدفعة الجديدة
        print("\n🔍 البحث عن الدفعة الجديدة...")
        payments_response = session.get('http://localhost:5000/payments')
        
        if payments_response.status_code == 200:
            soup = BeautifulSoup(payments_response.text, 'html.parser')
            
            # البحث عن الدفعة التجريبية
            found_payment_id = None
            table = soup.find('table', {'id': 'paymentsTable'})
            
            if table:
                tbody = table.find('tbody')
                if tbody:
                    rows = tbody.find_all('tr')
                    for row in rows:
                        if 'عميل تجريبي للحذف' in row.text:
                            print("✅ تم العثور على الدفعة التجريبية")
                            
                            # استخراج معرف الدفعة من زر الحذف
                            delete_button = row.find('button', title='حذف')
                            if delete_button and 'onclick' in delete_button.attrs:
                                onclick_text = delete_button['onclick']
                                import re
                                match = re.search(r'confirmDelete\((\d+)\)', onclick_text)
                                if match:
                                    found_payment_id = match.group(1)
                                    print(f"📋 معرف الدفعة: {found_payment_id}")
                                    break
            
            if found_payment_id:
                # 3. اختبار حذف الدفعة
                print(f"\n🗑️ حذف الدفعة {found_payment_id}...")
                delete_response = session.get(f'http://localhost:5000/delete_payment/{found_payment_id}')
                print(f"🗑️ استجابة الحذف: {delete_response.status_code}")
                
                if delete_response.status_code in [200, 302]:
                    print("✅ تم حذف الدفعة بنجاح")
                    
                    # 4. التحقق من الحذف
                    print("\n✅ التحقق من الحذف...")
                    verify_response = session.get('http://localhost:5000/payments')
                    
                    if verify_response.status_code == 200:
                        if 'عميل تجريبي للحذف' not in verify_response.text:
                            print("✅ تم التحقق: الدفعة لم تعد موجودة")
                            print("🎉 وظيفة الحذف تعمل بشكل مثالي!")
                        else:
                            print("⚠️ تحذير: الدفعة ما زالت موجودة بعد الحذف")
                    else:
                        print(f"❌ فشل في التحقق: {verify_response.status_code}")
                else:
                    print(f"❌ فشل في حذف الدفعة: {delete_response.status_code}")
                    
                    # طباعة محتوى الاستجابة للتشخيص
                    if delete_response.text:
                        print("📄 محتوى الاستجابة:")
                        print(delete_response.text[:500])
            else:
                print("❌ لم يتم العثور على معرف الدفعة")
        else:
            print(f"❌ فشل في تحميل صفحة المدفوعات: {payments_response.status_code}")
        
        # 5. اختبار إضافي: حذف دفعة غير موجودة
        print(f"\n🧪 اختبار حذف دفعة غير موجودة...")
        fake_delete_response = session.get('http://localhost:5000/delete_payment/99999')
        print(f"🗑️ حذف دفعة غير موجودة: {fake_delete_response.status_code}")
        
        if fake_delete_response.status_code == 404:
            print("✅ النظام يتعامل بشكل صحيح مع الدفعات غير الموجودة")
        elif fake_delete_response.status_code in [200, 302]:
            print("⚠️ النظام لا يتحقق من وجود الدفعة قبل الحذف")
        
    except Exception as e:
        print(f"❌ خطأ في الاختبار: {e}")
        import traceback
        traceback.print_exc()

def main():
    """الدالة الرئيسية"""
    print("🚀 اختبار وظيفة الحذف المباشر")
    print("=" * 40)
    
    test_delete_function()
    
    print("=" * 40)
    print("✅ انتهى اختبار الحذف!")

if __name__ == "__main__":
    main()
