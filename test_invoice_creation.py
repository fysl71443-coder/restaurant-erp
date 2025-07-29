#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار إنشاء الفاتورة
Test Invoice Creation
"""

import requests
from bs4 import BeautifulSoup
import time

def test_invoice_creation():
    """اختبار إنشاء الفاتورة"""
    print("🧪 اختبار إنشاء الفاتورة...")
    
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
        
        # 1. اختبار تحميل صفحة الفواتير العامة
        print("\n📋 اختبار صفحة الفواتير العامة...")
        invoices_response = session.get('http://localhost:5000/invoices')
        
        if invoices_response.status_code == 200:
            print("✅ صفحة الفواتير العامة تحمل بنجاح")
            
            # فحص وجود زر إنشاء فاتورة
            soup = BeautifulSoup(invoices_response.text, 'html.parser')
            create_button = soup.find('a', href='/add_invoice')
            
            if create_button:
                print("✅ زر إنشاء فاتورة موجود")
                print(f"📝 نص الزر: {create_button.get_text().strip()}")
            else:
                print("❌ زر إنشاء فاتورة غير موجود")
        else:
            print(f"❌ فشل في تحميل صفحة الفواتير: {invoices_response.status_code}")
        
        # 2. اختبار تحميل صفحة إنشاء الفاتورة
        print("\n➕ اختبار صفحة إنشاء الفاتورة...")
        add_invoice_response = session.get('http://localhost:5000/add_invoice')
        
        if add_invoice_response.status_code == 200:
            print("✅ صفحة إنشاء الفاتورة تحمل بنجاح")
            
            # فحص النموذج
            soup = BeautifulSoup(add_invoice_response.text, 'html.parser')
            
            form = soup.find('form', {'id': 'invoiceForm'})
            if form:
                print("✅ نموذج الفاتورة موجود")
                
                # فحص الحقول المطلوبة
                customer_name = soup.find('input', {'name': 'customer_name'})
                total_amount = soup.find('input', {'name': 'total_amount'})
                submit_button = soup.find('button', {'type': 'submit'})
                
                print(f"📝 حقل اسم العميل: {'✅ موجود' if customer_name else '❌ مفقود'}")
                print(f"📝 حقل المبلغ الإجمالي: {'✅ موجود' if total_amount else '❌ مفقود'}")
                print(f"🔘 زر الإرسال: {'✅ موجود' if submit_button else '❌ مفقود'}")
                
                if submit_button:
                    print(f"📝 نص زر الإرسال: {submit_button.get_text().strip()}")
            else:
                print("❌ نموذج الفاتورة غير موجود")
        else:
            print(f"❌ فشل في تحميل صفحة إنشاء الفاتورة: {add_invoice_response.status_code}")
            print(f"📄 محتوى الاستجابة: {add_invoice_response.text[:500]}")
        
        # 3. اختبار إرسال فاتورة تجريبية
        print("\n📤 اختبار إرسال فاتورة تجريبية...")
        
        test_invoice_data = {
            'customer_name': 'عميل تجريبي للاختبار',
            'total_amount': '1500.00',
            'invoice_date': '2025-07-29',
            'notes': 'فاتورة تجريبية للاختبار'
        }
        
        print(f"📋 بيانات الفاتورة التجريبية: {test_invoice_data}")
        
        # إرسال البيانات
        start_time = time.time()
        create_response = session.post('http://localhost:5000/add_invoice', data=test_invoice_data)
        end_time = time.time()
        
        response_time = end_time - start_time
        print(f"⏱️ زمن الاستجابة: {response_time:.2f} ثانية")
        print(f"📊 كود الاستجابة: {create_response.status_code}")
        
        if create_response.status_code == 200:
            # فحص إذا كانت الصفحة تحتوي على أخطاء
            if 'خطأ' in create_response.text or 'error' in create_response.text.lower():
                print("⚠️ الاستجابة تحتوي على رسائل خطأ")
                
                # البحث عن رسائل الخطأ
                soup = BeautifulSoup(create_response.text, 'html.parser')
                error_messages = soup.find_all(class_=['alert-danger', 'error', 'text-danger'])
                
                for error in error_messages:
                    print(f"❌ رسالة خطأ: {error.get_text().strip()}")
            else:
                print("✅ لا توجد رسائل خطأ واضحة")
                
        elif create_response.status_code == 302:
            print("✅ تم إعادة التوجيه (نجح الإنشاء)")
            print(f"📍 موقع إعادة التوجيه: {create_response.headers.get('Location', 'غير محدد')}")
            
        elif create_response.status_code == 500:
            print("❌ خطأ خادم داخلي (500)")
            print("📄 محتوى الخطأ:")
            print(create_response.text[:1000])
            
        else:
            print(f"⚠️ كود استجابة غير متوقع: {create_response.status_code}")
        
        # 4. فحص إذا تم إنشاء الفاتورة فعلاً
        print("\n🔍 التحقق من إنشاء الفاتورة...")
        
        verify_response = session.get('http://localhost:5000/invoices')
        if verify_response.status_code == 200:
            if 'عميل تجريبي للاختبار' in verify_response.text:
                print("✅ تم إنشاء الفاتورة بنجاح!")
            else:
                print("❌ لم يتم العثور على الفاتورة الجديدة")
        
        # 5. اختبار الأداء
        print("\n⚡ اختبار الأداء...")
        
        performance_times = []
        for i in range(3):
            start = time.time()
            test_response = session.get('http://localhost:5000/add_invoice')
            end = time.time()
            performance_times.append(end - start)
        
        avg_time = sum(performance_times) / len(performance_times)
        print(f"📊 متوسط زمن تحميل الصفحة: {avg_time:.3f} ثانية")
        
        if avg_time < 1.0:
            print("✅ الأداء ممتاز")
        elif avg_time < 3.0:
            print("⚠️ الأداء مقبول")
        else:
            print("❌ الأداء بطيء")
        
    except Exception as e:
        print(f"❌ خطأ في الاختبار: {e}")
        import traceback
        traceback.print_exc()

def main():
    """الدالة الرئيسية"""
    print("🚀 اختبار إنشاء الفاتورة")
    print("=" * 50)
    
    test_invoice_creation()
    
    print("=" * 50)
    print("✅ انتهى اختبار إنشاء الفاتورة!")

if __name__ == "__main__":
    main()
