#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار بيانات المدفوعات
Test Payments Data
"""

from app import app
from database import db, Payment
from datetime import datetime

def test_payments_data():
    """اختبار بيانات المدفوعات"""
    print("🔍 اختبار بيانات المدفوعات...")
    print("="*50)
    
    with app.app_context():
        try:
            # جلب جميع المدفوعات
            all_payments = Payment.query.all()
            print(f"📊 إجمالي المدفوعات: {len(all_payments)}")
            
            if not all_payments:
                print("⚠️ لا توجد مدفوعات في قاعدة البيانات")
                return
            
            # حساب الإحصائيات
            total_received = sum(p.amount for p in all_payments if p.payment_type == 'received')
            total_paid = sum(p.amount for p in all_payments if p.payment_type == 'paid')
            net_flow = total_received - total_paid
            
            print(f"💰 إجمالي المقبوضات: {total_received:,.2f} ر.س")
            print(f"💸 إجمالي المدفوعات: {total_paid:,.2f} ر.س")
            print(f"📈 صافي التدفق: {net_flow:,.2f} ر.س")
            
            # تجميع حسب النوع
            received_count = len([p for p in all_payments if p.payment_type == 'received'])
            paid_count = len([p for p in all_payments if p.payment_type == 'paid'])
            
            print(f"📥 عدد المقبوضات: {received_count}")
            print(f"📤 عدد المدفوعات: {paid_count}")
            
            # تجميع حسب طريقة الدفع
            payment_methods = {}
            for payment in all_payments:
                method = payment.payment_method
                if method not in payment_methods:
                    payment_methods[method] = {'count': 0, 'total': 0}
                payment_methods[method]['count'] += 1
                payment_methods[method]['total'] += payment.amount
            
            print("\n💳 إحصائيات طرق الدفع:")
            for method, stats in payment_methods.items():
                print(f"  - {method}: {stats['count']} معاملة، {stats['total']:,.2f} ر.س")
            
            # عرض أول 5 مدفوعات
            print("\n📋 أول 5 مدفوعات:")
            for i, payment in enumerate(all_payments[:5], 1):
                print(f"  {i}. ID: {payment.id}")
                print(f"     المبلغ: {payment.amount:,.2f} ر.س")
                print(f"     النوع: {payment.payment_type}")
                print(f"     الطريقة: {payment.payment_method}")
                print(f"     التاريخ: {payment.date}")
                if payment.customer_name:
                    print(f"     العميل: {payment.customer_name}")
                if payment.supplier_name:
                    print(f"     المورد: {payment.supplier_name}")
                print("     " + "-"*30)
            
            print("\n✅ تم اختبار البيانات بنجاح!")
            
        except Exception as e:
            print(f"❌ خطأ في اختبار البيانات: {e}")

if __name__ == "__main__":
    test_payments_data()
