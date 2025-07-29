#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
سكريبت مراقبة صحة النظام
System Health Monitoring Script
"""

import os
import sys
import time
import schedule
import logging
from datetime import datetime

# إضافة مسار التطبيق
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.monitoring.health_checker import health_checker
from app.notifications.alert_manager import alert_manager
from app.models.system_monitoring import PerformanceMetric
import psutil

# إعداد السجلات
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/health_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class HealthMonitor:
    """مراقب صحة النظام"""
    
    def __init__(self, app):
        self.app = app
        self.last_check_time = None
        self.consecutive_failures = {}
        
    def run_health_checks(self):
        """تشغيل فحوصات الصحة"""
        with self.app.app_context():
            try:
                logger.info("Starting health checks...")
                
                # تشغيل جميع فحوصات الصحة
                results = health_checker.run_all_checks()
                
                # تسجيل النتائج
                self._log_results(results)
                
                # إرسال تنبيهات إذا لزم الأمر
                self._handle_alerts(results)
                
                # تسجيل مقاييس الأداء
                self._record_performance_metrics()
                
                self.last_check_time = datetime.utcnow()
                logger.info(f"Health checks completed. Overall status: {results['overall_status']}")
                
            except Exception as e:
                logger.error(f"Health check failed: {str(e)}")
                
                # إرسال تنبيه فشل المراقبة
                alert_manager.send_error_notification(e, {
                    'context': 'health_monitor',
                    'timestamp': datetime.utcnow().isoformat()
                })
    
    def _log_results(self, results):
        """تسجيل نتائج الفحوصات"""
        for check_name, result in results['checks'].items():
            status = result['status']
            
            if status == 'healthy':
                logger.info(f"✅ {check_name}: {status}")
            elif status == 'warning':
                logger.warning(f"⚠️  {check_name}: {status} - {result.get('error', 'No details')}")
            else:  # critical
                logger.error(f"❌ {check_name}: {status} - {result.get('error', 'No details')}")
    
    def _handle_alerts(self, results):
        """معالجة التنبيهات"""
        for check_name, result in results['checks'].items():
            status = result['status']
            
            if status in ['warning', 'critical']:
                # تتبع الفشل المتتالي
                if check_name not in self.consecutive_failures:
                    self.consecutive_failures[check_name] = 0
                
                self.consecutive_failures[check_name] += 1
                
                # إرسال تنبيه بعد فشلين متتاليين
                if self.consecutive_failures[check_name] >= 2:
                    alert_manager.send_health_check_alert(
                        check_name=check_name,
                        status=status,
                        details=result.get('details', {})
                    )
            else:
                # إعادة تعيين عداد الفشل
                if check_name in self.consecutive_failures:
                    del self.consecutive_failures[check_name]
    
    def _record_performance_metrics(self):
        """تسجيل مقاييس الأداء"""
        try:
            # استخدام الذاكرة
            memory = psutil.virtual_memory()
            PerformanceMetric.record_metric(
                name='memory_usage',
                value=memory.percent,
                unit='%',
                category='system'
            )
            
            # استخدام المعالج
            cpu_percent = psutil.cpu_percent(interval=1)
            PerformanceMetric.record_metric(
                name='cpu_usage',
                value=cpu_percent,
                unit='%',
                category='system'
            )
            
            # استخدام القرص
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            PerformanceMetric.record_metric(
                name='disk_usage',
                value=disk_percent,
                unit='%',
                category='system'
            )
            
            # عدد العمليات
            process_count = len(psutil.pids())
            PerformanceMetric.record_metric(
                name='process_count',
                value=process_count,
                unit='count',
                category='system'
            )
            
            # حفظ المقاييس
            db.session.commit()
            
        except Exception as e:
            logger.error(f"Failed to record performance metrics: {str(e)}")
            db.session.rollback()
    
    def cleanup_old_data(self):
        """تنظيف البيانات القديمة"""
        with self.app.app_context():
            try:
                logger.info("Starting cleanup of old data...")
                
                # تنظيف السجلات القديمة (أكثر من 30 يوم)
                from app.models.system_monitoring import SystemLog
                logs_deleted = SystemLog.cleanup_old_logs(days=30)
                
                # تنظيف التنبيهات المحلولة القديمة (أكثر من 30 يوم)
                alerts_deleted = alert_manager.cleanup_old_alerts(days=30)
                
                # تنظيف مقاييس الأداء القديمة (أكثر من 90 يوم)
                from datetime import timedelta
                cutoff_date = datetime.utcnow() - timedelta(days=90)
                metrics_deleted = PerformanceMetric.query.filter(
                    PerformanceMetric.timestamp < cutoff_date
                ).delete()
                
                db.session.commit()
                
                logger.info(f"Cleanup completed: {logs_deleted} logs, {alerts_deleted} alerts, {metrics_deleted} metrics deleted")
                
            except Exception as e:
                logger.error(f"Cleanup failed: {str(e)}")
                db.session.rollback()
    
    def generate_daily_report(self):
        """إنشاء تقرير يومي"""
        with self.app.app_context():
            try:
                logger.info("Generating daily health report...")
                
                from app.models.system_monitoring import SystemLog, SystemAlert, SystemHealth
                
                # إحصائيات اليوم
                today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
                
                stats = {
                    'date': today_start.strftime('%Y-%m-%d'),
                    'total_logs': SystemLog.query.filter(SystemLog.timestamp >= today_start).count(),
                    'error_logs': SystemLog.query.filter(
                        SystemLog.timestamp >= today_start,
                        SystemLog.level.in_(['ERROR', 'CRITICAL'])
                    ).count(),
                    'total_alerts': SystemAlert.query.filter(SystemAlert.created_at >= today_start).count(),
                    'health_summary': SystemHealth.get_health_summary()
                }
                
                # إرسال التقرير للمديرين (يمكن تطويره لاحقاً)
                logger.info(f"Daily report: {stats}")
                
            except Exception as e:
                logger.error(f"Failed to generate daily report: {str(e)}")

def main():
    """الدالة الرئيسية"""
    # إنشاء التطبيق
    app = create_app()
    
    # إنشاء مراقب الصحة
    monitor = HealthMonitor(app)
    
    # جدولة المهام
    schedule.every(5).minutes.do(monitor.run_health_checks)  # كل 5 دقائق
    schedule.every().hour.do(monitor.cleanup_old_data)  # كل ساعة
    schedule.every().day.at("08:00").do(monitor.generate_daily_report)  # يومياً في 8 صباحاً
    
    logger.info("Health monitor started. Scheduled tasks:")
    logger.info("- Health checks: every 5 minutes")
    logger.info("- Data cleanup: every hour")
    logger.info("- Daily report: every day at 08:00")
    
    # تشغيل فحص أولي
    monitor.run_health_checks()
    
    # حلقة المراقبة الرئيسية
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # فحص كل دقيقة
            
    except KeyboardInterrupt:
        logger.info("Health monitor stopped by user")
    except Exception as e:
        logger.error(f"Health monitor crashed: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    # إنشاء مجلد السجلات إذا لم يكن موجود
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    main()
