#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
إصلاح جدول فواتير المشتريات
Fix Purchase Invoice Table
"""

from app import app
from database import db, PurchaseInvoice
from sqlalchemy import text
import sqlite3

def check_purchase_invoice_table():
    """فحص جدول فواتير المشتريات"""
    print("🔍 فحص جدول فواتير المشتريات...")
    print("="*50)
    
    try:
        with app.app_context():
            # فحص الأعمدة الموجودة
            result = db.session.execute(text("PRAGMA table_info(purchase_invoice)")).fetchall()
            
            existing_columns = [row[1] for row in result]
            print(f"📋 الأعمدة الموجودة: {existing_columns}")
            
            # الأعمدة المطلوبة
            required_columns = [
                'id', 'date', 'supplier_name', 'total_amount', 'status',
                'subtotal', 'tax_amount', 'discount', 'notes', 
                'invoice_number', 'supplier_id', 'created_at'
            ]
            
            missing_columns = []
            for col in required_columns:
                if col in existing_columns:
                    print(f"  ✅ {col}")
                else:
                    print(f"  ❌ {col} - مفقود")
                    missing_columns.append(col)
            
            return missing_columns
            
    except Exception as e:
        print(f"❌ خطأ في فحص الجدول: {e}")
        return None

def add_missing_columns(missing_columns):
    """إضافة الأعمدة المفقودة"""
    print(f"\n🔧 إضافة الأعمدة المفقودة: {missing_columns}")
    print("="*50)
    
    try:
        with app.app_context():
            # تعريف الأعمدة المفقودة مع أنواعها
            column_definitions = {
                'invoice_number': 'VARCHAR(50)',
                'supplier_id': 'INTEGER',
                'created_at': 'DATETIME'
            }
            
            for column in missing_columns:
                if column in column_definitions:
                    column_type = column_definitions[column]
                    sql = f"ALTER TABLE purchase_invoice ADD COLUMN {column} {column_type}"
                    
                    try:
                        db.session.execute(text(sql))
                        print(f"✅ تم إضافة العمود: {column}")
                    except Exception as e:
                        print(f"❌ فشل في إضافة العمود {column}: {e}")
            
            db.session.commit()
            print("✅ تم حفظ التغييرات")
            return True
            
    except Exception as e:
        print(f"❌ خطأ في إضافة الأعمدة: {e}")
        db.session.rollback()
        return False

def update_existing_records():
    """تحديث السجلات الموجودة"""
    print("\n🔄 تحديث السجلات الموجودة...")
    print("="*50)
    
    try:
        with app.app_context():
            # فحص عدد السجلات
            count = db.session.execute(text("SELECT COUNT(*) FROM purchase_invoice")).scalar()
            print(f"📊 عدد السجلات: {count}")
            
            if count > 0:
                # تحديث أرقام الفواتير المفقودة
                records = db.session.execute(text(
                    "SELECT id FROM purchase_invoice WHERE invoice_number IS NULL OR invoice_number = ''"
                )).fetchall()
                
                for i, record in enumerate(records, 1):
                    invoice_number = f"PURCH-{record[0]:06d}"
                    db.session.execute(text(
                        "UPDATE purchase_invoice SET invoice_number = :invoice_number WHERE id = :id"
                    ), {"invoice_number": invoice_number, "id": record[0]})
                    print(f"✅ تحديث الفاتورة {record[0]} -> {invoice_number}")
                
                # تحديث تواريخ الإنشاء المفقودة
                db.session.execute(text(
                    "UPDATE purchase_invoice SET created_at = date WHERE created_at IS NULL"
                ))
                
                db.session.commit()
                print("✅ تم تحديث جميع السجلات")
            else:
                print("ℹ️ لا توجد سجلات للتحديث")
            
            return True
            
    except Exception as e:
        print(f"❌ خطأ في تحديث السجلات: {e}")
        db.session.rollback()
        return False

def test_purchase_invoice_operations():
    """اختبار عمليات فواتير المشتريات"""
    print("\n🧪 اختبار عمليات فواتير المشتريات...")
    print("="*50)
    
    try:
        with app.app_context():
            # اختبار العد
            count = PurchaseInvoice.query.count()
            print(f"✅ عدد فواتير المشتريات: {count}")
            
            # اختبار إنشاء فاتورة جديدة
            test_invoice = PurchaseInvoice(
                supplier_name="مورد تجريبي",
                total_amount=1000.0,
                subtotal=900.0,
                tax_amount=100.0,
                discount=0.0,
                invoice_number="TEST-001",
                notes="فاتورة اختبار"
            )
            
            db.session.add(test_invoice)
            db.session.commit()
            print("✅ تم إنشاء فاتورة اختبار")
            
            # حذف فاتورة الاختبار
            db.session.delete(test_invoice)
            db.session.commit()
            print("✅ تم حذف فاتورة الاختبار")
            
            return True
            
    except Exception as e:
        print(f"❌ خطأ في الاختبار: {e}")
        db.session.rollback()
        return False

def create_indexes():
    """إنشاء الفهارس المطلوبة"""
    print("\n📇 إنشاء الفهارس...")
    print("="*50)
    
    try:
        with app.app_context():
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_purchase_invoice_number ON purchase_invoice(invoice_number)",
                "CREATE INDEX IF NOT EXISTS idx_purchase_invoice_supplier ON purchase_invoice(supplier_name)",
                "CREATE INDEX IF NOT EXISTS idx_purchase_invoice_date ON purchase_invoice(date)",
                "CREATE INDEX IF NOT EXISTS idx_purchase_invoice_status ON purchase_invoice(status)",
                "CREATE INDEX IF NOT EXISTS idx_purchase_invoice_amount ON purchase_invoice(total_amount)"
            ]
            
            for index_sql in indexes:
                try:
                    db.session.execute(text(index_sql))
                    index_name = index_sql.split()[5]  # استخراج اسم الفهرس
                    print(f"✅ تم إنشاء الفهرس: {index_name}")
                except Exception as e:
                    print(f"❌ فشل في إنشاء فهرس: {e}")
            
            db.session.commit()
            print("✅ تم إنشاء جميع الفهارس")
            return True
            
    except Exception as e:
        print(f"❌ خطأ في إنشاء الفهارس: {e}")
        return False

def main():
    """تشغيل إصلاح جدول فواتير المشتريات"""
    print("🔧 إصلاح جدول فواتير المشتريات")
    print("="*60)
    
    # فحص الجدول
    missing_columns = check_purchase_invoice_table()
    
    if missing_columns is None:
        print("❌ فشل في فحص الجدول")
        return
    
    # إضافة الأعمدة المفقودة
    if missing_columns:
        if not add_missing_columns(missing_columns):
            print("❌ فشل في إضافة الأعمدة المفقودة")
            return
    else:
        print("✅ جميع الأعمدة موجودة")
    
    # تحديث السجلات الموجودة
    if not update_existing_records():
        print("❌ فشل في تحديث السجلات")
        return
    
    # إنشاء الفهارس
    if not create_indexes():
        print("❌ فشل في إنشاء الفهارس")
        return
    
    # اختبار العمليات
    if not test_purchase_invoice_operations():
        print("❌ فشل في اختبار العمليات")
        return
    
    print("\n🎉 تم إصلاح جدول فواتير المشتريات بنجاح!")
    print("✅ الجدول جاهز للاستخدام")

if __name__ == "__main__":
    main()
