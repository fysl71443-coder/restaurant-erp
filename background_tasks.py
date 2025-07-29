#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نظام المهام الخلفية
Background Tasks System
"""

import threading
import time
import logging
from datetime import datetime, timedelta
from queue import Queue, Empty
from functools import wraps
import json
import os
from database import db, Invoice, PurchaseInvoice, Customer, Supplier, Employee, Attendance, Payroll
from performance_optimizations import app_cache

# إعداد نظام التسجيل
task_logger = logging.getLogger('background_tasks')
task_logger.setLevel(logging.INFO)

# قائمة انتظار المهام
task_queue = Queue()
task_results = {}
task_status = {}

class TaskStatus:
    """حالات المهام"""
    PENDING = 'pending'
    RUNNING = 'running'
    COMPLETED = 'completed'
    FAILED = 'failed'
    CANCELLED = 'cancelled'

class BackgroundTask:
    """فئة المهمة الخلفية"""
    
    def __init__(self, task_id, name, func, args=None, kwargs=None, priority=1):
        self.task_id = task_id
        self.name = name
        self.func = func
        self.args = args or []
        self.kwargs = kwargs or {}
        self.priority = priority
        self.created_at = datetime.now()
        self.started_at = None
        self.completed_at = None
        self.status = TaskStatus.PENDING
        self.result = None
        self.error = None
        self.progress = 0

    def __lt__(self, other):
        """للمقارنة في priority queue"""
        return self.priority > other.priority

class TaskWorker(threading.Thread):
    """عامل تنفيذ المهام"""
    
    def __init__(self, worker_id):
        super().__init__(daemon=True)
        self.worker_id = worker_id
        self.running = True
        
    def run(self):
        """تشغيل العامل"""
        task_logger.info(f"بدء تشغيل العامل {self.worker_id}")
        
        while self.running:
            try:
                # الحصول على مهمة من القائمة
                task = task_queue.get(timeout=1)
                
                if task is None:  # إشارة الإيقاف
                    break
                
                self.execute_task(task)
                task_queue.task_done()
                
            except Empty:
                continue
            except Exception as e:
                task_logger.error(f"خطأ في العامل {self.worker_id}: {str(e)}")
    
    def execute_task(self, task):
        """تنفيذ مهمة"""
        try:
            task_logger.info(f"بدء تنفيذ المهمة: {task.name} (ID: {task.task_id})")
            
            # تحديث حالة المهمة
            task.status = TaskStatus.RUNNING
            task.started_at = datetime.now()
            task_status[task.task_id] = task
            
            # تنفيذ المهمة
            result = task.func(*task.args, **task.kwargs)
            
            # تحديث النتيجة
            task.result = result
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now()
            task.progress = 100
            
            # حفظ النتيجة
            task_results[task.task_id] = result
            
            task_logger.info(f"تم إنجاز المهمة: {task.name} (ID: {task.task_id})")
            
        except Exception as e:
            task.error = str(e)
            task.status = TaskStatus.FAILED
            task.completed_at = datetime.now()
            
            task_logger.error(f"فشل في تنفيذ المهمة {task.name}: {str(e)}")
    
    def stop(self):
        """إيقاف العامل"""
        self.running = False

# إنشاء عمال المهام
workers = []
num_workers = 2  # عدد العمال

def start_workers():
    """بدء تشغيل العمال"""
    global workers
    for i in range(num_workers):
        worker = TaskWorker(f"worker-{i+1}")
        worker.start()
        workers.append(worker)
    task_logger.info(f"تم بدء تشغيل {num_workers} عامل")

def stop_workers():
    """إيقاف العمال"""
    global workers
    for worker in workers:
        worker.stop()
    
    # إضافة إشارات الإيقاف
    for _ in workers:
        task_queue.put(None)
    
    # انتظار انتهاء العمال
    for worker in workers:
        worker.join(timeout=5)
    
    workers.clear()
    task_logger.info("تم إيقاف جميع العمال")

def submit_task(name, func, args=None, kwargs=None, priority=1):
    """إرسال مهمة للتنفيذ"""
    task_id = f"task_{int(time.time() * 1000)}"
    task = BackgroundTask(task_id, name, func, args, kwargs, priority)
    
    task_status[task_id] = task
    task_queue.put(task)
    
    task_logger.info(f"تم إرسال المهمة: {name} (ID: {task_id})")
    return task_id

def get_task_status(task_id):
    """الحصول على حالة المهمة"""
    return task_status.get(task_id)

def get_task_result(task_id):
    """الحصول على نتيجة المهمة"""
    return task_results.get(task_id)

def background_task(name=None, priority=1):
    """Decorator لتحويل دالة إلى مهمة خلفية"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            task_name = name or func.__name__
            return submit_task(task_name, func, args, kwargs, priority)
        
        # إضافة دالة للتنفيذ المباشر
        wrapper.run_sync = func
        return wrapper
    return decorator

