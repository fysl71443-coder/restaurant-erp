#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
مسارات نظام السجلات والمراقبة
Logging and Monitoring Routes
"""

from flask import render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from app.logging import logging_bp
from app.models.system_monitoring import SystemLog, PerformanceMetric, SystemAlert, SystemHealth, UserActivity
from app.models.user_enhanced import User
from app.monitoring.health_checker import health_checker
from app.notifications.alert_manager import alert_manager
from app.decorators import admin_required
from app import db
import json

@logging_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """لوحة مراقبة النظام"""
    # إحصائيات عامة
    stats = {
        'total_logs': SystemLog.query.count(),
        'errors_today': SystemLog.query.filter(
            SystemLog.level.in_(['ERROR', 'CRITICAL']),
            SystemLog.timestamp > datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        ).count(),
        'active_alerts': SystemAlert.query.filter_by(status='active').count(),
        'active_users': User.query.filter(
            User.last_seen > datetime.utcnow() - timedelta(minutes=30),
            User.is_active == True
        ).count()
    }
    
    # أحدث السجلات
    recent_logs = SystemLog.get_recent_logs(hours=24, limit=10)
    
    # التنبيهات النشطة
    active_alerts = SystemAlert.get_active_alerts()
    
    # صحة النظام
    health_summary = SystemHealth.get_health_summary()
    
    # أحدث الأنشطة
    recent_activities = UserActivity.get_recent_activities(hours=24, limit=10)
    
    return render_template('logging/dashboard.html',
                         stats=stats,
                         recent_logs=recent_logs,
                         active_alerts=active_alerts,
                         health_summary=health_summary,
                         recent_activities=recent_activities)

@logging_bp.route('/logs')
@login_required
@admin_required
def logs():
    """عرض السجلات"""
    page = request.args.get('page', 1, type=int)
    level = request.args.get('level')
    logger_name = request.args.get('logger')
    search = request.args.get('search')
    
    # بناء الاستعلام
    query = SystemLog.query
    
    if level:
        query = query.filter(SystemLog.level == level.upper())
    
    if logger_name:
        query = query.filter(SystemLog.logger_name == logger_name)
    
    if search:
        query = query.filter(SystemLog.message.contains(search))
    
    # ترتيب وتقسيم الصفحات
    logs = query.order_by(SystemLog.timestamp.desc()).paginate(
        page=page, per_page=50, error_out=False
    )
    
    # قائمة المستويات والسجلات المتاحة
    levels = db.session.query(SystemLog.level.distinct()).all()
    loggers = db.session.query(SystemLog.logger_name.distinct()).all()
    
    return render_template('logging/logs.html',
                         logs=logs,
                         levels=[l[0] for l in levels],
                         loggers=[l[0] for l in loggers],
                         current_level=level,
                         current_logger=logger_name,
                         current_search=search)

@logging_bp.route('/alerts')
@login_required
@admin_required
def alerts():
    """عرض التنبيهات"""
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', 'active')
    alert_type = request.args.get('type')
    severity = request.args.get('severity')
    
    # بناء الاستعلام
    query = SystemAlert.query
    
    if status:
        query = query.filter(SystemAlert.status == status)
    
    if alert_type:
        query = query.filter(SystemAlert.alert_type == alert_type)
    
    if severity:
        query = query.filter(SystemAlert.severity == severity)
    
    # ترتيب وتقسيم الصفحات
    alerts = query.order_by(SystemAlert.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    # إحصائيات التنبيهات
    alert_stats = SystemAlert.get_alert_summary(hours=24)
    
    return render_template('logging/alerts.html',
                         alerts=alerts,
                         alert_stats=alert_stats,
                         current_status=status,
                         current_type=alert_type,
                         current_severity=severity)

@logging_bp.route('/health')
@login_required
@admin_required
def health():
    """عرض صحة النظام"""
    # تشغيل فحوصات الصحة
    health_results = health_checker.run_all_checks()
    
    # أحدث حالة لكل فحص
    latest_checks = SystemHealth.get_latest_status()
    
    # ملخص الصحة
    health_summary = SystemHealth.get_health_summary()
    
    return render_template('logging/health.html',
                         health_results=health_results,
                         latest_checks=latest_checks,
                         health_summary=health_summary)

@logging_bp.route('/performance')
@login_required
@admin_required
def performance():
    """عرض مقاييس الأداء"""
    # مقاييس الأداء الحديثة
    metrics = {}
    
    # وقت الاستجابة
    response_time_avg = PerformanceMetric.get_average('response_time', hours=24)
    metrics['response_time'] = {
        'current': response_time_avg,
        'trend': PerformanceMetric.get_trend_data('response_time', hours=24)
    }
    
    # استخدام الذاكرة
    memory_avg = PerformanceMetric.get_average('memory_usage', hours=24)
    metrics['memory_usage'] = {
        'current': memory_avg,
        'trend': PerformanceMetric.get_trend_data('memory_usage', hours=24)
    }
    
    # استخدام المعالج
    cpu_avg = PerformanceMetric.get_average('cpu_usage', hours=24)
    metrics['cpu_usage'] = {
        'current': cpu_avg,
        'trend': PerformanceMetric.get_trend_data('cpu_usage', hours=24)
    }
    
    return render_template('logging/performance.html', metrics=metrics)

@logging_bp.route('/activities')
@login_required
@admin_required
def activities():
    """عرض أنشطة المستخدمين"""
    page = request.args.get('page', 1, type=int)
    user_id = request.args.get('user_id', type=int)
    action = request.args.get('action')
    
    # بناء الاستعلام
    query = UserActivity.query
    
    if user_id:
        query = query.filter(UserActivity.user_id == user_id)
    
    if action:
        query = query.filter(UserActivity.action == action)
    
    # ترتيب وتقسيم الصفحات
    activities = query.order_by(UserActivity.timestamp.desc()).paginate(
        page=page, per_page=50, error_out=False
    )
    
    # ملخص الأنشطة
    activity_summary = UserActivity.get_activity_summary(hours=24)
    
    # قائمة المستخدمين والإجراءات
    users = User.query.filter_by(is_active=True).all()
    actions = db.session.query(UserActivity.action.distinct()).all()
    
    return render_template('logging/activities.html',
                         activities=activities,
                         activity_summary=activity_summary,
                         users=users,
                         actions=[a[0] for a in actions],
                         current_user_id=user_id,
                         current_action=action)

# API Routes
@logging_bp.route('/api/health-check')
@login_required
@admin_required
def api_health_check():
    """API فحص صحة النظام"""
    results = health_checker.run_all_checks()
    return jsonify(results)

@logging_bp.route('/api/stats')
@login_required
@admin_required
def api_stats():
    """API إحصائيات النظام"""
    hours = request.args.get('hours', 24, type=int)
    
    stats = {
        'logs': {
            'total': SystemLog.query.count(),
            'errors': SystemLog.query.filter(
                SystemLog.level.in_(['ERROR', 'CRITICAL']),
                SystemLog.timestamp > datetime.utcnow() - timedelta(hours=hours)
            ).count(),
            'warnings': SystemLog.query.filter(
                SystemLog.level == 'WARNING',
                SystemLog.timestamp > datetime.utcnow() - timedelta(hours=hours)
            ).count()
        },
        'alerts': {
            'active': SystemAlert.query.filter_by(status='active').count(),
            'total': SystemAlert.query.filter(
                SystemAlert.created_at > datetime.utcnow() - timedelta(hours=hours)
            ).count()
        },
        'users': {
            'active': User.query.filter(
                User.last_seen > datetime.utcnow() - timedelta(minutes=30),
                User.is_active == True
            ).count(),
            'total': User.query.filter_by(is_active=True).count()
        },
        'health': SystemHealth.get_health_summary()
    }
    
    return jsonify(stats)

@logging_bp.route('/api/performance-data')
@login_required
@admin_required
def api_performance_data():
    """API بيانات الأداء"""
    metric = request.args.get('metric', 'response_time')
    hours = request.args.get('hours', 24, type=int)
    
    trend_data = PerformanceMetric.get_trend_data(metric, hours=hours)
    
    # تحويل البيانات لتنسيق Chart.js
    labels = []
    values = []
    
    for data_point in trend_data:
        labels.append(data_point.time_bucket.strftime('%H:%M'))
        values.append(float(data_point.avg_value) if data_point.avg_value else 0)
    
    return jsonify({
        'labels': labels,
        'values': values,
        'metric': metric
    })

@logging_bp.route('/api/alert/<int:alert_id>/acknowledge', methods=['POST'])
@login_required
@admin_required
def api_acknowledge_alert(alert_id):
    """API تأكيد التنبيه"""
    alert = SystemAlert.query.get_or_404(alert_id)
    
    alert.acknowledge(current_user.id)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'تم تأكيد التنبيه بنجاح'
    })

@logging_bp.route('/api/alert/<int:alert_id>/resolve', methods=['POST'])
@login_required
@admin_required
def api_resolve_alert(alert_id):
    """API حل التنبيه"""
    alert = SystemAlert.query.get_or_404(alert_id)
    data = request.get_json()
    
    notes = data.get('notes', '')
    alert.resolve(current_user.id, notes)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'تم حل التنبيه بنجاح'
    })

@logging_bp.route('/api/cleanup', methods=['POST'])
@login_required
@admin_required
def api_cleanup():
    """API تنظيف البيانات القديمة"""
    data = request.get_json()
    days = data.get('days', 30)
    
    # تنظيف السجلات القديمة
    logs_deleted = SystemLog.cleanup_old_logs(days=days)
    
    # تنظيف التنبيهات القديمة
    alerts_deleted = alert_manager.cleanup_old_alerts(days=days)
    
    return jsonify({
        'success': True,
        'message': f'تم حذف {logs_deleted} سجل و {alerts_deleted} تنبيه',
        'logs_deleted': logs_deleted,
        'alerts_deleted': alerts_deleted
    })

@logging_bp.route('/export/logs')
@login_required
@admin_required
def export_logs():
    """تصدير السجلات"""
    # TODO: تطبيق تصدير السجلات إلى CSV/Excel
    flash('ميزة التصدير قيد التطوير', 'info')
    return redirect(url_for('logging.logs'))

@logging_bp.route('/export/alerts')
@login_required
@admin_required
def export_alerts():
    """تصدير التنبيهات"""
    # TODO: تطبيق تصدير التنبيهات إلى CSV/Excel
    flash('ميزة التصدير قيد التطوير', 'info')
    return redirect(url_for('logging.alerts'))
