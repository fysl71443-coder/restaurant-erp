#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
إعادة إنشاء قاعدة البيانات مع الحقول الجديدة
"""

import os
from app import app, db
from database import *
import random
from datetime import datetime, timedelta

def reset_database():
    """إعادة إنشاء قاعدة البيانات"""
    with app.app_context():
        print("🔄 إعادة إنشاء قاعدة البيانات...")
        
        # حذف قاعدة البيانات الموجودة
        if os.path.exists('accounting.db'):
            os.remove('accounting.db')
            print("✅ تم حذف قاعدة البيانات القديمة")
        
        # إنشاء قاعدة البيانات الجديدة
        db.create_all()
        print("✅ تم إنشاء قاعدة البيانات الجديدة")
        
        # إضافة بيانات تجريبية
        add_sample_data()
        
        print("🎉 تم إعادة إنشاء قاعدة البيانات بنجاح!")

def add_sample_data():
    """إضافة بيانات تجريبية"""
    print("📊 إضافة بيانات تجريبية...")
    
    # إضافة موظفين
    employees = [
        Employee(name='أحمد محمد علي', employee_id='EMP-001', department='المحاسبة', position='محاسب أول', salary=8000, status='active', hire_date=datetime.now() - timedelta(days=365)),
        Employee(name='فاطمة سالم أحمد', employee_id='EMP-002', department='الموارد البشرية', position='أخصائي موارد بشرية', salary=7000, status='active', hire_date=datetime.now() - timedelta(days=300)),
        Employee(name='محمد عبدالله سعد', employee_id='EMP-003', department='المبيعات', position='مندوب مبيعات', salary=6000, status='active', hire_date=datetime.now() - timedelta(days=200)),
        Employee(name='نورا خالد محمد', employee_id='EMP-004', department='التسويق', position='أخصائي تسويق', salary=6500, status='active', hire_date=datetime.now() - timedelta(days=150)),
        Employee(name='عبدالرحمن أحمد علي', employee_id='EMP-005', department='تقنية المعلومات', position='مطور برمجيات', salary=9000, status='active', hire_date=datetime.now() - timedelta(days=100))
    ]
    
    for emp in employees:
        db.session.add(emp)
    
    # إضافة عملاء
    customers = [
        Customer(name='شركة التجارة المتقدمة', email='info@advanced-trade.com', phone='0501234567'),
        Customer(name='مؤسسة الأعمال الحديثة', email='contact@modern-business.com', phone='0507654321'),
        Customer(name='شركة الخدمات المتكاملة', email='services@integrated.com', phone='0551234567'),
        Customer(name='مجموعة الاستثمار الذكي', email='invest@smart-group.com', phone='0557654321')
    ]
    
    for customer in customers:
        db.session.add(customer)
    
    # إضافة موردين
    suppliers = [
        Supplier(name='شركة الإمداد الحديثة', contact_info='supply@modern.com'),
        Supplier(name='مؤسسة التوريد المتقدمة', contact_info='advanced@supply.com'),
        Supplier(name='شركة المواد الأساسية', contact_info='materials@basic.com')
    ]
    
    for supplier in suppliers:
        db.session.add(supplier)
    
    # إضافة منتجات
    products = [
        Product(name='منتج أ', price=100.0, quantity=50),
        Product(name='منتج ب', price=200.0, quantity=30),
        Product(name='منتج ج', price=150.0, quantity=40),
        Product(name='منتج د', price=300.0, quantity=20)
    ]
    
    for product in products:
        db.session.add(product)
    
    db.session.commit()
    
    # إضافة فواتير مبيعات
    for i in range(5):
        invoice = Invoice(
            customer_name=f'عميل تجريبي {i+1}',
            total_amount=random.uniform(1000, 5000),
            invoice_type='sales',
            status=random.choice(['pending', 'paid', 'overdue']),
            subtotal=random.uniform(800, 4000),
            tax_amount=random.uniform(100, 600),
            discount=random.uniform(0, 200),
            notes=f'فاتورة مبيعات تجريبية رقم {i+1}',
            date=datetime.now() - timedelta(days=random.randint(1, 30))
        )
        db.session.add(invoice)
    
    # إضافة فواتير مشتريات
    for i in range(3):
        purchase_invoice = PurchaseInvoice(
            supplier_name=f'مورد تجريبي {i+1}',
            total_amount=random.uniform(2000, 8000),
            status=random.choice(['pending', 'paid', 'overdue']),
            subtotal=random.uniform(1500, 6000),
            tax_amount=random.uniform(200, 900),
            discount=random.uniform(0, 300),
            notes=f'فاتورة مشتريات تجريبية رقم {i+1}',
            date=datetime.now() - timedelta(days=random.randint(1, 20))
        )
        db.session.add(purchase_invoice)
    
    # إضافة مدفوعات
    payment_methods = ['cash', 'bank_transfer', 'check', 'card']
    payment_types = ['received', 'paid']
    
    for i in range(8):
        payment_type = random.choice(payment_types)
        payment = Payment(
            amount=random.uniform(500, 3000),
            payment_method=random.choice(payment_methods),
            payment_type=payment_type,
            reference_number=f'REF-{i+1:03d}',
            customer_name=f'عميل {i+1}' if payment_type == 'received' else None,
            supplier_name=f'مورد {i+1}' if payment_type == 'paid' else None,
            notes=f'دفع تجريبي رقم {i+1}',
            date=datetime.now() - timedelta(days=random.randint(1, 15))
        )
        db.session.add(payment)
    
    # إضافة سجلات حضور
    for emp in employees:
        for day in range(10):  # آخر 10 أيام
            attendance_date = datetime.now().date() - timedelta(days=day)
            if attendance_date.weekday() < 5:  # أيام العمل فقط
                attendance = Attendance(
                    employee_id=emp.id,
                    date=attendance_date,
                    check_in=datetime.min.time().replace(hour=8, minute=random.randint(0, 30)),
                    check_out=datetime.min.time().replace(hour=17, minute=random.randint(0, 30)),
                    total_hours=8 + random.uniform(-0.5, 1.0),
                    overtime_hours=random.uniform(0, 2) if random.random() > 0.7 else 0
                )
                db.session.add(attendance)
    
    # إضافة رواتب
    for emp in employees:
        payroll = Payroll(
            employee_id=emp.id,
            month=12,
            year=2024,
            basic_salary=emp.salary,
            allowances=emp.salary * 0.1,
            overtime_pay=random.uniform(0, 500),
            deductions=emp.salary * 0.05,
            tax=emp.salary * 0.02,
            insurance=emp.salary * 0.09,
            net_salary=emp.salary * 0.94 + random.uniform(-200, 200),
            status='pending'
        )
        db.session.add(payroll)
    
    # إضافة إجازات
    leave_types = ['annual', 'sick', 'emergency', 'maternity']
    statuses = ['pending', 'approved', 'rejected']
    
    for emp in employees[:3]:  # إجازات لأول 3 موظفين
        leave = Leave(
            employee_id=emp.id,
            leave_type=random.choice(leave_types),
            start_date=datetime.now().date() + timedelta(days=random.randint(1, 30)),
            end_date=datetime.now().date() + timedelta(days=random.randint(31, 40)),
            reason=f'سبب الإجازة للموظف {emp.name}',
            status=random.choice(statuses)
        )
        db.session.add(leave)
    
    db.session.commit()
    print("✅ تم إضافة البيانات التجريبية")

if __name__ == "__main__":
    reset_database()
