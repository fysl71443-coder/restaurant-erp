#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نماذج مراقبة النظام والسجلات
System Monitoring and Logging Models
"""

from datetime import datetime, timedelta
from app import db
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy import Index, text
import json

class SystemLog(db.Model):
    """نموذج سجلات النظام"""
    __tablename__ = 'system_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # معلومات السجل الأساسية
    level = db.Column(db.String(20), nullable=False, index=True)  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    logger_name = db.Column(db.String(100), nullable=False, index=True)
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # معلومات الكود
    module = db.Column(db.String(100))
    function = db.Column(db.String(100))
    line_number = db.Column(db.Integer)
    
    # معلومات الطلب
    request_id = db.Column(db.String(50), index=True)
    method = db.Column(db.String(10))
    url = db.Column(db.Text)
    
    # معلومات المستخدم
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    ip_address = db.Column(db.String(45))  # دعم IPv6
    user_agent = db.Column(db.Text)
    
    # معلومات الاستثناء
    exception_type = db.Column(db.String(100))
    exception_message = db.Column(db.Text)
    stack_trace = db.Column(db.Text)
    
    # بيانات إضافية
    extra_data = db.Column(JSON)
    
    # علاقات
    user = db.relationship('User', backref='system_logs')
    
    # فهارس مركبة لتحسين الأداء
    __table_args__ = (
        Index('idx_logs_level_timestamp', 'level', 'timestamp'),
        Index('idx_logs_user_timestamp', 'user_id', 'timestamp'),
        Index('idx_logs_logger_timestamp', 'logger_name', 'timestamp'),
    )
    
    def __repr__(self):
        return f'<SystemLog {self.level}: {self.message[:50]}...>'
    
    @classmethod
    def log_event(cls, level, logger_name, message, **kwargs):
        """إنشاء سجل جديد"""
        log_entry = cls(
            level=level.upper(),
            logger_name=logger_name,
            message=message,
            **kwargs
        )
        db.session.add(log_entry)
        return log_entry
    
    @classmethod
    def get_recent_logs(cls, hours=24, level=None, limit=100):
        """الحصول على السجلات الحديثة"""
        query = cls.query.filter(
            cls.timestamp > datetime.utcnow() - timedelta(hours=hours)
        )
        
        if level:
            query = query.filter(cls.level == level.upper())
        
        return query.order_by(cls.timestamp.desc()).limit(limit).all()
    
    @classmethod
    def get_error_summary(cls, hours=24):
        """ملخص الأخطاء"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        return db.session.query(
            cls.level,
            db.func.count(cls.id).label('count')
        ).filter(
            cls.timestamp > cutoff_time,
            cls.level.in_(['ERROR', 'CRITICAL'])
        ).group_by(cls.level).all()
    
    @classmethod
    def cleanup_old_logs(cls, days=30):
        """تنظيف السجلات القديمة"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        deleted_count = cls.query.filter(cls.timestamp < cutoff_date).delete()
        db.session.commit()
        return deleted_count

class PerformanceMetric(db.Model):
    """نموذج مقاييس الأداء"""
    __tablename__ = 'performance_metrics'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # معلومات المقياس
    metric_name = db.Column(db.String(100), nullable=False, index=True)
    value = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(20), default='ms')
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # معلومات السياق
    category = db.Column(db.String(50), index=True)  # database, api, ui, etc.
    source = db.Column(db.String(100))  # اسم الوظيفة أو المسار
    
    # بيانات إضافية
    metadata = db.Column(JSON)
    
    # فهارس
    __table_args__ = (
        Index('idx_metrics_name_timestamp', 'metric_name', 'timestamp'),
        Index('idx_metrics_category_timestamp', 'category', 'timestamp'),
    )
    
    def __repr__(self):
        return f'<PerformanceMetric {self.metric_name}: {self.value} {self.unit}>'
    
    @classmethod
    def record_metric(cls, name, value, unit='ms', category=None, source=None, **metadata):
        """تسجيل مقياس أداء"""
        metric = cls(
            metric_name=name,
            value=value,
            unit=unit,
            category=category,
            source=source,
            metadata=metadata if metadata else None
        )
        db.session.add(metric)
        return metric
    
    @classmethod
    def get_average(cls, metric_name, hours=24):
        """متوسط مقياس خلال فترة"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        result = db.session.query(
            db.func.avg(cls.value).label('average')
        ).filter(
            cls.metric_name == metric_name,
            cls.timestamp > cutoff_time
        ).first()
        
        return result.average if result.average else 0
    
    @classmethod
    def get_trend_data(cls, metric_name, hours=24, interval_minutes=60):
        """بيانات الاتجاه لمقياس"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        # تجميع البيانات حسب فترات زمنية
        interval = text(f"date_trunc('hour', timestamp)")
        
        return db.session.query(
            interval.label('time_bucket'),
            db.func.avg(cls.value).label('avg_value'),
            db.func.min(cls.value).label('min_value'),
            db.func.max(cls.value).label('max_value'),
            db.func.count(cls.id).label('count')
        ).filter(
            cls.metric_name == metric_name,
            cls.timestamp > cutoff_time
        ).group_by('time_bucket').order_by('time_bucket').all()

class SystemAlert(db.Model):
    """نموذج تنبيهات النظام"""
    __tablename__ = 'system_alerts'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # معلومات التنبيه
    alert_type = db.Column(db.String(50), nullable=False, index=True)  # error, performance, security
    severity = db.Column(db.String(20), nullable=False, index=True)  # low, medium, high, critical
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    
    # معلومات التوقيت
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    acknowledged_at = db.Column(db.DateTime)
    resolved_at = db.Column(db.DateTime)
    
    # معلومات المعالجة
    acknowledged_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    resolved_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # بيانات إضافية
    source_data = db.Column(JSON)
    resolution_notes = db.Column(db.Text)
    
    # حالة التنبيه
    status = db.Column(db.String(20), default='active', index=True)  # active, acknowledged, resolved
    
    # علاقات
    acknowledged_by = db.relationship('User', foreign_keys=[acknowledged_by_id])
    resolved_by = db.relationship('User', foreign_keys=[resolved_by_id])
    
    def __repr__(self):
        return f'<SystemAlert {self.alert_type}: {self.title}>'
    
    @classmethod
    def create_alert(cls, alert_type, severity, title, message, source_data=None):
        """إنشاء تنبيه جديد"""
        alert = cls(
            alert_type=alert_type,
            severity=severity,
            title=title,
            message=message,
            source_data=source_data
        )
        db.session.add(alert)
        return alert
    
    @classmethod
    def get_active_alerts(cls, severity=None):
        """الحصول على التنبيهات النشطة"""
        query = cls.query.filter(cls.status == 'active')
        
        if severity:
            query = query.filter(cls.severity == severity)
        
        return query.order_by(cls.created_at.desc()).all()
    
    @classmethod
    def get_alert_summary(cls, hours=24):
        """ملخص التنبيهات"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        return db.session.query(
            cls.alert_type,
            cls.severity,
            db.func.count(cls.id).label('count')
        ).filter(
            cls.created_at > cutoff_time
        ).group_by(cls.alert_type, cls.severity).all()
    
    def acknowledge(self, user_id):
        """تأكيد التنبيه"""
        self.acknowledged_at = datetime.utcnow()
        self.acknowledged_by_id = user_id
        self.status = 'acknowledged'
    
    def resolve(self, user_id, notes=None):
        """حل التنبيه"""
        self.resolved_at = datetime.utcnow()
        self.resolved_by_id = user_id
        self.resolution_notes = notes
        self.status = 'resolved'

