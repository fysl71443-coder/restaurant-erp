#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
مراقب الأداء
Performance Monitor
"""

import time
import psutil
import logging
from datetime import datetime, timedelta
from functools import wraps
from flask import request, g, current_app
from app import db
from app.models.system_monitoring import PerformanceMetric
from app.performance.cache_manager import cache_manager

logger = logging.getLogger('accounting_system')

class PerformanceMonitor:
    """مراقب الأداء"""
    
    def __init__(self, app=None):
        self.app = app
        self.metrics = {}
        self.slow_queries = []
        self.request_times = []
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """تهيئة مراقب الأداء"""
        self.app = app
        
        # إعداد حدود الأداء
        self.slow_query_threshold = app.config.get('SLOW_QUERY_THRESHOLD', 1.0)  # ثانية
        self.slow_request_threshold = app.config.get('SLOW_REQUEST_THRESHOLD', 2.0)  # ثانية
        self.memory_warning_threshold = app.config.get('MEMORY_WARNING_THRESHOLD', 80)  # نسبة مئوية
        
        # تسجيل معالجات الطلبات
        self._register_request_handlers()
    
    def _register_request_handlers(self):
        """تسجيل معالجات الطلبات لمراقبة الأداء"""
        
        @self.app.before_request
        def before_request():
            g.start_time = time.time()
            g.request_start_memory = psutil.Process().memory_info().rss
        
        @self.app.after_request
        def after_request(response):
            if hasattr(g, 'start_time'):
                request_time = time.time() - g.start_time
                
                # تسجيل وقت الطلب
                self.record_request_time(request_time)
                
                # تحذير للطلبات البطيئة
                if request_time > self.slow_request_threshold:
                    self.log_slow_request(request_time)
                
                # تسجيل استخدام الذاكرة
                if hasattr(g, 'request_start_memory'):
                    memory_used = psutil.Process().memory_info().rss - g.request_start_memory
                    self.record_memory_usage(memory_used)
                
                # إضافة headers للأداء
                response.headers['X-Response-Time'] = f"{request_time:.3f}s"
                response.headers['X-Memory-Usage'] = f"{memory_used / 1024 / 1024:.2f}MB" if hasattr(g, 'request_start_memory') else "N/A"
            
            return response
    
    def record_request_time(self, request_time):
        """تسجيل وقت الطلب"""
        try:
            # حفظ في قائمة محلية (آخر 1000 طلب)
            self.request_times.append({
                'time': request_time,
                'timestamp': datetime.utcnow(),
                'endpoint': request.endpoint,
                'method': request.method
            })
            
            # الاحتفاظ بآخر 1000 طلب فقط
            if len(self.request_times) > 1000:
                self.request_times = self.request_times[-1000:]
            
            # تسجيل في قاعدة البيانات كل 10 طلبات
            if len(self.request_times) % 10 == 0:
                avg_time = sum(r['time'] for r in self.request_times[-10:]) / 10
                PerformanceMetric.record_metric(
                    name='avg_response_time',
                    value=avg_time * 1000,  # تحويل لميلي ثانية
                    unit='ms',
                    category='request',
                    source=request.endpoint
                )
                db.session.commit()
        
        except Exception as e:
            logger.error(f"Failed to record request time: {str(e)}")
    
    def record_memory_usage(self, memory_used):
        """تسجيل استخدام الذاكرة"""
        try:
            # تسجيل استخدام الذاكرة للطلب
            PerformanceMetric.record_metric(
                name='request_memory_usage',
                value=memory_used / 1024 / 1024,  # تحويل لميجابايت
                unit='MB',
                category='memory',
                source=request.endpoint
            )
            
            # فحص استخدام الذاكرة الإجمالي
            total_memory = psutil.virtual_memory()
            if total_memory.percent > self.memory_warning_threshold:
                self.log_high_memory_usage(total_memory.percent)
        
        except Exception as e:
            logger.error(f"Failed to record memory usage: {str(e)}")
    
    def log_slow_request(self, request_time):
        """تسجيل الطلبات البطيئة"""
        try:
            slow_request = {
                'endpoint': request.endpoint,
                'method': request.method,
                'url': request.url,
                'time': request_time,
                'timestamp': datetime.utcnow(),
                'user_agent': request.headers.get('User-Agent', 'Unknown'),
                'ip': request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR'))
            }
            
            logger.warning(f"Slow request detected: {request.method} {request.endpoint} took {request_time:.3f}s")
            
            # حفظ في قائمة الطلبات البطيئة
            self.slow_queries.append(slow_request)
            
            # الاحتفاظ بآخر 100 طلب بطيء
            if len(self.slow_queries) > 100:
                self.slow_queries = self.slow_queries[-100:]
            
            # تسجيل في قاعدة البيانات
            PerformanceMetric.record_metric(
                name='slow_request',
                value=request_time * 1000,
                unit='ms',
                category='performance_issue',
                source=request.endpoint,
                metadata=slow_request
            )
            db.session.commit()
        
        except Exception as e:
            logger.error(f"Failed to log slow request: {str(e)}")
    
    def log_high_memory_usage(self, memory_percent):
        """تسجيل استخدام الذاكرة العالي"""
        try:
            logger.warning(f"High memory usage detected: {memory_percent:.1f}%")
            
            PerformanceMetric.record_metric(
                name='high_memory_usage',
                value=memory_percent,
                unit='%',
                category='system_warning',
                source='system_monitor'
            )
            db.session.commit()
        
        except Exception as e:
            logger.error(f"Failed to log high memory usage: {str(e)}")
    
    def get_performance_stats(self, hours=24):
        """الحصول على إحصائيات الأداء"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            
            # متوسط وقت الاستجابة
            avg_response_time = PerformanceMetric.get_average('avg_response_time', hours)
            
            # عدد الطلبات البطيئة
            slow_requests_count = len([r for r in self.request_times 
                                     if r['timestamp'] > cutoff_time and r['time'] > self.slow_request_threshold])
            
            # استخدام الذاكرة الحالي
            current_memory = psutil.virtual_memory()
            
            # استخدام المعالج الحالي
            current_cpu = psutil.cpu_percent(interval=1)
            
            # إحصائيات التخزين المؤقت
            cache_stats = cache_manager.get_stats()
            
            return {
                'avg_response_time': round(avg_response_time, 2) if avg_response_time else 0,
                'slow_requests_count': slow_requests_count,
                'total_requests': len([r for r in self.request_times if r['timestamp'] > cutoff_time]),
                'memory_usage': {
                    'percent': current_memory.percent,
                    'available_gb': round(current_memory.available / (1024**3), 2),
                    'total_gb': round(current_memory.total / (1024**3), 2)
                },
                'cpu_usage': current_cpu,
                'cache_stats': cache_stats,
                'uptime': self._get_system_uptime()
            }
        
        except Exception as e:
            logger.error(f"Failed to get performance stats: {str(e)}")
            return {}
    
    def get_slow_requests(self, limit=50):
        """الحصول على الطلبات البطيئة"""
        return sorted(self.slow_queries, key=lambda x: x['timestamp'], reverse=True)[:limit]
    
    def get_endpoint_performance(self, hours=24):
        """الحصول على أداء النقاط النهائية"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            
            # تجميع الطلبات حسب النقطة النهائية
            endpoint_stats = {}
            
            for request_data in self.request_times:
                if request_data['timestamp'] > cutoff_time:
                    endpoint = request_data['endpoint']
                    
                    if endpoint not in endpoint_stats:
                        endpoint_stats[endpoint] = {
                            'count': 0,
                            'total_time': 0,
                            'max_time': 0,
                            'min_time': float('inf'),
                            'slow_count': 0
                        }
                    
                    stats = endpoint_stats[endpoint]
                    stats['count'] += 1
                    stats['total_time'] += request_data['time']
                    stats['max_time'] = max(stats['max_time'], request_data['time'])
                    stats['min_time'] = min(stats['min_time'], request_data['time'])
                    
                    if request_data['time'] > self.slow_request_threshold:
                        stats['slow_count'] += 1
            
            # حساب المتوسطات
            for endpoint, stats in endpoint_stats.items():
                stats['avg_time'] = stats['total_time'] / stats['count']
                stats['slow_percentage'] = (stats['slow_count'] / stats['count']) * 100
                
                # تحويل min_time إذا لم يتم تحديثه
                if stats['min_time'] == float('inf'):
                    stats['min_time'] = 0
            
            return endpoint_stats
        
        except Exception as e:
            logger.error(f"Failed to get endpoint performance: {str(e)}")
            return {}
    
    def _get_system_uptime(self):
        """الحصول على وقت تشغيل النظام"""
        try:
            import platform
            if platform.system() == "Windows":
                import subprocess
                result = subprocess.run(['wmic', 'os', 'get', 'LastBootUpTime'], 
                                      capture_output=True, text=True)
                # تحليل النتيجة وحساب الوقت
                return "N/A"  # تبسيط للآن
            else:
                with open('/proc/uptime', 'r') as f:
                    uptime_seconds = float(f.readline().split()[0])
                    return str(timedelta(seconds=int(uptime_seconds)))
        except:
            return "N/A"
    
    def optimize_performance(self):
        """تحسين الأداء التلقائي"""
        try:
            optimizations = []
            
            # تنظيف التخزين المؤقت المنتهي الصلاحية
            from app.performance.cache_manager import cleanup_expired_cache
            cleaned_cache = cleanup_expired_cache()
            if cleaned_cache > 0:
                optimizations.append(f"Cleaned {cleaned_cache} expired cache entries")
            
            # تحسين قاعدة البيانات
            from app.performance.cache_manager import optimize_database_queries
            if optimize_database_queries():
                optimizations.append("Database indexes optimized")
            
            # تنظيف البيانات القديمة
            cutoff_date = datetime.utcnow() - timedelta(days=7)
            old_metrics = PerformanceMetric.query.filter(
                PerformanceMetric.timestamp < cutoff_date
            ).delete()
            
            if old_metrics > 0:
                db.session.commit()
                optimizations.append(f"Cleaned {old_metrics} old performance metrics")
            
            logger.info(f"Performance optimization completed: {', '.join(optimizations)}")
            return optimizations
        
        except Exception as e:
            logger.error(f"Performance optimization failed: {str(e)}")
            return []

# ديكوريتر لمراقبة أداء الوظائف
def monitor_performance(func_name=None):
    """ديكوريتر لمراقبة أداء الوظائف"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            start_memory = psutil.Process().memory_info().rss
            
            try:
                result = func(*args, **kwargs)
                
                # حساب الأداء
                execution_time = time.time() - start_time
                memory_used = psutil.Process().memory_info().rss - start_memory
                
                # تسجيل المقاييس
                name = func_name or func.__name__
                PerformanceMetric.record_metric(
                    name=f"function_{name}_time",
                    value=execution_time * 1000,
                    unit='ms',
                    category='function_performance',
                    source=name
                )
                
                PerformanceMetric.record_metric(
                    name=f"function_{name}_memory",
                    value=memory_used / 1024 / 1024,
                    unit='MB',
                    category='function_performance',
                    source=name
                )
                
                # تحذير للوظائف البطيئة
                if execution_time > 1.0:  # أكثر من ثانية
                    logger.warning(f"Slow function detected: {name} took {execution_time:.3f}s")
                
                return result
            
            except Exception as e:
                # تسجيل الأخطاء
                execution_time = time.time() - start_time
                logger.error(f"Function {func_name or func.__name__} failed after {execution_time:.3f}s: {str(e)}")
                raise
        
        return wrapper
    return decorator

# إنشاء مثيل مراقب الأداء
performance_monitor = PerformanceMonitor()
