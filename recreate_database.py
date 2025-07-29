#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
إعادة إنشاء قاعدة البيانات
Recreate Database
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from database import *
import sqlite3

def recreate_database():
    """إعادة إنشاء قاعدة البيانات"""
    print("🔧 إعادة إنشاء قاعدة البيانات...")
    
    with app.app_context():
        try:
            # فحص الجداول الموجودة
            print("📊 فحص الجداول الموجودة...")
            
            db_path = 'accounting.db'
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # الحصول على قائمة الجداول
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            existing_tables = [table[0] for table in cursor.fetchall()]
            print(f"📋 الجداول الموجودة: {existing_tables}")
            
            conn.close()
            
            # إنشاء جميع الجداول
            print("\n🏗️ إنشاء جميع الجداول...")
            db.create_all()
            print("✅ تم إنشاء جميع الجداول")
            
            # التحقق من الجداول الجديدة
            print("\n✅ التحقق من الجداول الجديدة...")
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            new_tables = [table[0] for table in cursor.fetchall()]
            print(f"📋 الجداول الجديدة: {new_tables}")
            
            # فحص جدول الفواتير
            if 'invoice' in new_tables:
                print("\n📋 فحص جدول الفواتير...")
                cursor.execute("PRAGMA table_info(invoice)")
                columns = cursor.fetchall()
                
                print("📝 أعمدة جدول الفواتير:")
                for col in columns:
                    nullable = "اختياري" if col[3] == 0 else "مطلوب"
                    print(f"   - {col[1]}: {col[2]} ({nullable})")
            
            conn.close()
            
            # إنشاء بيانات تجريبية
            print("\n📝 إنشاء بيانات تجريبية...")
            
            # إنشاء عملاء تجريبيين
            customers_data = [
                "شركة الأمل للتجارة",
                "مؤسسة النور للخدمات",
                "شركة الفجر للمقاولات",
                "مكتب الرياض للاستشارات",
                "شركة الخليج للتطوير"
            ]
            
            for customer_name in customers_data:
                existing_customer = Customer.query.filter_by(name=customer_name).first()
                if not existing_customer:
                    customer = Customer(name=customer_name)
                    db.session.add(customer)
                    print(f"➕ تم إضافة العميل: {customer_name}")
            
            db.session.commit()
            
            # إنشاء فواتير تجريبية
            print("\n📄 إنشاء فواتير تجريبية...")
            
            customers = Customer.query.all()
            if customers:
                for i, customer in enumerate(customers[:3], 1):
                    invoice_number = f"INV-{i:06d}"
                    
                    invoice = Invoice(
                        customer_id=customer.id,
                        customer_name=customer.name,
                        invoice_number=invoice_number,
                        total_amount=1000.0 * i,
                        subtotal=1000.0 * i,
                        notes=f"فاتورة تجريبية رقم {i}"
                    )
                    
                    db.session.add(invoice)
                    print(f"📄 تم إضافة الفاتورة: {invoice_number} للعميل {customer.name}")
                
                db.session.commit()
            
            # اختبار إنشاء فاتورة جديدة
            print("\n🧪 اختبار إنشاء فاتورة جديدة...")
            
            test_customer = customers[0] if customers else None
            if test_customer:
                # إنشاء رقم فاتورة
                last_invoice = Invoice.query.order_by(Invoice.id.desc()).first()
                invoice_number = f"INV-{(last_invoice.id + 1) if last_invoice else 1:06d}"
                
                test_invoice = Invoice(
                    customer_id=test_customer.id,
                    customer_name=test_customer.name,
                    invoice_number=invoice_number,
                    total_amount=1500.00,
                    subtotal=1500.00,
                    notes="فاتورة اختبار النظام"
                )
                
                db.session.add(test_invoice)
                db.session.commit()
                
                print(f"✅ تم إنشاء فاتورة اختبار: {test_invoice.invoice_number}")
                
                # التحقق من الفاتورة
                verify_invoice = Invoice.query.get(test_invoice.id)
                if verify_invoice:
                    print(f"✅ تم التحقق من الفاتورة: {verify_invoice.invoice_number}")
                    print(f"   - العميل: {verify_invoice.customer_name}")
                    print(f"   - المبلغ: {verify_invoice.total_amount}")
                    print(f"   - معرف العميل: {verify_invoice.customer_id}")
                
                # حذف فاتورة الاختبار
                db.session.delete(test_invoice)
                db.session.commit()
                print("🗑️ تم حذف فاتورة الاختبار")
            
            print("\n🎉 تم إعادة إنشاء قاعدة البيانات بنجاح!")
            
            # إحصائيات نهائية
            print("\n📊 إحصائيات قاعدة البيانات:")
            print(f"👥 العملاء: {Customer.query.count()}")
            print(f"📄 الفواتير: {Invoice.query.count()}")
            print(f"💰 المدفوعات: {Payment.query.count()}")
            
        except Exception as e:
            print(f"❌ خطأ في إعادة إنشاء قاعدة البيانات: {e}")
            import traceback
            traceback.print_exc()
            db.session.rollback()

def main():
    """الدالة الرئيسية"""
    print("🚀 إعادة إنشاء قاعدة البيانات")
    print("=" * 50)
    
    recreate_database()
    
    print("=" * 50)
    print("✅ انتهى إعادة الإنشاء!")

if __name__ == "__main__":
    main()