class SystemHealth(db.Model):
    """نموذج صحة النظام"""
    __tablename__ = 'system_health'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # معلومات الفحص
    check_name = db.Column(db.String(100), nullable=False, index=True)
    status = db.Column(db.String(20), nullable=False, index=True)  # healthy, warning, critical
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # تفاصيل الفحص
    response_time = db.Column(db.Float)  # بالثواني
    details = db.Column(JSON)
    error_message = db.Column(db.Text)
    
    # معلومات إضافية
    metadata = db.Column(JSON)
    
    def __repr__(self):
        return f'<SystemHealth {self.check_name}: {self.status}>'
    
    @classmethod
    def record_check(cls, check_name, status, response_time=None, details=None, error_message=None, **metadata):
        """تسجيل فحص صحة"""
        health_check = cls(
            check_name=check_name,
            status=status,
            response_time=response_time,
            details=details,
            error_message=error_message,
            metadata=metadata if metadata else None
        )
        db.session.add(health_check)
        return health_check
    
    @classmethod
    def get_latest_status(cls):
        """أحدث حالة لجميع الفحوصات"""
        subquery = db.session.query(
            cls.check_name,
            db.func.max(cls.timestamp).label('latest_timestamp')
        ).group_by(cls.check_name).subquery()
        
        return db.session.query(cls).join(
            subquery,
            (cls.check_name == subquery.c.check_name) &
            (cls.timestamp == subquery.c.latest_timestamp)
        ).all()
    
    @classmethod
    def get_health_summary(cls):
        """ملخص صحة النظام"""
        latest_checks = cls.get_latest_status()
        
        summary = {
            'healthy': 0,
            'warning': 0,
            'critical': 0,
            'total': len(latest_checks)
        }
        
        for check in latest_checks:
            summary[check.status] += 1
        
        # حساب النسبة المئوية للصحة
        if summary['total'] > 0:
            summary['health_percentage'] = (summary['healthy'] / summary['total']) * 100
        else:
            summary['health_percentage'] = 100
        
        return summary

