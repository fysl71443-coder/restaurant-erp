#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
تحسينات الأداء للخادم
Server Performance Optimizations
"""

from functools import wraps, lru_cache
from datetime import datetime, timedelta
import time
import threading
from flask import request, jsonify, g
from database import db
import logging

# إعداد نظام التسجيل للأداء
performance_logger = logging.getLogger('performance')
performance_logger.setLevel(logging.INFO)

# Cache للبيانات المحسوبة
_cache = {}
_cache_lock = threading.Lock()

class PerformanceCache:
    """نظام cache محسن للبيانات"""
    
    def __init__(self, default_timeout=300):  # 5 دقائق افتراضي
        self.cache = {}
        self.timeouts = {}
        self.default_timeout = default_timeout
        self.lock = threading.Lock()
    
    def get(self, key):
        """الحصول على قيمة من الـ cache"""
        with self.lock:
            if key in self.cache:
                # التحقق من انتهاء الصلاحية
                if key in self.timeouts and time.time() > self.timeouts[key]:
                    del self.cache[key]
                    del self.timeouts[key]
                    return None
                return self.cache[key]
            return None
    
    def set(self, key, value, timeout=None):
        """تعيين قيمة في الـ cache"""
        with self.lock:
            self.cache[key] = value
            if timeout is None:
                timeout = self.default_timeout
            self.timeouts[key] = time.time() + timeout
    
    def delete(self, key):
        """حذف قيمة من الـ cache"""
        with self.lock:
            if key in self.cache:
                del self.cache[key]
            if key in self.timeouts:
                del self.timeouts[key]
    
    def clear(self):
        """مسح جميع البيانات من الـ cache"""
        with self.lock:
            self.cache.clear()
            self.timeouts.clear()

# إنشاء instance من الـ cache
app_cache = PerformanceCache()

def cache_result(timeout=300, key_func=None):
    """Decorator لـ cache نتائج الدوال"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # إنشاء مفتاح cache
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = f"{func.__name__}:{str(args)}:{str(sorted(kwargs.items()))}"
            
            # محاولة الحصول على النتيجة من الـ cache
            cached_result = app_cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # تنفيذ الدالة وحفظ النتيجة
            result = func(*args, **kwargs)
            app_cache.set(cache_key, result, timeout)
            return result
        return wrapper
    return decorator

