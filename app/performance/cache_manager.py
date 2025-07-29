#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
مدير التخزين المؤقت
Cache Manager
"""

import redis
import pickle
import json
import logging
from datetime import datetime, timedelta
from functools import wraps
from flask import current_app, request
from app import db

logger = logging.getLogger('accounting_system')

class CacheManager:
    """مدير التخزين المؤقت"""
    
    def __init__(self, app=None):
        self.redis_client = None
        self.app = app
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """تهيئة مدير التخزين المؤقت"""
        self.app = app
        
        # إعداد Redis
        redis_url = app.config.get('REDIS_URL', 'redis://localhost:6379/0')
        try:
            self.redis_client = redis.from_url(redis_url, decode_responses=False)
            # اختبار الاتصال
            self.redis_client.ping()
            logger.info("Redis cache initialized successfully")
        except Exception as e:
            logger.warning(f"Redis not available, using memory cache: {str(e)}")
            self.redis_client = None
        
        # إعداد التخزين المؤقت في الذاكرة كبديل
        self.memory_cache = {}
        self.cache_expiry = {}
    
    def get(self, key):
        """الحصول على قيمة من التخزين المؤقت"""
        try:
            if self.redis_client:
                value = self.redis_client.get(key)
                if value:
                    return pickle.loads(value)
            else:
                # استخدام التخزين المؤقت في الذاكرة
                if key in self.memory_cache:
                    if key in self.cache_expiry and datetime.now() > self.cache_expiry[key]:
                        # انتهت صلاحية التخزين المؤقت
                        del self.memory_cache[key]
                        del self.cache_expiry[key]
                        return None
                    return self.memory_cache[key]
            
            return None
        except Exception as e:
            logger.error(f"Cache get error: {str(e)}")
            return None
    
    def set(self, key, value, timeout=3600):
        """تعيين قيمة في التخزين المؤقت"""
        try:
            if self.redis_client:
                self.redis_client.setex(key, timeout, pickle.dumps(value))
            else:
                # استخدام التخزين المؤقت في الذاكرة
                self.memory_cache[key] = value
                self.cache_expiry[key] = datetime.now() + timedelta(seconds=timeout)
            
            return True
        except Exception as e:
            logger.error(f"Cache set error: {str(e)}")
            return False
    
    def delete(self, key):
        """حذف قيمة من التخزين المؤقت"""
        try:
            if self.redis_client:
                self.redis_client.delete(key)
            else:
                if key in self.memory_cache:
                    del self.memory_cache[key]
                if key in self.cache_expiry:
                    del self.cache_expiry[key]
            
            return True
        except Exception as e:
            logger.error(f"Cache delete error: {str(e)}")
            return False
    
    def clear(self, pattern=None):
        """مسح التخزين المؤقت"""
        try:
            if self.redis_client:
                if pattern:
                    keys = self.redis_client.keys(pattern)
                    if keys:
                        self.redis_client.delete(*keys)
                else:
                    self.redis_client.flushdb()
            else:
                if pattern:
                    # مسح المفاتيح المطابقة للنمط
                    import fnmatch
                    keys_to_delete = [k for k in self.memory_cache.keys() if fnmatch.fnmatch(k, pattern)]
                    for key in keys_to_delete:
                        del self.memory_cache[key]
                        if key in self.cache_expiry:
                            del self.cache_expiry[key]
                else:
                    self.memory_cache.clear()
                    self.cache_expiry.clear()
            
            return True
        except Exception as e:
            logger.error(f"Cache clear error: {str(e)}")
            return False
    
    def get_stats(self):
        """الحصول على إحصائيات التخزين المؤقت"""
        try:
            if self.redis_client:
                info = self.redis_client.info()
                return {
                    'type': 'redis',
                    'connected': True,
                    'used_memory': info.get('used_memory_human', 'N/A'),
                    'total_keys': self.redis_client.dbsize(),
                    'hits': info.get('keyspace_hits', 0),
                    'misses': info.get('keyspace_misses', 0)
                }
            else:
                return {
                    'type': 'memory',
                    'connected': True,
                    'total_keys': len(self.memory_cache),
                    'expired_keys': len([k for k, exp in self.cache_expiry.items() if datetime.now() > exp])
                }
        except Exception as e:
            logger.error(f"Cache stats error: {str(e)}")
            return {
                'type': 'unknown',
                'connected': False,
                'error': str(e)
            }

# إنشاء مثيل مدير التخزين المؤقت
cache_manager = CacheManager()

# ديكوريتر للتخزين المؤقت
def cached(timeout=3600, key_prefix=''):
    """ديكوريتر للتخزين المؤقت للوظائف"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # إنشاء مفتاح التخزين المؤقت
            cache_key = f"{key_prefix}:{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
            
            # محاولة الحصول على القيمة من التخزين المؤقت
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # تنفيذ الوظيفة وحفظ النتيجة
            result = func(*args, **kwargs)
            cache_manager.set(cache_key, result, timeout)
            
            return result
        
        return wrapper
    return decorator

