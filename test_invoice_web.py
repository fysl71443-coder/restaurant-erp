#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار إنشاء الفاتورة عبر الويب
Test Invoice Creation via Web
"""

import requests
import time
from datetime import datetime

def test_invoice_web():
    """اختبار إنشاء الفاتورة عبر الويب"""
    print("🌐 اختبار إنشاء الفاتورة عبر الويب...")
    
    base_url = "http://localhost:5000"
    
    try:
        # إنشاء جلسة
        session = requests.Session()
        
        # 1. اختبار الاتصال بالخادم
        print("🔗 اختبار الاتصال بالخادم...")
        try:
            response = session.get(f"{base_url}/")
            if response.status_code == 200:
                print("✅ الخادم يعمل بشكل طبيعي")
            else:
                print(f"⚠️ الخادم يستجيب بكود: {response.status_code}")
        except requests.exceptions.ConnectionError:
            print("❌ لا يمكن الاتصال بالخادم. تأكد من تشغيل الخادم على المنفذ 5000")
            return
        
        # 2. تسجيل الدخول
        print("\n🔐 تسجيل الدخول...")
        login_data = {
            'username': 'admin',
            'password': 'admin123'
        }
        
        login_response = session.post(f"{base_url}/login", data=login_data)
        if login_response.status_code == 200:
            print("✅ تم تسجيل الدخول بنجاح")
        else:
            print(f"❌ فشل في تسجيل الدخول: {login_response.status_code}")
            return
        
        # 3. اختبار صفحة الفواتير
        print("\n📋 اختبار صفحة الفواتير...")
        invoices_response = session.get(f"{base_url}/invoices")
        
        if invoices_response.status_code == 200:
            print("✅ صفحة الفواتير تعمل بشكل طبيعي")
        else:
            print(f"❌ مشكلة في صفحة الفواتير: {invoices_response.status_code}")
        
        # 4. اختبار صفحة إنشاء الفاتورة
        print("\n➕ اختبار صفحة إنشاء الفاتورة...")
        add_invoice_response = session.get(f"{base_url}/add_invoice")
        
        if add_invoice_response.status_code == 200:
            print("✅ صفحة إنشاء الفاتورة تعمل بشكل طبيعي")
        else:
            print(f"❌ مشكلة في صفحة إنشاء الفاتورة: {add_invoice_response.status_code}")
            print(f"📄 محتوى الاستجابة: {add_invoice_response.text[:500]}")
            return
        
        # 5. إرسال فاتورة تجريبية
        print("\n📤 إرسال فاتورة تجريبية...")
        
        current_time = datetime.now().strftime("%Y-%m-%d")
        test_invoice_data = {
            'customer_name': f'عميل اختبار الويب - {datetime.now().strftime("%H:%M:%S")}',
            'total_amount': '2500.00',
            'invoice_date': current_time,
            'notes': 'فاتورة اختبار عبر الويب'
        }
        
        print(f"📋 بيانات الفاتورة: {test_invoice_data}")
        
        # قياس زمن الاستجابة
        start_time = time.time()
        create_response = session.post(f"{base_url}/add_invoice", data=test_invoice_data)
        end_time = time.time()
        
        response_time = end_time - start_time
        print(f"⏱️ زمن الاستجابة: {response_time:.2f} ثانية")
        print(f"📊 كود الاستجابة: {create_response.status_code}")
        
        # تحليل الاستجابة
        if create_response.status_code == 200:
            # فحص إذا كانت الصفحة تحتوي على رسائل نجاح أو خطأ
            response_text = create_response.text
            
            if 'تم إنشاء الفاتورة بنجاح' in response_text:
                print("✅ تم إنشاء الفاتورة بنجاح!")
            elif 'خطأ' in response_text or 'error' in response_text.lower():
                print("❌ حدث خطأ أثناء إنشاء الفاتورة")
                
                # البحث عن رسائل الخطأ
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response_text, 'html.parser')
                error_messages = soup.find_all(class_=['alert-danger', 'error', 'text-danger'])
                
                for error in error_messages:
                    error_text = error.get_text().strip()
                    if error_text and len(error_text) > 3:
                        print(f"❌ رسالة خطأ: {error_text}")
            else:
                print("⚠️ لا توجد رسائل واضحة حول نتيجة العملية")
                
        elif create_response.status_code == 302:
            print("✅ تم إعادة التوجيه (نجح الإنشاء)")
            redirect_location = create_response.headers.get('Location', 'غير محدد')
            print(f"📍 موقع إعادة التوجيه: {redirect_location}")
            
        elif create_response.status_code == 500:
            print("❌ خطأ خادم داخلي (500)")
            print("📄 محتوى الخطأ:")
            print(create_response.text[:1000])
            
        else:
            print(f"⚠️ كود استجابة غير متوقع: {create_response.status_code}")
            print(f"📄 محتوى الاستجابة: {create_response.text[:500]}")
        
        # 6. التحقق من إنشاء الفاتورة
        print("\n🔍 التحقق من إنشاء الفاتورة...")
        
        verify_response = session.get(f"{base_url}/invoices")
        if verify_response.status_code == 200:
            if test_invoice_data['customer_name'] in verify_response.text:
                print("✅ تم العثور على الفاتورة الجديدة في قائمة الفواتير!")
            else:
                print("❌ لم يتم العثور على الفاتورة الجديدة")
        
        # 7. اختبار الأداء
        print("\n⚡ اختبار الأداء...")
        
        performance_times = []
        for i in range(3):
            start = time.time()
            test_response = session.get(f"{base_url}/add_invoice")
            end = time.time()
            performance_times.append(end - start)
        
        avg_time = sum(performance_times) / len(performance_times)
        print(f"📊 متوسط زمن تحميل صفحة إنشاء الفاتورة: {avg_time:.3f} ثانية")
        
        if avg_time < 1.0:
            print("✅ الأداء ممتاز")
        elif avg_time < 3.0:
            print("⚠️ الأداء مقبول")
        else:
            print("❌ الأداء بطيء")
        
        print("\n🎉 انتهى اختبار إنشاء الفاتورة عبر الويب!")
        
    except Exception as e:
        print(f"❌ خطأ في الاختبار: {e}")
        import traceback
        traceback.print_exc()

def main():
    """الدالة الرئيسية"""
    print("🚀 اختبار إنشاء الفاتورة عبر الويب")
    print("=" * 60)
    
    test_invoice_web()
    
    print("=" * 60)
    print("✅ انتهى الاختبار!")

if __name__ == "__main__":
    main()
