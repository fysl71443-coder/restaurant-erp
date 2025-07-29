#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
تشخيص مشكلة إنشاء الفاتورة
Debug Invoice Creation Issue
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from database import Invoice, Customer
from datetime import datetime

def debug_invoice_creation():
    """تشخيص مشكلة إنشاء الفاتورة"""
    print("🔍 تشخيص مشكلة إنشاء الفاتورة...")
    
    with app.app_context():
        try:
            # 1. فحص قاعدة البيانات
            print("\n📊 فحص قاعدة البيانات...")
            
            # فحص جدول العملاء
            try:
                customers_count = Customer.query.count()
                print(f"✅ جدول العملاء: {customers_count} عميل")
            except Exception as e:
                print(f"❌ خطأ في جدول العملاء: {e}")
            
            # فحص جدول الفواتير
            try:
                invoices_count = Invoice.query.count()
                print(f"✅ جدول الفواتير: {invoices_count} فاتورة")
            except Exception as e:
                print(f"❌ خطأ في جدول الفواتير: {e}")
            
            # 2. محاولة إنشاء فاتورة تجريبية
            print("\n➕ محاولة إنشاء فاتورة تجريبية...")
            
            try:
                # إنشاء عميل تجريبي أولاً
                test_customer_name = "عميل تجريبي للتشخيص"
                
                # البحث عن العميل أو إنشاؤه
                customer = Customer.query.filter_by(name=test_customer_name).first()
                if not customer:
                    print("📝 إنشاء عميل جديد...")
                    customer = Customer(name=test_customer_name)
                    db.session.add(customer)
                    db.session.flush()
                    print(f"✅ تم إنشاء العميل بمعرف: {customer.id}")
                else:
                    print(f"✅ العميل موجود بمعرف: {customer.id}")
                
                # إنشاء رقم فاتورة
                try:
                    last_invoice = Invoice.query.order_by(Invoice.id.desc()).first()
                    invoice_number = f"INV-{(last_invoice.id + 1) if last_invoice else 1:06d}"
                    print(f"📋 رقم الفاتورة الجديد: {invoice_number}")
                except Exception as e:
                    invoice_number = "INV-000001"
                    print(f"⚠️ استخدام رقم افتراضي: {invoice_number} (خطأ: {e})")
                
                # إنشاء الفاتورة
                print("📄 إنشاء الفاتورة...")
                new_invoice = Invoice(
                    customer_id=customer.id,
                    customer_name=test_customer_name,
                    invoice_number=invoice_number,
                    total_amount=1500.00,
                    subtotal=1500.00,
                    date=datetime.now(),
                    notes="فاتورة تجريبية للتشخيص"
                )
                
                db.session.add(new_invoice)
                db.session.commit()
                
                print(f"✅ تم إنشاء الفاتورة بنجاح! معرف الفاتورة: {new_invoice.id}")
                
                # التحقق من الفاتورة
                verify_invoice = Invoice.query.get(new_invoice.id)
                if verify_invoice:
                    print(f"✅ تم التحقق من الفاتورة: {verify_invoice.invoice_number}")
                    print(f"📋 تفاصيل الفاتورة:")
                    print(f"   - العميل: {verify_invoice.customer_name}")
                    print(f"   - المبلغ: {verify_invoice.total_amount}")
                    print(f"   - التاريخ: {verify_invoice.date}")
                    print(f"   - الملاحظات: {verify_invoice.notes}")
                else:
                    print("❌ فشل في التحقق من الفاتورة")
                
            except Exception as e:
                print(f"❌ خطأ في إنشاء الفاتورة: {e}")
                db.session.rollback()
                import traceback
                traceback.print_exc()
            
            # 3. فحص الحقول المطلوبة
            print("\n🔍 فحص الحقول المطلوبة...")
            
            try:
                # فحص أعمدة جدول الفواتير
                from sqlalchemy import inspect
                inspector = inspect(db.engine)
                columns = inspector.get_columns('invoice')
                
                print("📋 أعمدة جدول الفواتير:")
                for column in columns:
                    nullable = "اختياري" if column['nullable'] else "مطلوب"
                    print(f"   - {column['name']}: {column['type']} ({nullable})")
                
            except Exception as e:
                print(f"❌ خطأ في فحص الأعمدة: {e}")
            
            # 4. فحص القيود والفهارس
            print("\n🔗 فحص القيود والفهارس...")
            
            try:
                # فحص المفاتيح الخارجية
                foreign_keys = inspector.get_foreign_keys('invoice')
                print("🔗 المفاتيح الخارجية:")
                for fk in foreign_keys:
                    print(f"   - {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}")
                
                # فحص الفهارس الفريدة
                indexes = inspector.get_indexes('invoice')
                print("📇 الفهارس:")
                for index in indexes:
                    unique = "فريد" if index['unique'] else "عادي"
                    print(f"   - {index['name']}: {index['column_names']} ({unique})")
                
            except Exception as e:
                print(f"❌ خطأ في فحص القيود: {e}")
            
        except Exception as e:
            print(f"❌ خطأ عام في التشخيص: {e}")
            import traceback
            traceback.print_exc()

def main():
    """الدالة الرئيسية"""
    print("🚀 تشخيص مشكلة إنشاء الفاتورة")
    print("=" * 50)
    
    debug_invoice_creation()
    
    print("=" * 50)
    print("✅ انتهى التشخيص!")

if __name__ == "__main__":
    main()