# ==================== مهام خلفية محددة ====================

@background_task("إنشاء تقرير مالي شامل", priority=2)
def generate_comprehensive_financial_report(start_date=None, end_date=None):
    """إنشاء تقرير مالي شامل"""
    try:
        if not start_date:
            start_date = datetime.now().replace(day=1)  # بداية الشهر
        if not end_date:
            end_date = datetime.now()
        
        report_data = {
            'period': {
                'start': start_date.strftime('%Y-%m-%d'),
                'end': end_date.strftime('%Y-%m-%d')
            },
            'generated_at': datetime.now().isoformat()
        }
        
        # إحصائيات المبيعات
        sales_query = db.session.query(
            db.func.sum(Invoice.total_amount).label('total'),
            db.func.count(Invoice.id).label('count'),
            db.func.avg(Invoice.total_amount).label('average')
        ).filter(
            Invoice.date.between(start_date, end_date)
        ).first()
        
        report_data['sales'] = {
            'total': float(sales_query.total or 0),
            'count': sales_query.count or 0,
            'average': float(sales_query.average or 0)
        }
        
        # إحصائيات المشتريات
        purchases_query = db.session.query(
            db.func.sum(PurchaseInvoice.total_amount).label('total'),
            db.func.count(PurchaseInvoice.id).label('count'),
            db.func.avg(PurchaseInvoice.total_amount).label('average')
        ).filter(
            PurchaseInvoice.date.between(start_date, end_date)
        ).first()
        
        report_data['purchases'] = {
            'total': float(purchases_query.total or 0),
            'count': purchases_query.count or 0,
            'average': float(purchases_query.average or 0)
        }
        
        # حساب الربح
        profit = report_data['sales']['total'] - report_data['purchases']['total']
        profit_margin = (profit / report_data['sales']['total'] * 100) if report_data['sales']['total'] > 0 else 0
        
        report_data['profit'] = {
            'net_profit': profit,
            'margin_percentage': profit_margin
        }
        
        # أفضل العملاء
        top_customers = db.session.query(
            Customer.name,
            db.func.sum(Invoice.total_amount).label('total')
        ).join(Invoice).filter(
            Invoice.date.between(start_date, end_date)
        ).group_by(Customer.id).order_by(
            db.func.sum(Invoice.total_amount).desc()
        ).limit(10).all()
        
        report_data['top_customers'] = [
            {'name': row.name, 'total': float(row.total)}
            for row in top_customers
        ]
        
        # حفظ التقرير في ملف
        report_filename = f"financial_report_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.json"
        report_path = os.path.join('reports', report_filename)
        
        # إنشاء مجلد التقارير إذا لم يكن موجوداً
        os.makedirs('reports', exist_ok=True)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        # حفظ في الـ cache
        cache_key = f"financial_report:{start_date.strftime('%Y%m%d')}:{end_date.strftime('%Y%m%d')}"
        app_cache.set(cache_key, report_data, 3600)  # ساعة واحدة
        
        return {
            'success': True,
            'report_path': report_path,
            'data': report_data
        }
        
    except Exception as e:
        task_logger.error(f"خطأ في إنشاء التقرير المالي: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }

@background_task("حساب إحصائيات الموظفين", priority=1)
def calculate_employee_statistics():
    """حساب إحصائيات شاملة للموظفين"""
    try:
        current_month = datetime.now().month
        current_year = datetime.now().year
        
        # إحصائيات عامة
        total_employees = Employee.query.count()
        active_employees = Employee.query.filter_by(status='active').count()
        
        # إحصائيات الحضور
        attendance_stats = db.session.query(
            db.func.count(Attendance.id).label('total_records'),
            db.func.avg(Attendance.total_hours).label('avg_hours'),
            db.func.sum(Attendance.overtime_hours).label('total_overtime')
        ).filter(
            db.extract('month', Attendance.date) == current_month,
            db.extract('year', Attendance.date) == current_year
        ).first()
        
        # إحصائيات الرواتب
        payroll_stats = db.session.query(
            db.func.sum(Payroll.net_salary).label('total_salaries'),
            db.func.avg(Payroll.net_salary).label('avg_salary'),
            db.func.count(Payroll.id).label('payroll_count')
        ).filter_by(
            month=current_month,
            year=current_year
        ).first()
        
        stats = {
            'employees': {
                'total': total_employees,
                'active': active_employees,
                'inactive': total_employees - active_employees
            },
            'attendance': {
                'total_records': attendance_stats.total_records or 0,
                'average_hours': float(attendance_stats.avg_hours or 0),
                'total_overtime': float(attendance_stats.total_overtime or 0)
            },
            'payroll': {
                'total_salaries': float(payroll_stats.total_salaries or 0),
                'average_salary': float(payroll_stats.avg_salary or 0),
                'payroll_count': payroll_stats.payroll_count or 0
            },
            'calculated_at': datetime.now().isoformat()
        }
        
        # حفظ في الـ cache
        cache_key = f"employee_stats:{current_year}:{current_month}"
        app_cache.set(cache_key, stats, 1800)  # 30 دقيقة
        
        return stats
        
    except Exception as e:
        task_logger.error(f"خطأ في حساب إحصائيات الموظفين: {str(e)}")
        return {'success': False, 'error': str(e)}

@background_task("تنظيف البيانات القديمة", priority=3)
def cleanup_old_data():
    """تنظيف البيانات والملفات القديمة"""
    try:
        cleaned_items = []
        
        # تنظيف cache منتهي الصلاحية
        app_cache.clear()
        cleaned_items.append("تم تنظيف الـ cache")
        
        # تنظيف نتائج المهام القديمة (أكثر من يوم)
        cutoff_time = datetime.now() - timedelta(days=1)
        old_tasks = [
            task_id for task_id, task in task_status.items()
            if task.completed_at and task.completed_at < cutoff_time
        ]
        
        for task_id in old_tasks:
            del task_status[task_id]
            if task_id in task_results:
                del task_results[task_id]
        
        cleaned_items.append(f"تم حذف {len(old_tasks)} مهمة قديمة")
        
        # تنظيف ملفات التقارير القديمة (أكثر من أسبوع)
        reports_dir = 'reports'
        if os.path.exists(reports_dir):
            old_files = []
            cutoff_timestamp = time.time() - (7 * 24 * 60 * 60)  # أسبوع
            
            for filename in os.listdir(reports_dir):
                filepath = os.path.join(reports_dir, filename)
                if os.path.isfile(filepath) and os.path.getmtime(filepath) < cutoff_timestamp:
                    os.remove(filepath)
                    old_files.append(filename)
            
            cleaned_items.append(f"تم حذف {len(old_files)} ملف تقرير قديم")
        
        return {
            'success': True,
            'cleaned_items': cleaned_items,
            'cleaned_at': datetime.now().isoformat()
        }
        
    except Exception as e:
        task_logger.error(f"خطأ في تنظيف البيانات: {str(e)}")
        return {'success': False, 'error': str(e)}

# تهيئة النظام
def initialize_background_tasks():
    """تهيئة نظام المهام الخلفية"""
    start_workers()
    task_logger.info("تم تهيئة نظام المهام الخلفية")

def shutdown_background_tasks():
    """إغلاق نظام المهام الخلفية"""
    stop_workers()
    task_logger.info("تم إغلاق نظام المهام الخلفية")
