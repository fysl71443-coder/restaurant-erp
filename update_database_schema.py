#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
تحديث مخطط قاعدة البيانات للحقول الجديدة
Database Schema Update for New Fields
"""

from flask import Flask
from database import db, init_db, Invoice, Payment, Customer, Supplier
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///accounting_system.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

def backup_database():
    """إنشاء نسخة احتياطية من قاعدة البيانات"""
    if os.path.exists('accounting_system.db'):
        backup_name = f'accounting_system_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'
        os.system(f'copy accounting_system.db {backup_name}')
        print(f"✅ تم إنشاء نسخة احتياطية: {backup_name}")
        return True
    return False

def check_column_exists(table_name, column_name):
    """فحص وجود عمود في الجدول"""
    try:
        conn = sqlite3.connect('accounting_system.db')
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [column[1] for column in cursor.fetchall()]
        conn.close()
        return column_name in columns
    except Exception as e:
        print(f"خطأ في فحص العمود {column_name}: {e}")
        return False

def add_missing_columns():
    """إضافة الأعمدة المفقودة"""
    try:
        conn = sqlite3.connect('accounting_system.db')
        cursor = conn.cursor()
        
        # فحص وإضافة الأعمدة للفواتير
        if not check_column_exists('invoice', 'invoice_number'):
            print("إضافة عمود invoice_number للفواتير...")
            cursor.execute('ALTER TABLE invoice ADD COLUMN invoice_number VARCHAR(50)')
            
            # تحديث الفواتير الموجودة برقم فاتورة تلقائي
            cursor.execute('SELECT id FROM invoice')
            invoices = cursor.fetchall()
            for invoice in invoices:
                invoice_number = f"INV-{invoice[0]:06d}"
                cursor.execute('UPDATE invoice SET invoice_number = ? WHERE id = ?', 
                             (invoice_number, invoice[0]))
            
            # إضافة قيد الفريد
            cursor.execute('CREATE UNIQUE INDEX IF NOT EXISTS idx_invoice_number ON invoice(invoice_number)')
            print("✅ تم إضافة عمود invoice_number")
        
        if not check_column_exists('invoice', 'customer_id'):
            print("إضافة عمود customer_id للفواتير...")
            cursor.execute('ALTER TABLE invoice ADD COLUMN customer_id INTEGER')
            
            # ربط الفواتير بالعملاء الموجودين
            cursor.execute('SELECT id, customer_name FROM invoice')
            invoices = cursor.fetchall()
            for invoice in invoices:
                # البحث عن العميل أو إنشاؤه
                cursor.execute('SELECT id FROM customer WHERE name = ?', (invoice[1],))
                customer = cursor.fetchone()
                if customer:
                    customer_id = customer[0]
                else:
                    # إنشاء عميل جديد
                    cursor.execute('INSERT INTO customer (name) VALUES (?)', (invoice[1],))
                    customer_id = cursor.lastrowid
                
                cursor.execute('UPDATE invoice SET customer_id = ? WHERE id = ?', 
                             (customer_id, invoice[0]))
            print("✅ تم إضافة عمود customer_id")
        
        # فحص وإضافة الأعمدة للمدفوعات
        if not check_column_exists('payment', 'payment_reference'):
            print("إضافة عمود payment_reference للمدفوعات...")
            cursor.execute('ALTER TABLE payment ADD COLUMN payment_reference VARCHAR(50)')
            
            # تحديث المدفوعات الموجودة برقم مرجع تلقائي
            cursor.execute('SELECT id FROM payment')
            payments = cursor.fetchall()
            for payment in payments:
                payment_ref = f"PAY-{payment[0]:06d}"
                cursor.execute('UPDATE payment SET payment_reference = ? WHERE id = ?', 
                             (payment_ref, payment[0]))
            
            # إضافة قيد الفريد
            cursor.execute('CREATE UNIQUE INDEX IF NOT EXISTS idx_payment_reference ON payment(payment_reference)')
            print("✅ تم إضافة عمود payment_reference")
        
        conn.commit()
        conn.close()
        print("✅ تم تحديث مخطط قاعدة البيانات بنجاح")
        return True
        
    except Exception as e:
        print(f"❌ خطأ في تحديث قاعدة البيانات: {e}")
        return False

def verify_schema():
    """التحقق من صحة المخطط المحدث"""
    try:
        with app.app_context():
            init_db(app)
            
            # فحص الجداول
            tables = ['invoice', 'payment', 'customer', 'supplier']
            for table in tables:
                result = db.engine.execute(f"SELECT COUNT(*) FROM {table}")
                count = result.fetchone()[0]
                print(f"✅ جدول {table}: {count} سجل")
            
            # فحص الفهارس
            result = db.engine.execute("SELECT name FROM sqlite_master WHERE type='index'")
            indexes = [row[0] for row in result.fetchall()]
            
            required_indexes = ['idx_invoice_number', 'idx_payment_reference']
            for index in required_indexes:
                if index in indexes:
                    print(f"✅ فهرس {index}: موجود")
                else:
                    print(f"⚠️ فهرس {index}: مفقود")
            
            return True
            
    except Exception as e:
        print(f"❌ خطأ في التحقق من المخطط: {e}")
        return False

def add_sample_data():
    """إضافة بيانات تجريبية للاختبار"""
    try:
        with app.app_context():
            # التحقق من وجود بيانات
            if Customer.query.count() == 0:
                print("إضافة عملاء تجريبيين...")
                customers = [
                    Customer(name="أحمد محمد", email="ahmed@example.com", phone="0501234567"),
                    Customer(name="فاطمة علي", email="fatima@example.com", phone="0509876543"),
                    Customer(name="محمد سعد", email="mohammed@example.com", phone="0505555555")
                ]
                for customer in customers:
                    db.session.add(customer)
                db.session.commit()
                print("✅ تم إضافة العملاء التجريبيين")
            
            if Supplier.query.count() == 0:
                print("إضافة موردين تجريبيين...")
                suppliers = [
                    Supplier(name="شركة التوريدات المتقدمة", contact_info="info@advanced.com - 0112345678"),
                    Supplier(name="مؤسسة الجودة التجارية", contact_info="sales@quality.com - 0113456789"),
                    Supplier(name="مكتب الخدمات الشاملة", contact_info="office@services.com - 0114567890")
                ]
                for supplier in suppliers:
                    db.session.add(supplier)
                db.session.commit()
                print("✅ تم إضافة الموردين التجريبيين")
            
            return True
            
    except Exception as e:
        print(f"❌ خطأ في إضافة البيانات التجريبية: {e}")
        return False

def main():
    """تشغيل عملية التحديث"""
    print("🔄 بدء تحديث مخطط قاعدة البيانات...")
    print("="*50)
    
    # إنشاء نسخة احتياطية
    if backup_database():
        print("✅ تم إنشاء نسخة احتياطية")
    else:
        print("⚠️ لم يتم العثور على قاعدة بيانات موجودة")
    
    # تحديث المخطط
    if add_missing_columns():
        print("✅ تم تحديث المخطط")
    else:
        print("❌ فشل في تحديث المخطط")
        return
    
    # التحقق من المخطط
    if verify_schema():
        print("✅ تم التحقق من المخطط")
    else:
        print("❌ فشل في التحقق من المخطط")
        return
    
    # إضافة بيانات تجريبية
    if add_sample_data():
        print("✅ تم إضافة البيانات التجريبية")
    else:
        print("❌ فشل في إضافة البيانات التجريبية")
    
    print("\n🎉 تم تحديث قاعدة البيانات بنجاح!")
    print("يمكنك الآن تشغيل التطبيق باستخدام: python app.py")

if __name__ == "__main__":
    main()
