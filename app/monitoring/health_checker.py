#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نظام فحص صحة النظام
System Health Checker
"""

import time
import psutil
import requests
from datetime import datetime, timedelta
from flask import current_app
from app import db
from app.models.system_monitoring import SystemHealth, SystemAlert, PerformanceMetric
import logging

logger = logging.getLogger('accounting_system')

class HealthChecker:
    """فاحص صحة النظام"""
    
    def __init__(self):
        self.checks = {
            'database': self.check_database,
            'disk_space': self.check_disk_space,
            'memory_usage': self.check_memory_usage,
            'cpu_usage': self.check_cpu_usage,
            'response_time': self.check_response_time,
            'log_errors': self.check_log_errors,
            'active_sessions': self.check_active_sessions
        }
        
        # حدود التحذير والخطر
        self.thresholds = {
            'disk_space': {'warning': 80, 'critical': 90},  # نسبة مئوية
            'memory_usage': {'warning': 80, 'critical': 90},  # نسبة مئوية
            'cpu_usage': {'warning': 80, 'critical': 95},  # نسبة مئوية
            'response_time': {'warning': 2.0, 'critical': 5.0},  # ثواني
            'error_rate': {'warning': 10, 'critical': 50}  # أخطاء في الساعة
        }
    
    def run_all_checks(self):
        """تشغيل جميع فحوصات الصحة"""
        results = {}
        overall_status = 'healthy'
        
        for check_name, check_function in self.checks.items():
            try:
                start_time = time.time()
                result = check_function()
                response_time = time.time() - start_time
                
                # تسجيل النتيجة
                SystemHealth.record_check(
                    check_name=check_name,
                    status=result['status'],
                    response_time=response_time,
                    details=result.get('details'),
                    error_message=result.get('error')
                )
                
                results[check_name] = result
                
                # تحديث الحالة العامة
                if result['status'] == 'critical':
                    overall_status = 'critical'
                elif result['status'] == 'warning' and overall_status != 'critical':
                    overall_status = 'warning'
                
                # إنشاء تنبيه إذا لزم الأمر
                if result['status'] in ['warning', 'critical']:
                    self._create_alert(check_name, result)
                
            except Exception as e:
                logger.error(f"Health check failed for {check_name}: {str(e)}")
                
                # تسجيل فشل الفحص
                SystemHealth.record_check(
                    check_name=check_name,
                    status='critical',
                    error_message=str(e)
                )
                
                results[check_name] = {
                    'status': 'critical',
                    'error': str(e)
                }
                overall_status = 'critical'
        
        # حفظ النتائج
        try:
            db.session.commit()
        except Exception as e:
            logger.error(f"Failed to save health check results: {str(e)}")
            db.session.rollback()
        
        return {
            'overall_status': overall_status,
            'checks': results,
            'timestamp': datetime.utcnow()
        }
    
    def check_database(self):
        """فحص اتصال قاعدة البيانات"""
        try:
            start_time = time.time()
            
            # اختبار استعلام بسيط
            result = db.session.execute('SELECT 1').fetchone()
            
            response_time = time.time() - start_time
            
            if result and response_time < 1.0:
                return {
                    'status': 'healthy',
                    'details': {
                        'response_time': response_time,
                        'message': 'Database connection is healthy'
                    }
                }
            elif response_time >= 1.0:
                return {
                    'status': 'warning',
                    'details': {
                        'response_time': response_time,
                        'message': 'Database response is slow'
                    }
                }
            else:
                return {
                    'status': 'critical',
                    'error': 'Database query failed'
                }
                
        except Exception as e:
            return {
                'status': 'critical',
                'error': f'Database connection failed: {str(e)}'
            }
    
    def check_disk_space(self):
        """فحص مساحة القرص"""
        try:
            disk_usage = psutil.disk_usage('/')
            used_percent = (disk_usage.used / disk_usage.total) * 100
            
            details = {
                'used_percent': round(used_percent, 2),
                'free_gb': round(disk_usage.free / (1024**3), 2),
                'total_gb': round(disk_usage.total / (1024**3), 2)
            }
            
            if used_percent >= self.thresholds['disk_space']['critical']:
                return {
                    'status': 'critical',
                    'details': details,
                    'error': f'Disk space critically low: {used_percent:.1f}% used'
                }
            elif used_percent >= self.thresholds['disk_space']['warning']:
                return {
                    'status': 'warning',
                    'details': details,
                    'error': f'Disk space low: {used_percent:.1f}% used'
                }
            else:
                return {
                    'status': 'healthy',
                    'details': details
                }
                
        except Exception as e:
            return {
                'status': 'critical',
                'error': f'Failed to check disk space: {str(e)}'
            }
    
    def check_memory_usage(self):
        """فحص استخدام الذاكرة"""
        try:
            memory = psutil.virtual_memory()
            used_percent = memory.percent
            
            details = {
                'used_percent': used_percent,
                'available_gb': round(memory.available / (1024**3), 2),
                'total_gb': round(memory.total / (1024**3), 2)
            }
            
            if used_percent >= self.thresholds['memory_usage']['critical']:
                return {
                    'status': 'critical',
                    'details': details,
                    'error': f'Memory usage critically high: {used_percent:.1f}%'
                }
            elif used_percent >= self.thresholds['memory_usage']['warning']:
                return {
                    'status': 'warning',
                    'details': details,
                    'error': f'Memory usage high: {used_percent:.1f}%'
                }
            else:
                return {
                    'status': 'healthy',
                    'details': details
                }
                
        except Exception as e:
            return {
                'status': 'critical',
                'error': f'Failed to check memory usage: {str(e)}'
            }
    
    def check_cpu_usage(self):
        """فحص استخدام المعالج"""
        try:
            # قياس استخدام المعالج لمدة ثانية واحدة
            cpu_percent = psutil.cpu_percent(interval=1)
            
            details = {
                'cpu_percent': cpu_percent,
                'cpu_count': psutil.cpu_count(),
                'load_average': psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None
            }
            
            if cpu_percent >= self.thresholds['cpu_usage']['critical']:
                return {
                    'status': 'critical',
                    'details': details,
                    'error': f'CPU usage critically high: {cpu_percent:.1f}%'
                }
            elif cpu_percent >= self.thresholds['cpu_usage']['warning']:
                return {
                    'status': 'warning',
                    'details': details,
                    'error': f'CPU usage high: {cpu_percent:.1f}%'
                }
            else:
                return {
                    'status': 'healthy',
                    'details': details
                }
                
        except Exception as e:
            return {
                'status': 'critical',
                'error': f'Failed to check CPU usage: {str(e)}'
            }
    
    def check_response_time(self):
        """فحص وقت الاستجابة"""
        try:
            # اختبار وقت استجابة الصفحة الرئيسية
            start_time = time.time()
            
            # محاولة الوصول للصفحة الرئيسية
            base_url = current_app.config.get('SERVER_NAME', 'localhost:5000')
            if not base_url.startswith('http'):
                base_url = f'http://{base_url}'
            
            response = requests.get(f'{base_url}/', timeout=10)
            response_time = time.time() - start_time
            
            details = {
                'response_time': response_time,
                'status_code': response.status_code,
                'url': f'{base_url}/'
            }
            
            if response_time >= self.thresholds['response_time']['critical']:
                return {
                    'status': 'critical',
                    'details': details,
                    'error': f'Response time critically slow: {response_time:.2f}s'
                }
            elif response_time >= self.thresholds['response_time']['warning']:
                return {
                    'status': 'warning',
                    'details': details,
                    'error': f'Response time slow: {response_time:.2f}s'
                }
            else:
                return {
                    'status': 'healthy',
                    'details': details
                }
                
        except Exception as e:
            return {
                'status': 'critical',
                'error': f'Failed to check response time: {str(e)}'
            }
    
    def check_log_errors(self):
        """فحص معدل الأخطاء في السجلات"""
        try:
            from app.models.system_monitoring import SystemLog
            
            # عدد الأخطاء في الساعة الماضية
            one_hour_ago = datetime.utcnow() - timedelta(hours=1)
            error_count = SystemLog.query.filter(
                SystemLog.timestamp > one_hour_ago,
                SystemLog.level.in_(['ERROR', 'CRITICAL'])
            ).count()
            
            details = {
                'error_count': error_count,
                'time_period': '1 hour'
            }
            
            if error_count >= self.thresholds['error_rate']['critical']:
                return {
                    'status': 'critical',
                    'details': details,
                    'error': f'High error rate: {error_count} errors in the last hour'
                }
            elif error_count >= self.thresholds['error_rate']['warning']:
                return {
                    'status': 'warning',
                    'details': details,
                    'error': f'Elevated error rate: {error_count} errors in the last hour'
                }
            else:
                return {
                    'status': 'healthy',
                    'details': details
                }
                
        except Exception as e:
            return {
                'status': 'critical',
                'error': f'Failed to check log errors: {str(e)}'
            }
    
    def check_active_sessions(self):
        """فحص الجلسات النشطة"""
        try:
            from app.models.user_enhanced import User
            
            # عدد المستخدمين النشطين في آخر 30 دقيقة
            thirty_minutes_ago = datetime.utcnow() - timedelta(minutes=30)
            active_users = User.query.filter(
                User.last_seen > thirty_minutes_ago,
                User.is_active == True
            ).count()
            
            details = {
                'active_users': active_users,
                'time_period': '30 minutes'
            }
            
            # هذا فحص إعلامي فقط
            return {
                'status': 'healthy',
                'details': details
            }
            
        except Exception as e:
            return {
                'status': 'warning',
                'error': f'Failed to check active sessions: {str(e)}'
            }
    
    def _create_alert(self, check_name, result):
        """إنشاء تنبيه للمشاكل"""
        try:
            # تحقق من وجود تنبيه مشابه نشط
            existing_alert = SystemAlert.query.filter(
                SystemAlert.alert_type == 'health_check',
                SystemAlert.status == 'active',
                SystemAlert.source_data['check_name'].astext == check_name
            ).first()
            
            if existing_alert:
                return  # تنبيه موجود بالفعل
            
            # إنشاء تنبيه جديد
            title = f"Health Check Alert: {check_name}"
            message = result.get('error', f"Health check {check_name} status: {result['status']}")
            
            SystemAlert.create_alert(
                alert_type='health_check',
                severity=result['status'],
                title=title,
                message=message,
                source_data={
                    'check_name': check_name,
                    'details': result.get('details', {}),
                    'timestamp': datetime.utcnow().isoformat()
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to create alert for {check_name}: {str(e)}")

# إنشاء مثيل فاحص الصحة
health_checker = HealthChecker()
