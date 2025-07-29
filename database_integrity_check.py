#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
فحص سلامة قاعدة البيانات
Database Integrity Check
"""

from app import app
from database import db, Customer, Invoice, Supplier, Product, Expense, Employee, Attendance, Payroll, Leave, PurchaseInvoice, Payment, User, SystemSettings
from sqlalchemy import inspect, text
import sqlite3
import os

def check_database_file():
    """فحص ملف قاعدة البيانات"""
    print("📁 فحص ملف قاعدة البيانات...")
    print("="*50)
    
    db_files = ['accounting_system.db', 'accounting.db', 'instance/accounting_system.db']
    found_files = []
    
    for db_file in db_files:
        if os.path.exists(db_file):
            size = os.path.getsize(db_file)
            print(f"✅ {db_file} - الحجم: {size:,} بايت")
            found_files.append(db_file)
        else:
            print(f"❌ {db_file} - غير موجود")
    
    if not found_files:
        print("⚠️ لم يتم العثور على أي ملف قاعدة بيانات")
        return False
    
    return True

def check_database_connection():
    """فحص الاتصال بقاعدة البيانات"""
    print("\n🔗 فحص الاتصال بقاعدة البيانات...")
    print("="*50)
    
    try:
        with app.app_context():
            # اختبار الاتصال
            result = db.session.execute(text("SELECT 1")).fetchone()
            if result:
                print("✅ الاتصال بقاعدة البيانات يعمل")
                return True
            else:
                print("❌ فشل في الاتصال بقاعدة البيانات")
                return False
    except Exception as e:
        print(f"❌ خطأ في الاتصال: {e}")
        return False

def check_tables_structure():
    """فحص هيكل الجداول"""
    print("\n🏗️ فحص هيكل الجداول...")
    print("="*50)
    
    try:
        with app.app_context():
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            print(f"📊 عدد الجداول: {len(tables)}")
            
            # الجداول المطلوبة
            required_tables = [
                'users', 'customer', 'invoice', 'supplier', 'product', 
                'expense', 'employee', 'attendance', 'payroll', 'leave', 
                'purchase_invoice', 'payment', 'system_settings'
            ]
            
            missing_tables = []
            existing_tables = []
            
            for table in required_tables:
                if table in tables:
                    existing_tables.append(table)
                    print(f"✅ {table}")
                else:
                    missing_tables.append(table)
                    print(f"❌ {table} - مفقود")
            
            print(f"\n📈 الجداول الموجودة: {len(existing_tables)}/{len(required_tables)}")
            
            if missing_tables:
                print(f"⚠️ الجداول المفقودة: {missing_tables}")
                return False
            
            return True
            
    except Exception as e:
        print(f"❌ خطأ في فحص الجداول: {e}")
        return False

def check_table_columns():
    """فحص أعمدة الجداول"""
    print("\n📋 فحص أعمدة الجداول...")
    print("="*50)
    
    try:
        with app.app_context():
            inspector = inspect(db.engine)
            
            # فحص جدول المستخدمين
            print("👤 جدول المستخدمين:")
            user_columns = inspector.get_columns('users')
            user_column_names = [col['name'] for col in user_columns]
            required_user_columns = ['id', 'username', 'email', 'password_hash', 'full_name', 'role']
            
            for col in required_user_columns:
                if col in user_column_names:
                    print(f"  ✅ {col}")
                else:
                    print(f"  ❌ {col} - مفقود")
            
            # فحص جدول الفواتير
            print("\n📄 جدول الفواتير:")
            invoice_columns = inspector.get_columns('invoice')
            invoice_column_names = [col['name'] for col in invoice_columns]
            required_invoice_columns = ['id', 'date', 'customer_name', 'total_amount', 'status']
            
            for col in required_invoice_columns:
                if col in invoice_column_names:
                    print(f"  ✅ {col}")
                else:
                    print(f"  ❌ {col} - مفقود")
            
            # فحص جدول المدفوعات
            print("\n💰 جدول المدفوعات:")
            payment_columns = inspector.get_columns('payment')
            payment_column_names = [col['name'] for col in payment_columns]
            required_payment_columns = ['id', 'date', 'amount', 'payment_method', 'payment_type']
            
            for col in required_payment_columns:
                if col in payment_column_names:
                    print(f"  ✅ {col}")
                else:
                    print(f"  ❌ {col} - مفقود")
            
            return True
            
    except Exception as e:
        print(f"❌ خطأ في فحص الأعمدة: {e}")
        return False

def check_foreign_keys():
    """فحص المفاتيح الخارجية"""
    print("\n🔗 فحص المفاتيح الخارجية...")
    print("="*50)
    
    try:
        with app.app_context():
            inspector = inspect(db.engine)
            
            # فحص العلاقات
            tables_with_fks = ['attendance', 'payroll', 'leave', 'payment']
            
            for table in tables_with_fks:
                if table in inspector.get_table_names():
                    fks = inspector.get_foreign_keys(table)
                    print(f"📊 {table}:")
                    if fks:
                        for fk in fks:
                            print(f"  ✅ {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}")
                    else:
                        print(f"  ⚠️ لا توجد مفاتيح خارجية")
            
            return True
            
    except Exception as e:
        print(f"❌ خطأ في فحص المفاتيح الخارجية: {e}")
        return False

def check_indexes():
    """فحص الفهارس"""
    print("\n📇 فحص الفهارس...")
    print("="*50)
    
    try:
        with app.app_context():
            inspector = inspect(db.engine)
            
            # فحص الفهارس المهمة
            important_tables = ['invoice', 'payment', 'employee', 'attendance']
            
            for table in important_tables:
                if table in inspector.get_table_names():
                    indexes = inspector.get_indexes(table)
                    print(f"📊 {table}:")
                    if indexes:
                        for idx in indexes:
                            unique = "فريد" if idx['unique'] else "عادي"
                            print(f"  ✅ {idx['name']}: {idx['column_names']} ({unique})")
                    else:
                        print(f"  ⚠️ لا توجد فهارس")
            
            return True
            
    except Exception as e:
        print(f"❌ خطأ في فحص الفهارس: {e}")
        return False

def check_data_integrity():
    """فحص سلامة البيانات"""
    print("\n🔍 فحص سلامة البيانات...")
    print("="*50)
    
    try:
        with app.app_context():
            # فحص عدد السجلات
            tables_models = {
                'المستخدمين': User,
                'العملاء': Customer,
                'الفواتير': Invoice,
                'الموردين': Supplier,
                'المنتجات': Product,
                'المصروفات': Expense,
                'الموظفين': Employee,
                'الحضور': Attendance,
                'الرواتب': Payroll,
                'الإجازات': Leave,
                'فواتير المشتريات': PurchaseInvoice,
                'المدفوعات': Payment
            }
            
            total_records = 0
            for name, model in tables_models.items():
                try:
                    count = model.query.count()
                    total_records += count
                    print(f"📊 {name}: {count:,} سجل")
                except Exception as e:
                    print(f"❌ {name}: خطأ في العد - {e}")
            
            print(f"\n📈 إجمالي السجلات: {total_records:,}")
            
            # فحص البيانات المرتبطة
            print("\n🔗 فحص الروابط:")
            
            # فحص المدفوعات المرتبطة بالفواتير
            payments_with_invoices = Payment.query.filter(Payment.invoice_id.isnot(None)).count()
            total_payments = Payment.query.count()
            print(f"💰 المدفوعات المرتبطة بفواتير: {payments_with_invoices}/{total_payments}")
            
            # فحص الحضور المرتبط بالموظفين
            attendance_records = Attendance.query.count()
            employees_count = Employee.query.count()
            print(f"👥 سجلات الحضور: {attendance_records} للموظفين: {employees_count}")
            
            return True
            
    except Exception as e:
        print(f"❌ خطأ في فحص البيانات: {e}")
        return False

def run_sqlite_integrity_check():
    """تشغيل فحص سلامة SQLite"""
    print("\n🔧 فحص سلامة SQLite...")
    print("="*50)
    
    try:
        with app.app_context():
            # فحص سلامة قاعدة البيانات
            result = db.session.execute(text("PRAGMA integrity_check")).fetchall()
            
            if result and result[0][0] == 'ok':
                print("✅ فحص السلامة: قاعدة البيانات سليمة")
            else:
                print("❌ فحص السلامة: توجد مشاكل")
                for row in result:
                    print(f"  ⚠️ {row[0]}")
            
            # فحص الإحصائيات
            stats = db.session.execute(text("PRAGMA database_list")).fetchall()
            for stat in stats:
                print(f"📊 قاعدة البيانات: {stat[1]} - الملف: {stat[2]}")
            
            return True
            
    except Exception as e:
        print(f"❌ خطأ في فحص SQLite: {e}")
        return False

def main():
    """تشغيل جميع فحوصات قاعدة البيانات"""
    print("🔍 فحص سلامة قاعدة البيانات الشامل")
    print("="*60)
    
    checks = [
        ("فحص ملف قاعدة البيانات", check_database_file),
        ("فحص الاتصال", check_database_connection),
        ("فحص هيكل الجداول", check_tables_structure),
        ("فحص أعمدة الجداول", check_table_columns),
        ("فحص المفاتيح الخارجية", check_foreign_keys),
        ("فحص الفهارس", check_indexes),
        ("فحص سلامة البيانات", check_data_integrity),
        ("فحص سلامة SQLite", run_sqlite_integrity_check)
    ]
    
    passed = 0
    total = len(checks)
    
    for name, check_func in checks:
        try:
            if check_func():
                passed += 1
                print(f"\n✅ {name}: نجح")
            else:
                print(f"\n❌ {name}: فشل")
        except Exception as e:
            print(f"\n❌ {name}: خطأ - {e}")
    
    print("\n" + "="*60)
    print(f"📊 نتائج الفحص: {passed}/{total} فحص نجح")
    print(f"📈 معدل النجاح: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("🎉 قاعدة البيانات سليمة تماماً!")
    elif passed >= total * 0.8:
        print("⚠️ قاعدة البيانات تحتاج بعض التحسينات")
    else:
        print("❌ قاعدة البيانات تحتاج إصلاح شامل")

if __name__ == "__main__":
    main()
