#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
إصلاح جدول الفواتير
Fix Invoice Table
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from database import Invoice, Customer
import sqlite3

def fix_invoice_table():
    """إصلاح جدول الفواتير"""
    print("🔧 إصلاح جدول الفواتير...")
    
    with app.app_context():
        try:
            # الحصول على مسار قاعدة البيانات
            db_path = 'accounting.db'
            
            # الاتصال المباشر بقاعدة البيانات
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            print("📊 فحص الأعمدة الحالية...")
            
            # فحص الأعمدة الموجودة
            cursor.execute("PRAGMA table_info(invoice)")
            columns = cursor.fetchall()
            
            existing_columns = [col[1] for col in columns]
            print(f"📋 الأعمدة الموجودة: {existing_columns}")
            
            # إضافة الأعمدة المفقودة
            missing_columns = []
            
            if 'invoice_number' not in existing_columns:
                missing_columns.append(('invoice_number', 'VARCHAR(50)'))
            
            if 'customer_id' not in existing_columns:
                missing_columns.append(('customer_id', 'INTEGER'))
            
            if missing_columns:
                print(f"➕ إضافة الأعمدة المفقودة: {[col[0] for col in missing_columns]}")
                
                for column_name, column_type in missing_columns:
                    try:
                        cursor.execute(f"ALTER TABLE invoice ADD COLUMN {column_name} {column_type}")
                        print(f"✅ تم إضافة العمود: {column_name}")
                    except sqlite3.OperationalError as e:
                        if "duplicate column name" in str(e):
                            print(f"⚠️ العمود {column_name} موجود بالفعل")
                        else:
                            print(f"❌ خطأ في إضافة العمود {column_name}: {e}")
                
                conn.commit()
            else:
                print("✅ جميع الأعمدة موجودة")
            
            # تحديث البيانات الموجودة
            print("\n🔄 تحديث البيانات الموجودة...")
            
            # إضافة أرقام فواتير للفواتير الموجودة
            cursor.execute("SELECT id FROM invoice WHERE invoice_number IS NULL OR invoice_number = ''")
            invoices_without_numbers = cursor.fetchall()
            
            if invoices_without_numbers:
                print(f"📝 تحديث {len(invoices_without_numbers)} فاتورة بدون أرقام...")
                
                for i, (invoice_id,) in enumerate(invoices_without_numbers, 1):
                    invoice_number = f"INV-{invoice_id:06d}"
                    cursor.execute("UPDATE invoice SET invoice_number = ? WHERE id = ?", 
                                 (invoice_number, invoice_id))
                    print(f"✅ تحديث الفاتورة {invoice_id} -> {invoice_number}")
                
                conn.commit()
            
            # ربط الفواتير بالعملاء
            cursor.execute("SELECT id, customer_name FROM invoice WHERE customer_id IS NULL")
            invoices_without_customers = cursor.fetchall()
            
            if invoices_without_customers:
                print(f"👥 ربط {len(invoices_without_customers)} فاتورة بالعملاء...")
                
                for invoice_id, customer_name in invoices_without_customers:
                    # البحث عن العميل أو إنشاؤه
                    with app.app_context():
                        customer = Customer.query.filter_by(name=customer_name).first()
                        if not customer:
                            customer = Customer(name=customer_name)
                            db.session.add(customer)
                            db.session.commit()
                            print(f"➕ تم إنشاء عميل جديد: {customer_name} (ID: {customer.id})")
                        
                        # ربط الفاتورة بالعميل
                        cursor.execute("UPDATE invoice SET customer_id = ? WHERE id = ?", 
                                     (customer.id, invoice_id))
                        print(f"🔗 ربط الفاتورة {invoice_id} بالعميل {customer.id}")
                
                conn.commit()
            
            # إنشاء الفهارس المطلوبة
            print("\n📇 إنشاء الفهارس...")
            
            indexes_to_create = [
                ("idx_invoice_number", "CREATE UNIQUE INDEX IF NOT EXISTS idx_invoice_number ON invoice(invoice_number)"),
                ("idx_invoice_customer_id", "CREATE INDEX IF NOT EXISTS idx_invoice_customer_id ON invoice(customer_id)"),
                ("idx_invoice_date_status", "CREATE INDEX IF NOT EXISTS idx_invoice_date_status ON invoice(date, status)"),
                ("idx_invoice_customer_date", "CREATE INDEX IF NOT EXISTS idx_invoice_customer_date ON invoice(customer_id, date)"),
                ("idx_invoice_type_date", "CREATE INDEX IF NOT EXISTS idx_invoice_type_date ON invoice(invoice_type, date)"),
                ("idx_invoice_amount_date", "CREATE INDEX IF NOT EXISTS idx_invoice_amount_date ON invoice(total_amount, date)")
            ]
            
            for index_name, index_sql in indexes_to_create:
                try:
                    cursor.execute(index_sql)
                    print(f"✅ تم إنشاء الفهرس: {index_name}")
                except sqlite3.OperationalError as e:
                    if "already exists" in str(e):
                        print(f"⚠️ الفهرس {index_name} موجود بالفعل")
                    else:
                        print(f"❌ خطأ في إنشاء الفهرس {index_name}: {e}")
            
            conn.commit()
            conn.close()
            
            # التحقق من الإصلاح
            print("\n✅ التحقق من الإصلاح...")
            
            with app.app_context():
                try:
                    # اختبار إنشاء فاتورة جديدة
                    test_customer_name = "عميل اختبار الإصلاح"
                    
                    # البحث عن العميل أو إنشاؤه
                    customer = Customer.query.filter_by(name=test_customer_name).first()
                    if not customer:
                        customer = Customer(name=test_customer_name)
                        db.session.add(customer)
                        db.session.flush()
                    
                    # إنشاء رقم فاتورة
                    last_invoice = Invoice.query.order_by(Invoice.id.desc()).first()
                    invoice_number = f"INV-{(last_invoice.id + 1) if last_invoice else 1:06d}"
                    
                    # إنشاء الفاتورة
                    test_invoice = Invoice(
                        customer_id=customer.id,
                        customer_name=test_customer_name,
                        invoice_number=invoice_number,
                        total_amount=999.99,
                        subtotal=999.99,
                        notes="فاتورة اختبار الإصلاح"
                    )
                    
                    db.session.add(test_invoice)
                    db.session.commit()
                    
                    print(f"✅ تم إنشاء فاتورة اختبار بنجاح! رقم الفاتورة: {test_invoice.invoice_number}")
                    
                    # حذف فاتورة الاختبار
                    db.session.delete(test_invoice)
                    db.session.commit()
                    print("🗑️ تم حذف فاتورة الاختبار")
                    
                except Exception as e:
                    print(f"❌ فشل في اختبار الإصلاح: {e}")
                    db.session.rollback()
            
            print("\n🎉 تم إصلاح جدول الفواتير بنجاح!")
            
        except Exception as e:
            print(f"❌ خطأ في إصلاح الجدول: {e}")
            import traceback
            traceback.print_exc()

def main():
    """الدالة الرئيسية"""
    print("🚀 إصلاح جدول الفواتير")
    print("=" * 50)
    
    fix_invoice_table()
    
    print("=" * 50)
    print("✅ انتهى الإصلاح!")

if __name__ == "__main__":
    main()
