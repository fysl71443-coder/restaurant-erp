#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
إضافة الفهارس لتحسين أداء قاعدة البيانات
Add Database Indexes for Performance
"""

from app import app
from database import db
from sqlalchemy import text

def create_invoice_indexes():
    """إنشاء فهارس جدول الفواتير"""
    print("📄 إنشاء فهارس جدول الفواتير...")
    
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_invoice_date ON invoice(date)",
        "CREATE INDEX IF NOT EXISTS idx_invoice_customer ON invoice(customer_name)",
        "CREATE INDEX IF NOT EXISTS idx_invoice_status ON invoice(status)",
        "CREATE INDEX IF NOT EXISTS idx_invoice_amount ON invoice(total_amount)",
        "CREATE INDEX IF NOT EXISTS idx_invoice_type ON invoice(invoice_type)",
        "CREATE INDEX IF NOT EXISTS idx_invoice_customer_date ON invoice(customer_name, date)"
    ]
    
    success_count = 0
    for index_sql in indexes:
        try:
            db.session.execute(text(index_sql))
            index_name = index_sql.split()[5]
            print(f"  ✅ {index_name}")
            success_count += 1
        except Exception as e:
            print(f"  ❌ فشل في إنشاء فهرس: {e}")
    
    return success_count

def create_payment_indexes():
    """إنشاء فهارس جدول المدفوعات"""
    print("\n💰 إنشاء فهارس جدول المدفوعات...")
    
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_payment_date ON payment(date)",
        "CREATE INDEX IF NOT EXISTS idx_payment_method ON payment(payment_method)",
        "CREATE INDEX IF NOT EXISTS idx_payment_type ON payment(payment_type)",
        "CREATE INDEX IF NOT EXISTS idx_payment_amount ON payment(amount)",
        "CREATE INDEX IF NOT EXISTS idx_payment_invoice ON payment(invoice_id)",
        "CREATE INDEX IF NOT EXISTS idx_payment_reference ON payment(reference_number)",
        "CREATE INDEX IF NOT EXISTS idx_payment_type_date ON payment(payment_type, date)"
    ]
    
    success_count = 0
    for index_sql in indexes:
        try:
            db.session.execute(text(index_sql))
            index_name = index_sql.split()[5]
            print(f"  ✅ {index_name}")
            success_count += 1
        except Exception as e:
            print(f"  ❌ فشل في إنشاء فهرس: {e}")
    
    return success_count

def create_employee_indexes():
    """إنشاء فهارس جدول الموظفين"""
    print("\n👥 إنشاء فهارس جدول الموظفين...")
    
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_employee_name ON employee(name)",
        "CREATE INDEX IF NOT EXISTS idx_employee_id_unique ON employee(employee_id)",
        "CREATE INDEX IF NOT EXISTS idx_employee_department ON employee(department)",
        "CREATE INDEX IF NOT EXISTS idx_employee_position ON employee(position)",
        "CREATE INDEX IF NOT EXISTS idx_employee_status ON employee(status)",
        "CREATE INDEX IF NOT EXISTS idx_employee_hire_date ON employee(hire_date)",
        "CREATE INDEX IF NOT EXISTS idx_employee_salary ON employee(salary)",
        "CREATE INDEX IF NOT EXISTS idx_employee_dept_status ON employee(department, status)"
    ]
    
    success_count = 0
    for index_sql in indexes:
        try:
            db.session.execute(text(index_sql))
            index_name = index_sql.split()[5]
            print(f"  ✅ {index_name}")
            success_count += 1
        except Exception as e:
            print(f"  ❌ فشل في إنشاء فهرس: {e}")
    
    return success_count

def create_attendance_indexes():
    """إنشاء فهارس جدول الحضور"""
    print("\n⏰ إنشاء فهارس جدول الحضور...")
    
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_attendance_employee ON attendance(employee_id)",
        "CREATE INDEX IF NOT EXISTS idx_attendance_date ON attendance(date)",
        "CREATE INDEX IF NOT EXISTS idx_attendance_status ON attendance(status)",
        "CREATE INDEX IF NOT EXISTS idx_attendance_hours ON attendance(total_hours)",
        "CREATE INDEX IF NOT EXISTS idx_attendance_overtime ON attendance(overtime_hours)",
        "CREATE INDEX IF NOT EXISTS idx_attendance_emp_date ON attendance(employee_id, date)",
        "CREATE INDEX IF NOT EXISTS idx_attendance_date_status ON attendance(date, status)"
    ]
    
    success_count = 0
    for index_sql in indexes:
        try:
            db.session.execute(text(index_sql))
            index_name = index_sql.split()[5]
            print(f"  ✅ {index_name}")
            success_count += 1
        except Exception as e:
            print(f"  ❌ فشل في إنشاء فهرس: {e}")
    
    return success_count

def create_customer_indexes():
    """إنشاء فهارس جدول العملاء"""
    print("\n👤 إنشاء فهارس جدول العملاء...")
    
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_customer_name ON customer(name)",
        "CREATE INDEX IF NOT EXISTS idx_customer_email ON customer(email)",
        "CREATE INDEX IF NOT EXISTS idx_customer_phone ON customer(phone)"
    ]
    
    success_count = 0
    for index_sql in indexes:
        try:
            db.session.execute(text(index_sql))
            index_name = index_sql.split()[5]
            print(f"  ✅ {index_name}")
            success_count += 1
        except Exception as e:
            print(f"  ❌ فشل في إنشاء فهرس: {e}")
    
    return success_count

def create_product_indexes():
    """إنشاء فهارس جدول المنتجات"""
    print("\n📦 إنشاء فهارس جدول المنتجات...")
    
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_product_name ON product(name)",
        "CREATE INDEX IF NOT EXISTS idx_product_quantity ON product(quantity)",
        "CREATE INDEX IF NOT EXISTS idx_product_price ON product(price)"
    ]
    
    success_count = 0
    for index_sql in indexes:
        try:
            db.session.execute(text(index_sql))
            index_name = index_sql.split()[5]
            print(f"  ✅ {index_name}")
            success_count += 1
        except Exception as e:
            print(f"  ❌ فشل في إنشاء فهرس: {e}")
    
    return success_count

def create_expense_indexes():
    """إنشاء فهارس جدول المصروفات"""
    print("\n💸 إنشاء فهارس جدول المصروفات...")
    
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_expense_date ON expense(date)",
        "CREATE INDEX IF NOT EXISTS idx_expense_amount ON expense(amount)",
        "CREATE INDEX IF NOT EXISTS idx_expense_description ON expense(description)"
    ]
    
    success_count = 0
    for index_sql in indexes:
        try:
            db.session.execute(text(index_sql))
            index_name = index_sql.split()[5]
            print(f"  ✅ {index_name}")
            success_count += 1
        except Exception as e:
            print(f"  ❌ فشل في إنشاء فهرس: {e}")
    
    return success_count

def create_payroll_indexes():
    """إنشاء فهارس جدول الرواتب"""
    print("\n💰 إنشاء فهارس جدول الرواتب...")
    
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_payroll_employee ON payroll(employee_id)",
        "CREATE INDEX IF NOT EXISTS idx_payroll_month_year ON payroll(month, year)",
        "CREATE INDEX IF NOT EXISTS idx_payroll_status ON payroll(status)",
        "CREATE INDEX IF NOT EXISTS idx_payroll_payment_date ON payroll(payment_date)",
        "CREATE INDEX IF NOT EXISTS idx_payroll_net_salary ON payroll(net_salary)"
    ]
    
    success_count = 0
    for index_sql in indexes:
        try:
            db.session.execute(text(index_sql))
            index_name = index_sql.split()[5]
            print(f"  ✅ {index_name}")
            success_count += 1
        except Exception as e:
            print(f"  ❌ فشل في إنشاء فهرس: {e}")
    
    return success_count

def create_leave_indexes():
    """إنشاء فهارس جدول الإجازات"""
    print("\n🏖️ إنشاء فهارس جدول الإجازات...")
    
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_leave_employee ON leave(employee_id)",
        "CREATE INDEX IF NOT EXISTS idx_leave_start_date ON leave(start_date)",
        "CREATE INDEX IF NOT EXISTS idx_leave_end_date ON leave(end_date)",
        "CREATE INDEX IF NOT EXISTS idx_leave_type ON leave(leave_type)",
        "CREATE INDEX IF NOT EXISTS idx_leave_status ON leave(status)"
    ]
    
    success_count = 0
    for index_sql in indexes:
        try:
            db.session.execute(text(index_sql))
            index_name = index_sql.split()[5]
            print(f"  ✅ {index_name}")
            success_count += 1
        except Exception as e:
            print(f"  ❌ فشل في إنشاء فهرس: {e}")
    
    return success_count

def analyze_database_performance():
    """تحليل أداء قاعدة البيانات"""
    print("\n📊 تحليل أداء قاعدة البيانات...")
    print("="*50)
    
    try:
        # تحديث إحصائيات SQLite
        db.session.execute(text("ANALYZE"))
        print("✅ تم تحديث إحصائيات قاعدة البيانات")
        
        # فحص حجم قاعدة البيانات
        result = db.session.execute(text("PRAGMA page_count")).scalar()
        page_size = db.session.execute(text("PRAGMA page_size")).scalar()
        db_size = result * page_size
        
        print(f"📏 حجم قاعدة البيانات: {db_size:,} بايت ({db_size/1024/1024:.2f} ميجابايت)")
        print(f"📄 عدد الصفحات: {result:,}")
        print(f"📐 حجم الصفحة: {page_size:,} بايت")
        
        # فحص الفهارس
        indexes = db.session.execute(text(
            "SELECT name FROM sqlite_master WHERE type='index' AND name NOT LIKE 'sqlite_%'"
        )).fetchall()
        
        print(f"📇 عدد الفهارس المخصصة: {len(indexes)}")
        
        return True
        
    except Exception as e:
        print(f"❌ خطأ في تحليل الأداء: {e}")
        return False

def main():
    """إنشاء جميع الفهارس"""
    print("📇 إضافة فهارس قاعدة البيانات لتحسين الأداء")
    print("="*60)
    
    try:
        with app.app_context():
            total_indexes = 0
            
            # إنشاء فهارس لكل جدول
            total_indexes += create_invoice_indexes()
            total_indexes += create_payment_indexes()
            total_indexes += create_employee_indexes()
            total_indexes += create_attendance_indexes()
            total_indexes += create_customer_indexes()
            total_indexes += create_product_indexes()
            total_indexes += create_expense_indexes()
            total_indexes += create_payroll_indexes()
            total_indexes += create_leave_indexes()
            
            # حفظ التغييرات
            db.session.commit()
            print(f"\n✅ تم إنشاء {total_indexes} فهرس بنجاح")
            
            # تحليل الأداء
            analyze_database_performance()
            
            print("\n🎉 تم تحسين أداء قاعدة البيانات بنجاح!")
            print("🚀 التطبيق الآن أسرع في البحث والاستعلامات")
            
    except Exception as e:
        print(f"❌ خطأ في إنشاء الفهارس: {e}")
        db.session.rollback()

if __name__ == "__main__":
    main()