def measure_performance(func):
    """Decorator لقياس أداء الدوال"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            # تسجيل الأداء إذا كان بطيئاً
            if execution_time > 1.0:  # أكثر من ثانية
                performance_logger.warning(
                    f"Slow function: {func.__name__} took {execution_time:.2f}s"
                )
            elif execution_time > 0.5:  # أكثر من نصف ثانية
                performance_logger.info(
                    f"Function: {func.__name__} took {execution_time:.2f}s"
                )
            
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            performance_logger.error(
                f"Function {func.__name__} failed after {execution_time:.2f}s: {str(e)}"
            )
            raise
    return wrapper

def optimize_db_query(query, use_cache=True, cache_timeout=300):
    """تحسين استعلامات قاعدة البيانات"""
    if use_cache:
        # إنشاء مفتاح cache للاستعلام
        cache_key = f"db_query:{str(query)}"
        cached_result = app_cache.get(cache_key)
        if cached_result is not None:
            return cached_result
    
    # تنفيذ الاستعلام
    start_time = time.time()
    try:
        result = query.all()
        execution_time = time.time() - start_time
        
        # تسجيل الاستعلامات البطيئة
        if execution_time > 0.5:
            performance_logger.warning(
                f"Slow DB query took {execution_time:.2f}s: {str(query)}"
            )
        
        # حفظ النتيجة في الـ cache
        if use_cache:
            app_cache.set(cache_key, result, cache_timeout)
        
        return result
    except Exception as e:
        execution_time = time.time() - start_time
        performance_logger.error(
            f"DB query failed after {execution_time:.2f}s: {str(e)}"
        )
        raise

@lru_cache(maxsize=128)
def get_cached_analytics_data(date_str):
    """الحصول على بيانات التحليلات مع cache"""
    from database import Invoice, PurchaseInvoice, Customer, Supplier
    
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        # إحصائيات أساسية
        total_sales = db.session.query(db.func.sum(Invoice.total_amount)).scalar() or 0
        total_purchases = db.session.query(db.func.sum(PurchaseInvoice.total_amount)).scalar() or 0
        
        # عدد العملاء والموردين
        customers_count = Customer.query.count()
        suppliers_count = Supplier.query.count()
        
        return {
            'total_sales': total_sales,
            'total_purchases': total_purchases,
            'net_profit': total_sales - total_purchases,
            'customers_count': customers_count,
            'suppliers_count': suppliers_count,
            'cached_at': datetime.now().isoformat()
        }
    except Exception as e:
        performance_logger.error(f"Error in get_cached_analytics_data: {str(e)}")
        return None

def invalidate_analytics_cache():
    """إلغاء cache بيانات التحليلات"""
    get_cached_analytics_data.cache_clear()
    # حذف cache keys ذات الصلة
    keys_to_delete = [key for key in app_cache.cache.keys() if 'analytics' in key or 'reports' in key]
    for key in keys_to_delete:
        app_cache.delete(key)

def batch_database_operations(operations, batch_size=100):
    """تنفيذ عمليات قاعدة البيانات في مجموعات"""
    results = []
    for i in range(0, len(operations), batch_size):
        batch = operations[i:i + batch_size]
        try:
            # تنفيذ المجموعة
            for operation in batch:
                if callable(operation):
                    result = operation()
                    results.append(result)
            
            # حفظ التغييرات
            db.session.commit()
            
        except Exception as e:
            db.session.rollback()
            performance_logger.error(f"Batch operation failed: {str(e)}")
            raise
    
    return results

def optimize_pagination(query, page, per_page=20, max_per_page=100):
    """تحسين pagination للاستعلامات الكبيرة"""
    # تحديد حد أقصى للعناصر في الصفحة
    per_page = min(per_page, max_per_page)
    
    # حساب offset
    offset = (page - 1) * per_page
    
    # تنفيذ الاستعلام مع limit و offset
    items = query.offset(offset).limit(per_page).all()
    
    # حساب العدد الكلي (مع cache)
    cache_key = f"total_count:{str(query)}"
    total = app_cache.get(cache_key)
    if total is None:
        total = query.count()
        app_cache.set(cache_key, total, 60)  # cache لمدة دقيقة
    
    return {
        'items': items,
        'total': total,
        'page': page,
        'per_page': per_page,
        'pages': (total + per_page - 1) // per_page
    }

def preload_related_data(query, *relationships):
    """تحميل البيانات المرتبطة مسبقاً لتجنب N+1 queries"""
    from sqlalchemy.orm import joinedload
    
    for relationship in relationships:
        query = query.options(joinedload(relationship))
    
    return query

# دوال مساعدة للتحسين
def get_optimized_monthly_data(year=None):
    """الحصول على البيانات الشهرية محسنة"""
    if year is None:
        year = datetime.now().year
    
    cache_key = f"monthly_data:{year}"
    cached_data = app_cache.get(cache_key)
    if cached_data:
        return cached_data
    
    # تنفيذ استعلام محسن
    from database import Invoice, PurchaseInvoice
    
    monthly_sales = db.session.query(
        db.func.strftime('%m', Invoice.date).label('month'),
        db.func.sum(Invoice.total_amount).label('total')
    ).filter(
        db.func.strftime('%Y', Invoice.date) == str(year)
    ).group_by(
        db.func.strftime('%m', Invoice.date)
    ).all()
    
    monthly_purchases = db.session.query(
        db.func.strftime('%m', PurchaseInvoice.date).label('month'),
        db.func.sum(PurchaseInvoice.total_amount).label('total')
    ).filter(
        db.func.strftime('%Y', PurchaseInvoice.date) == str(year)
    ).group_by(
        db.func.strftime('%m', PurchaseInvoice.date)
    ).all()
    
    # تنظيم البيانات
    sales_by_month = {int(row.month): float(row.total or 0) for row in monthly_sales}
    purchases_by_month = {int(row.month): float(row.total or 0) for row in monthly_purchases}
    
    result = {
        'sales': [sales_by_month.get(i, 0) for i in range(1, 13)],
        'purchases': [purchases_by_month.get(i, 0) for i in range(1, 13)],
        'year': year
    }
    
    # حفظ في الـ cache لمدة ساعة
    app_cache.set(cache_key, result, 3600)
    return result