def cache_page(timeout=3600):
    """ديكوريتر لتخزين الصفحات مؤقتاً"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # إنشاء مفتاح التخزين المؤقت للصفحة
            cache_key = f"page:{request.endpoint}:{request.args.to_dict()}"
            
            # محاولة الحصول على الصفحة من التخزين المؤقت
            cached_page = cache_manager.get(cache_key)
            if cached_page is not None:
                return cached_page
            
            # تنفيذ الوظيفة وحفظ النتيجة
            result = func(*args, **kwargs)
            cache_manager.set(cache_key, result, timeout)
            
            return result
        
        return wrapper
    return decorator

class QueryCache:
    """تخزين مؤقت لاستعلامات قاعدة البيانات"""
    
    @staticmethod
    def get_cached_query(query_key, query_func, timeout=1800):
        """تنفيذ استعلام مع تخزين مؤقت"""
        cached_result = cache_manager.get(f"query:{query_key}")
        
        if cached_result is not None:
            return cached_result
        
        # تنفيذ الاستعلام
        result = query_func()
        
        # تحويل النتيجة لتنسيق قابل للتخزين المؤقت
        if hasattr(result, 'all'):
            # SQLAlchemy Query object
            serializable_result = [item.to_dict() if hasattr(item, 'to_dict') else str(item) for item in result.all()]
        elif hasattr(result, 'to_dict'):
            # SQLAlchemy Model object
            serializable_result = result.to_dict()
        else:
            serializable_result = result
        
        cache_manager.set(f"query:{query_key}", serializable_result, timeout)
        
        return serializable_result
    
    @staticmethod
    def invalidate_query_cache(pattern):
        """إبطال التخزين المؤقت للاستعلامات"""
        cache_manager.clear(f"query:{pattern}")

class SessionCache:
    """تخزين مؤقت للجلسات"""
    
    @staticmethod
    def get_user_cache(user_id, key):
        """الحصول على بيانات مخزنة مؤقتاً للمستخدم"""
        cache_key = f"user:{user_id}:{key}"
        return cache_manager.get(cache_key)
    
    @staticmethod
    def set_user_cache(user_id, key, value, timeout=3600):
        """تعيين بيانات مخزنة مؤقتاً للمستخدم"""
        cache_key = f"user:{user_id}:{key}"
        return cache_manager.set(cache_key, value, timeout)
    
    @staticmethod
    def clear_user_cache(user_id):
        """مسح التخزين المؤقت للمستخدم"""
        pattern = f"user:{user_id}:*"
        return cache_manager.clear(pattern)

class AssetCache:
    """تخزين مؤقت للأصول الثابتة"""
    
    @staticmethod
    def get_minified_css():
        """الحصول على CSS مضغوط ومخزن مؤقتاً"""
        cached_css = cache_manager.get("assets:minified_css")
        
        if cached_css is not None:
            return cached_css
        
        # ضغط وتجميع ملفات CSS
        css_files = [
            'app/static/css/bootstrap.rtl.min.css',
            'app/static/css/main.css'
        ]
        
        minified_css = ""
        for css_file in css_files:
            try:
                with open(css_file, 'r', encoding='utf-8') as f:
                    css_content = f.read()
                    # ضغط بسيط للـ CSS
                    css_content = css_content.replace('\n', '').replace('  ', ' ')
                    minified_css += css_content
            except FileNotFoundError:
                logger.warning(f"CSS file not found: {css_file}")
        
        # تخزين مؤقت لمدة يوم واحد
        cache_manager.set("assets:minified_css", minified_css, 86400)
        
        return minified_css
    
    @staticmethod
    def get_minified_js():
        """الحصول على JavaScript مضغوط ومخزن مؤقتاً"""
        cached_js = cache_manager.get("assets:minified_js")
        
        if cached_js is not None:
            return cached_js
        
        # ضغط وتجميع ملفات JavaScript
        js_files = [
            'app/static/js/jquery.min.js',
            'app/static/js/bootstrap.bundle.min.js',
            'app/static/js/main.js',
            'app/static/js/i18n.js'
        ]
        
        minified_js = ""
        for js_file in js_files:
            try:
                with open(js_file, 'r', encoding='utf-8') as f:
                    js_content = f.read()
                    minified_js += js_content + '\n'
            except FileNotFoundError:
                logger.warning(f"JS file not found: {js_file}")
        
        # تخزين مؤقت لمدة يوم واحد
        cache_manager.set("assets:minified_js", minified_js, 86400)
        
        return minified_js
    
    @staticmethod
    def clear_asset_cache():
        """مسح تخزين الأصول المؤقت"""
        cache_manager.clear("assets:*")

# وظائف مساعدة للتحسين
def optimize_database_queries():
    """تحسين استعلامات قاعدة البيانات"""
    try:
        # إنشاء فهارس مفقودة
        with db.engine.connect() as conn:
            # فهرس للبحث في المستخدمين
            conn.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_users_active ON users(is_active)")
            
            # فهرس للسجلات
            conn.execute("CREATE INDEX IF NOT EXISTS idx_system_logs_timestamp ON system_logs(timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_system_logs_level ON system_logs(level)")
            
            # فهرس للتنبيهات
            conn.execute("CREATE INDEX IF NOT EXISTS idx_system_alerts_status ON system_alerts(status)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_system_alerts_created ON system_alerts(created_at)")
        
        logger.info("Database indexes optimized")
        return True
    
    except Exception as e:
        logger.error(f"Database optimization failed: {str(e)}")
        return False

def cleanup_expired_cache():
    """تنظيف التخزين المؤقت المنتهي الصلاحية"""
    try:
        if not cache_manager.redis_client:
            # تنظيف التخزين المؤقت في الذاكرة
            expired_keys = []
            for key, expiry in cache_manager.cache_expiry.items():
                if datetime.now() > expiry:
                    expired_keys.append(key)
            
            for key in expired_keys:
                del cache_manager.memory_cache[key]
                del cache_manager.cache_expiry[key]
            
            logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")
            return len(expired_keys)
        
        return 0
    
    except Exception as e:
        logger.error(f"Cache cleanup failed: {str(e)}")
        return 0
