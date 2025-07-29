#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار بسيط لإنشاء الفاتورة
Simple Invoice Creation Test
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from database import Invoice, Customer
from datetime import datetime

def simple_test():
    """اختبار بسيط لإنشاء الفاتورة"""
    print("🧪 اختبار بسيط لإنشاء الفاتورة...")
    
    with app.app_context():
        try:
            # إنشاء فاتورة تجريبية
            print("📄 إنشاء فاتورة تجريبية...")
            
            test_invoice = Invoice(
                customer_name="عميل اختبار بسيط",
                total_amount=1500.00,
                date=datetime.now(),
                notes="فاتورة اختبار بسيط"
            )
            
            db.session.add(test_invoice)
            db.session.commit()
            
            print(f"✅ تم إنشاء الفاتورة بنجاح! معرف الفاتورة: {test_invoice.id}")
            
            # التحقق من الفاتورة
            verify_invoice = Invoice.query.get(test_invoice.id)
            if verify_invoice:
                print(f"✅ تم التحقق من الفاتورة:")
                print(f"   - العميل: {verify_invoice.customer_name}")
                print(f"   - المبلغ: {verify_invoice.total_amount}")
                print(f"   - التاريخ: {verify_invoice.date}")
                print(f"   - الملاحظات: {verify_invoice.notes}")
            
            # عد الفواتير
            total_invoices = Invoice.query.count()
            print(f"📊 إجمالي الفواتير في قاعدة البيانات: {total_invoices}")
            
            print("🎉 الاختبار نجح!")
            
        except Exception as e:
            print(f"❌ خطأ في الاختبار: {e}")
            import traceback
            traceback.print_exc()
            db.session.rollback()

if __name__ == "__main__":
    simple_test()
