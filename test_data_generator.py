#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
مولد البيانات التجريبية لاختبار نظام إدارة الموظفين
"""

from app import app
from database import db, Employee, Attendance, Payroll
from datetime import datetime, date, time, timedelta
import random

def create_test_employees():
    """إنشاء موظفين تجريبيين للاختبار"""
    
    # بيانات الموظفين التجريبية
    test_employees = [
        {
            'name': 'أحمد محمد العلي',
            'email': 'ahmed.ali@company.com',
            'phone': '0501234567',
            'national_id': '1234567890',
            'position': 'محاسب أول',
            'department': 'المالية والمحاسبة',
            'hire_date': date(2023, 1, 15),
            'birth_date': date(1990, 5, 20),
            'salary': 8000.00,
            'address': 'الرياض، حي النرجس، شارع الملك فهد',
            'emergency_contact': 'فاطمة العلي',
            'emergency_phone': '0509876543',
            'contract_type': 'full_time',
            'bank_account': '123456789',
            'iban': 'SA0123456789012345678901',
            'notes': 'موظف متميز في المحاسبة'
        },
        {
            'name': 'سارة أحمد الزهراني',
            'email': 'sara.zahrani@company.com',
            'phone': '0502345678',
            'national_id': '2345678901',
            'position': 'مطورة برمجيات',
            'department': 'تقنية المعلومات',
            'hire_date': date(2023, 3, 10),
            'birth_date': date(1992, 8, 15),
            'salary': 9500.00,
            'address': 'جدة، حي الروضة، شارع التحلية',
            'emergency_contact': 'محمد الزهراني',
            'emergency_phone': '0508765432',
            'contract_type': 'full_time',
            'bank_account': '234567890',
            'iban': 'SA0234567890123456789012',
            'notes': 'خبيرة في تطوير الويب'
        },
        {
            'name': 'خالد عبدالله القحطاني',
            'email': 'khalid.qahtani@company.com',
            'phone': '0503456789',
            'national_id': '3456789012',
            'position': 'مدير مبيعات',
            'department': 'المبيعات',
            'hire_date': date(2022, 6, 1),
            'birth_date': date(1988, 12, 3),
            'salary': 12000.00,
            'address': 'الدمام، حي الفيصلية، شارع الأمير محمد',
            'emergency_contact': 'نورا القحطاني',
            'emergency_phone': '0507654321',
            'contract_type': 'full_time',
            'bank_account': '345678901',
            'iban': 'SA0345678901234567890123',
            'notes': 'قائد فريق مبيعات ناجح'
        },
        {
            'name': 'فاطمة علي الشهري',
            'email': 'fatima.shahri@company.com',
            'phone': '0504567890',
            'national_id': '4567890123',
            'position': 'أخصائية موارد بشرية',
            'department': 'الموارد البشرية',
            'hire_date': date(2023, 2, 20),
            'birth_date': date(1991, 4, 10),
            'salary': 7500.00,
            'address': 'مكة المكرمة، حي العزيزية، شارع الحرم',
            'emergency_contact': 'عبدالله الشهري',
            'emergency_phone': '0506543210',
            'contract_type': 'full_time',
            'bank_account': '456789012',
            'iban': 'SA0456789012345678901234',
            'notes': 'متخصصة في التوظيف والتدريب'
        },
        {
            'name': 'محمد سعد الغامدي',
            'email': 'mohammed.ghamdi@company.com',
            'phone': '0505678901',
            'national_id': '5678901234',
            'position': 'مصمم جرافيك',
            'department': 'التسويق',
            'hire_date': date(2023, 4, 5),
            'birth_date': date(1993, 7, 25),
            'salary': 6500.00,
            'address': 'الطائف، حي الشفا، شارع الملك عبدالعزيز',
            'emergency_contact': 'أم محمد الغامدي',
            'emergency_phone': '0505432109',
            'contract_type': 'part_time',
            'bank_account': '567890123',
            'iban': 'SA0567890123456789012345',
            'notes': 'مبدع في التصميم والإعلان'
        },
        {
            'name': 'نورا حسن العتيبي',
            'email': 'nora.otaibi@company.com',
            'phone': '0506789012',
            'national_id': '6789012345',
            'position': 'منسقة عمليات',
            'department': 'العمليات',
            'hire_date': date(2023, 1, 30),
            'birth_date': date(1989, 11, 18),
            'salary': 7000.00,
            'address': 'المدينة المنورة، حي العوالي، شارع قباء',
            'emergency_contact': 'سعد العتيبي',
            'emergency_phone': '0504321098',
            'contract_type': 'full_time',
            'bank_account': '678901234',
            'iban': 'SA0678901234567890123456',
            'notes': 'منظمة ودقيقة في العمل'
        },
        {
            'name': 'عبدالرحمن يوسف الدوسري',
            'email': 'abdulrahman.dosari@company.com',
            'phone': '0507890123',
            'national_id': '7890123456',
            'position': 'أخصائي خدمة عملاء',
            'department': 'خدمة العملاء',
            'hire_date': date(2023, 5, 15),
            'birth_date': date(1994, 2, 8),
            'salary': 5500.00,
            'address': 'الخبر، حي الثقبة، شارع الملك فيصل',
            'emergency_contact': 'أم عبدالرحمن',
            'emergency_phone': '0503210987',
            'contract_type': 'contract',
            'bank_account': '789012345',
            'iban': 'SA0789012345678901234567',
            'notes': 'ممتاز في التعامل مع العملاء'
        },
        {
            'name': 'ريم عبدالله المطيري',
            'email': 'reem.mutairi@company.com',
            'phone': '0508901234',
            'national_id': '8901234567',
            'position': 'محللة مالية',
            'department': 'المالية والمحاسبة',
            'hire_date': date(2022, 9, 12),
            'birth_date': date(1987, 6, 30),
            'salary': 8500.00,
            'address': 'بريدة، حي الصفراء، شارع الملك سعود',
            'emergency_contact': 'خالد المطيري',
            'emergency_phone': '0502109876',
            'contract_type': 'full_time',
            'bank_account': '890123456',
            'iban': 'SA0890123456789012345678',
            'notes': 'خبيرة في التحليل المالي'
        }
    ]
    
    with app.app_context():
        # حذف البيانات الموجودة
        db.session.query(Attendance).delete()
        db.session.query(Payroll).delete()
        db.session.query(Employee).delete()
        
        employees = []
        for i, emp_data in enumerate(test_employees, 1):
            # إنشاء رقم موظف تلقائي
            employee_id = f'EMP{i:04d}'
            
            employee = Employee(
                employee_id=employee_id,
                **emp_data
            )
            
            db.session.add(employee)
            employees.append(employee)
        
        db.session.commit()
        print(f"✅ تم إنشاء {len(employees)} موظف تجريبي بنجاح!")
        return employees

def create_test_attendance():
    """إنشاء سجلات حضور تجريبية"""

    with app.app_context():
        # الحصول على الموظفين من قاعدة البيانات
        employees = Employee.query.all()
        attendance_records = []

        # إنشاء سجلات حضور للأسبوعين الماضيين
        start_date = date.today() - timedelta(days=14)

        for day_offset in range(15):  # 15 يوم
            current_date = start_date + timedelta(days=day_offset)

            # تجاهل عطلة نهاية الأسبوع
            if current_date.weekday() >= 5:  # السبت والأحد
                continue

            for employee in employees:
                # احتمالية الحضور 90%
                if random.random() < 0.9:
                    # أوقات عمل عشوائية واقعية
                    check_in_hour = random.randint(7, 9)
                    check_in_minute = random.randint(0, 59)
                    check_in = time(check_in_hour, check_in_minute)
                    
                    # وقت الخروج (8-10 ساعات بعد الدخول)
                    work_hours = random.uniform(8, 10)
                    check_out_datetime = datetime.combine(current_date, check_in) + timedelta(hours=work_hours)
                    check_out = check_out_datetime.time()
                    
                    # استراحة الغداء
                    break_start = time(12, 0)
                    break_end = time(13, 0)
                    
                    # حساب إجمالي الساعات
                    total_hours = work_hours - 1  # خصم ساعة الغداء
                    overtime_hours = max(0, total_hours - 8)
                    
                    # تحديد الحالة
                    if check_in_hour > 8:
                        status = 'late'
                    elif total_hours < 6:
                        status = 'half_day'
                    else:
                        status = 'present'
                    
                    attendance = Attendance(
                        employee_id=employee.id,
                        date=current_date,
                        check_in=check_in,
                        check_out=check_out,
                        break_start=break_start,
                        break_end=break_end,
                        total_hours=total_hours,
                        overtime_hours=overtime_hours,
                        status=status,
                        notes=f'حضور {current_date.strftime("%A")}'
                    )
                    
                    db.session.add(attendance)
                    attendance_records.append(attendance)
                else:
                    # غياب
                    attendance = Attendance(
                        employee_id=employee.id,
                        date=current_date,
                        status='absent',
                        notes='غياب بدون إذن'
                    )
                    
                    db.session.add(attendance)
                    attendance_records.append(attendance)
        
        db.session.commit()
        print(f"✅ تم إنشاء {len(attendance_records)} سجل حضور تجريبي!")
        return attendance_records

def create_test_payroll():
    """إنشاء سجلات رواتب تجريبية"""

    with app.app_context():
        # الحصول على الموظفين من قاعدة البيانات
        employees = Employee.query.all()
        payroll_records = []
        
        # إنشاء رواتب للشهرين الماضيين
        current_date = date.today()
        
        for month_offset in range(2):
            if current_date.month - month_offset <= 0:
                month = 12 + (current_date.month - month_offset)
                year = current_date.year - 1
            else:
                month = current_date.month - month_offset
                year = current_date.year
            
            for employee in employees:
                # حساب البدلات والخصومات
                basic_salary = employee.salary or 5000
                allowances = basic_salary * 0.1  # 10% بدلات
                
                # حساب أجر الساعات الإضافية
                overtime_pay = 0
                if month_offset == 0:  # الشهر الحالي
                    # حساب الساعات الإضافية من سجلات الحضور
                    overtime_records = db.session.query(Attendance).filter(
                        Attendance.employee_id == employee.id,
                        Attendance.overtime_hours > 0
                    ).all()
                    
                    total_overtime = sum(record.overtime_hours for record in overtime_records)
                    overtime_rate = basic_salary / (30 * 8) * 1.5  # معدل الساعة الإضافية
                    overtime_pay = total_overtime * overtime_rate
                
                # الخصومات
                deductions = basic_salary * 0.05  # 5% خصومات متنوعة
                tax = basic_salary * 0.02  # 2% ضرائب
                insurance = basic_salary * 0.09  # 9% تأمينات اجتماعية
                
                # صافي الراتب
                net_salary = basic_salary + allowances + overtime_pay - deductions - tax - insurance
                
                payroll = Payroll(
                    employee_id=employee.id,
                    month=month,
                    year=year,
                    basic_salary=basic_salary,
                    allowances=allowances,
                    overtime_pay=overtime_pay,
                    deductions=deductions,
                    tax=tax,
                    insurance=insurance,
                    net_salary=net_salary,
                    payment_date=date(year, month, 25) if month_offset > 0 else None,
                    status='paid' if month_offset > 0 else 'pending',
                    notes=f'راتب شهر {month}/{year}'
                )
                
                db.session.add(payroll)
                payroll_records.append(payroll)
        
        db.session.commit()
        print(f"✅ تم إنشاء {len(payroll_records)} سجل راتب تجريبي!")
        return payroll_records

def run_test_data_generation():
    """تشغيل مولد البيانات التجريبية"""
    print("🚀 بدء إنشاء البيانات التجريبية...")
    
    try:
        # إنشاء الموظفين
        employees = create_test_employees()
        
        # إنشاء سجلات الحضور
        create_test_attendance()

        # إنشاء سجلات الرواتب
        create_test_payroll()
        
        print("\n🎉 تم إنشاء جميع البيانات التجريبية بنجاح!")
        print(f"📊 الإحصائيات:")
        print(f"   - الموظفين: {len(employees)}")
        print(f"   - الأقسام: 6 أقسام مختلفة")
        print(f"   - سجلات الحضور: ~{len(employees) * 10} سجل")
        print(f"   - سجلات الرواتب: {len(employees) * 2} سجل")
        
        return True
        
    except Exception as e:
        print(f"❌ خطأ في إنشاء البيانات التجريبية: {str(e)}")
        return False

if __name__ == "__main__":
    run_test_data_generation()
