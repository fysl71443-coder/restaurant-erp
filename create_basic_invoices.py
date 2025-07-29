#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
إنشاء فواتير أساسية للاختبار
Create Basic Invoices for Testing
"""

import sqlite3
from datetime import datetime, timedelta
import random

def create_basic_invoices():
    """إنشاء فواتير أساسية مباشرة في قاعدة البيانات"""
    
    print("🔄 بدء إنشاء فواتير أساسية للاختبار...")
    
    try:
        # الاتصال بقاعدة البيانات
        conn = sqlite3.connect('accounting_system.db')
        cursor = conn.cursor()
        
        # التحقق من وجود العملاء
        cursor.execute("SELECT COUNT(*) FROM customer")
        customer_count = cursor.fetchone()[0]
        
        if customer_count == 0:
            print("⚠️ لا توجد عملاء في قاعدة البيانات")
            return
        
        # جلب العملاء
        cursor.execute("SELECT id, name FROM customer")
        customers = cursor.fetchall()
        
        print(f"👥 تم العثور على {len(customers)} عميل")
        
        # إنشاء فواتير مبيعات بسيطة
        print("🛍️ إنشاء فواتير المبيعات...")
        
        for i in range(8):
            customer = random.choice(customers)
            customer_id, customer_name = customer
            
            invoice_date = datetime.now() - timedelta(days=random.randint(1, 30))
            total_amount = random.uniform(1000, 10000)
            
            # إدراج فاتورة بسيطة
            cursor.execute("""
                INSERT INTO invoice (date, customer_name, total_amount)
                VALUES (?, ?, ?)
            """, (invoice_date, customer_name, round(total_amount, 2)))
        
        print("✅ تم إنشاء 8 فواتير مبيعات")
        
        # التحقق من وجود الموردين
        cursor.execute("SELECT COUNT(*) FROM supplier")
        supplier_count = cursor.fetchone()[0]
        
        if supplier_count > 0:
            # جلب الموردين
            cursor.execute("SELECT id, name FROM supplier")
            suppliers = cursor.fetchall()
            
            print(f"🏭 تم العثور على {len(suppliers)} مورد")
            
            # إنشاء فواتير مشتريات بسيطة
            print("🛒 إنشاء فواتير المشتريات...")
            
            for i in range(6):
                supplier = random.choice(suppliers)
                supplier_id, supplier_name = supplier
                
                invoice_date = datetime.now() - timedelta(days=random.randint(1, 30))
                total_amount = random.uniform(2000, 15000)
                
                # إدراج فاتورة مشتريات بسيطة
                cursor.execute("""
                    INSERT INTO purchase_invoice (date, supplier_name, total_amount)
                    VALUES (?, ?, ?)
                """, (invoice_date, supplier_name, round(total_amount, 2)))
            
            print("✅ تم إنشاء 6 فواتير مشتريات")
        else:
            print("⚠️ لا توجد موردين لإنشاء فواتير المشتريات")
        
        # إنشاء مدفوعات بسيطة
        print("💰 إنشاء المدفوعات...")
        
        for i in range(4):
            payment_date = datetime.now() - timedelta(days=random.randint(1, 20))
            amount = random.uniform(500, 5000)
            payment_method = random.choice(['cash', 'bank_transfer', 'check', 'card'])
            payment_type = random.choice(['received', 'paid'])
            
            # إدراج دفعة بسيطة
            cursor.execute("""
                INSERT INTO payment (date, amount, payment_method, payment_type)
                VALUES (?, ?, ?, ?)
            """, (payment_date, round(amount, 2), payment_method, payment_type))
        
        print("✅ تم إنشاء 4 مدفوعات")
        
        # حفظ التغييرات
        conn.commit()
        
        print("\n🎉 تم إنشاء جميع البيانات الأساسية بنجاح!")
        
        # عرض ملخص البيانات
        print("\n📊 ملخص البيانات المُنشأة:")
        
        cursor.execute("SELECT COUNT(*) FROM customer")
        print(f"👥 العملاء: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM supplier")
        print(f"🏭 الموردين: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM invoice")
        print(f"🛍️ فواتير المبيعات: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM purchase_invoice")
        print(f"🛒 فواتير المشتريات: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM payment")
        print(f"💰 المدفوعات: {cursor.fetchone()[0]}")
        
    except Exception as e:
        print(f"❌ خطأ في إنشاء البيانات: {str(e)}")
        if 'conn' in locals():
            conn.rollback()
    
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    create_basic_invoices()