class UserActivity(db.Model):
    """نموذج نشاط المستخدمين"""
    __tablename__ = 'user_activities'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # معلومات النشاط
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    action = db.Column(db.String(100), nullable=False, index=True)
    resource_type = db.Column(db.String(50), index=True)  # customer, invoice, payment, etc.
    resource_id = db.Column(db.Integer, index=True)
    
    # تفاصيل النشاط
    description = db.Column(db.Text)
    old_values = db.Column(JSON)  # القيم القديمة (للتعديل)
    new_values = db.Column(JSON)  # القيم الجديدة (للتعديل)
    
    # معلومات السياق
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    session_id = db.Column(db.String(100))
    
    # علاقات
    user = db.relationship('User', backref='activities')
    
    # فهارس
    __table_args__ = (
        Index('idx_activities_user_timestamp', 'user_id', 'timestamp'),
        Index('idx_activities_action_timestamp', 'action', 'timestamp'),
        Index('idx_activities_resource', 'resource_type', 'resource_id'),
    )
    
    def __repr__(self):
        return f'<UserActivity {self.user.username}: {self.action}>'
    
    @classmethod
    def log_activity(cls, user_id, action, description=None, resource_type=None, resource_id=None, 
                    old_values=None, new_values=None, **context):
        """تسجيل نشاط مستخدم"""
        activity = cls(
            user_id=user_id,
            action=action,
            description=description,
            resource_type=resource_type,
            resource_id=resource_id,
            old_values=old_values,
            new_values=new_values,
            **context
        )
        db.session.add(activity)
        return activity
    
    @classmethod
    def get_user_activities(cls, user_id, limit=50):
        """أنشطة مستخدم محدد"""
        return cls.query.filter_by(user_id=user_id)\
                       .order_by(cls.timestamp.desc())\
                       .limit(limit).all()
    
    @classmethod
    def get_recent_activities(cls, hours=24, limit=100):
        """الأنشطة الحديثة"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        return cls.query.filter(cls.timestamp > cutoff_time)\
                       .order_by(cls.timestamp.desc())\
                       .limit(limit).all()
    
    @classmethod
    def get_activity_summary(cls, hours=24):
        """ملخص الأنشطة"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        return db.session.query(
            cls.action,
            db.func.count(cls.id).label('count')
        ).filter(
            cls.timestamp > cutoff_time
        ).group_by(cls.action).order_by(db.func.count(cls.id).desc()).all()
