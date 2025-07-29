#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
مدير التنبيهات والإشعارات
Alert and Notification Manager
"""

import smtplib
import logging
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app, render_template_string
from app import db
from app.models.system_monitoring import SystemAlert
from app.models.user_enhanced import User

logger = logging.getLogger('accounting_system')

class AlertManager:
    """مدير التنبيهات"""
    
    def __init__(self):
        self.email_templates = {
            'error': self._get_error_email_template(),
            'performance': self._get_performance_email_template(),
            'security': self._get_security_email_template(),
            'health_check': self._get_health_check_email_template()
        }
    
    def send_error_notification(self, exception, request_info=None):
        """إرسال إشعار خطأ"""
        try:
            # إنشاء تنبيه في قاعدة البيانات
            alert = SystemAlert.create_alert(
                alert_type='error',
                severity='critical',
                title=f'Application Error: {type(exception).__name__}',
                message=str(exception),
                source_data={
                    'exception_type': type(exception).__name__,
                    'exception_message': str(exception),
                    'request_info': request_info,
                    'timestamp': datetime.utcnow().isoformat()
                }
            )
            
            # إرسال بريد إلكتروني للمديرين
            self._send_email_alert(alert)
            
            db.session.commit()
            
        except Exception as e:
            logger.error(f"Failed to send error notification: {str(e)}")
    
    def send_performance_alert(self, metric_name, value, threshold, details=None):
        """إرسال تنبيه أداء"""
        try:
            severity = 'critical' if value > threshold * 1.5 else 'warning'
            
            alert = SystemAlert.create_alert(
                alert_type='performance',
                severity=severity,
                title=f'Performance Alert: {metric_name}',
                message=f'{metric_name} is {value}, exceeding threshold of {threshold}',
                source_data={
                    'metric_name': metric_name,
                    'value': value,
                    'threshold': threshold,
                    'details': details or {},
                    'timestamp': datetime.utcnow().isoformat()
                }
            )
            
            # إرسال بريد إلكتروني إذا كان حرج
            if severity == 'critical':
                self._send_email_alert(alert)
            
            db.session.commit()
            
        except Exception as e:
            logger.error(f"Failed to send performance alert: {str(e)}")
    
    def send_security_alert(self, event_type, details, severity='warning'):
        """إرسال تنبيه أمني"""
        try:
            alert = SystemAlert.create_alert(
                alert_type='security',
                severity=severity,
                title=f'Security Alert: {event_type}',
                message=f'Security event detected: {event_type}',
                source_data={
                    'event_type': event_type,
                    'details': details,
                    'timestamp': datetime.utcnow().isoformat()
                }
            )
            
            # إرسال بريد إلكتروني للتنبيهات الأمنية
            self._send_email_alert(alert)
            
            db.session.commit()
            
        except Exception as e:
            logger.error(f"Failed to send security alert: {str(e)}")
    
    def send_health_check_alert(self, check_name, status, details):
        """إرسال تنبيه فحص الصحة"""
        try:
            alert = SystemAlert.create_alert(
                alert_type='health_check',
                severity=status,
                title=f'Health Check Alert: {check_name}',
                message=f'Health check {check_name} status: {status}',
                source_data={
                    'check_name': check_name,
                    'status': status,
                    'details': details,
                    'timestamp': datetime.utcnow().isoformat()
                }
            )
            
            # إرسال بريد إلكتروني للحالات الحرجة
            if status == 'critical':
                self._send_email_alert(alert)
            
            db.session.commit()
            
        except Exception as e:
            logger.error(f"Failed to send health check alert: {str(e)}")
    
    def _send_email_alert(self, alert):
        """إرسال تنبيه عبر البريد الإلكتروني"""
        try:
            # الحصول على قائمة المديرين
            admin_users = User.query.filter(
                User.is_admin == True,
                User.is_active == True,
                User.email.isnot(None)
            ).all()
            
            if not admin_users:
                logger.warning("No admin users found to send alert email")
                return
            
            # إعداد البريد الإلكتروني
            smtp_config = current_app.config.get('MAIL_SETTINGS', {})
            if not smtp_config:
                logger.warning("No email configuration found")
                return
            
            # إنشاء محتوى البريد
            template = self.email_templates.get(alert.alert_type, self.email_templates['error'])
            
            subject = f"[{alert.severity.upper()}] {alert.title}"
            body = render_template_string(template, alert=alert)
            
            # إرسال البريد لكل مدير
            for admin in admin_users:
                self._send_email(admin.email, subject, body, smtp_config)
            
        except Exception as e:
            logger.error(f"Failed to send email alert: {str(e)}")
    
    def _send_email(self, to_email, subject, body, smtp_config):
        """إرسال بريد إلكتروني"""
        try:
            # إنشاء الرسالة
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = smtp_config.get('MAIL_USERNAME')
            msg['To'] = to_email
            
            # إضافة المحتوى
            html_part = MIMEText(body, 'html', 'utf-8')
            msg.attach(html_part)
            
            # إرسال البريد
            with smtplib.SMTP(smtp_config.get('MAIL_SERVER'), smtp_config.get('MAIL_PORT', 587)) as server:
                if smtp_config.get('MAIL_USE_TLS'):
                    server.starttls()
                
                if smtp_config.get('MAIL_USERNAME') and smtp_config.get('MAIL_PASSWORD'):
                    server.login(smtp_config.get('MAIL_USERNAME'), smtp_config.get('MAIL_PASSWORD'))
                
                server.send_message(msg)
            
            logger.info(f"Alert email sent to {to_email}")
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
    
    def _get_error_email_template(self):
        """قالب بريد الأخطاء"""
        return """
        <!DOCTYPE html>
        <html dir="rtl" lang="ar">
        <head>
            <meta charset="UTF-8">
            <style>
                body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }
                .container { max-width: 600px; margin: 0 auto; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                .header { background: #e74c3c; color: white; padding: 20px; text-align: center; }
                .content { padding: 20px; }
                .alert-info { background: #f8f9fa; border-right: 4px solid #e74c3c; padding: 15px; margin: 15px 0; }
                .footer { background: #f8f9fa; padding: 15px; text-align: center; font-size: 12px; color: #666; }
                .timestamp { color: #666; font-size: 12px; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>🚨 تنبيه خطأ في النظام</h2>
                </div>
                <div class="content">
                    <div class="alert-info">
                        <h3>{{ alert.title }}</h3>
                        <p><strong>الرسالة:</strong> {{ alert.message }}</p>
                        <p><strong>النوع:</strong> {{ alert.alert_type }}</p>
                        <p><strong>الخطورة:</strong> {{ alert.severity }}</p>
                        <p class="timestamp"><strong>الوقت:</strong> {{ alert.created_at.strftime('%Y-%m-%d %H:%M:%S') }}</p>
                    </div>
                    
                    {% if alert.source_data %}
                    <h4>تفاصيل إضافية:</h4>
                    <ul>
                        {% for key, value in alert.source_data.items() %}
                        <li><strong>{{ key }}:</strong> {{ value }}</li>
                        {% endfor %}
                    </ul>
                    {% endif %}
                    
                    <p>يرجى مراجعة النظام واتخاذ الإجراء المناسب.</p>
                </div>
                <div class="footer">
                    نظام المحاسبة الاحترافي - تنبيهات تلقائية
                </div>
            </div>
        </body>
        </html>
        """
    
    def _get_performance_email_template(self):
        """قالب بريد الأداء"""
        return """
        <!DOCTYPE html>
        <html dir="rtl" lang="ar">
        <head>
            <meta charset="UTF-8">
            <style>
                body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }
                .container { max-width: 600px; margin: 0 auto; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                .header { background: #f39c12; color: white; padding: 20px; text-align: center; }
                .content { padding: 20px; }
                .alert-info { background: #fff3cd; border-right: 4px solid #f39c12; padding: 15px; margin: 15px 0; }
                .footer { background: #f8f9fa; padding: 15px; text-align: center; font-size: 12px; color: #666; }
                .timestamp { color: #666; font-size: 12px; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>⚡ تنبيه أداء النظام</h2>
                </div>
                <div class="content">
                    <div class="alert-info">
                        <h3>{{ alert.title }}</h3>
                        <p><strong>الرسالة:</strong> {{ alert.message }}</p>
                        <p><strong>الخطورة:</strong> {{ alert.severity }}</p>
                        <p class="timestamp"><strong>الوقت:</strong> {{ alert.created_at.strftime('%Y-%m-%d %H:%M:%S') }}</p>
                    </div>
                    
                    {% if alert.source_data %}
                    <h4>مقاييس الأداء:</h4>
                    <ul>
                        {% for key, value in alert.source_data.items() %}
                        <li><strong>{{ key }}:</strong> {{ value }}</li>
                        {% endfor %}
                    </ul>
                    {% endif %}
                    
                    <p>يرجى مراجعة أداء النظام واتخاذ الإجراءات اللازمة لتحسين الأداء.</p>
                </div>
                <div class="footer">
                    نظام المحاسبة الاحترافي - مراقبة الأداء
                </div>
            </div>
        </body>
        </html>
        """
    
    def _get_security_email_template(self):
        """قالب بريد الأمان"""
        return """
        <!DOCTYPE html>
        <html dir="rtl" lang="ar">
        <head>
            <meta charset="UTF-8">
            <style>
                body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }
                .container { max-width: 600px; margin: 0 auto; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                .header { background: #dc3545; color: white; padding: 20px; text-align: center; }
                .content { padding: 20px; }
                .alert-info { background: #f8d7da; border-right: 4px solid #dc3545; padding: 15px; margin: 15px 0; }
                .footer { background: #f8f9fa; padding: 15px; text-align: center; font-size: 12px; color: #666; }
                .timestamp { color: #666; font-size: 12px; }
                .urgent { color: #dc3545; font-weight: bold; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>🔒 تنبيه أمني عاجل</h2>
                </div>
                <div class="content">
                    <div class="alert-info">
                        <h3 class="urgent">{{ alert.title }}</h3>
                        <p><strong>الرسالة:</strong> {{ alert.message }}</p>
                        <p><strong>نوع الحدث:</strong> {{ alert.alert_type }}</p>
                        <p><strong>الخطورة:</strong> {{ alert.severity }}</p>
                        <p class="timestamp"><strong>الوقت:</strong> {{ alert.created_at.strftime('%Y-%m-%d %H:%M:%S') }}</p>
                    </div>
                    
                    {% if alert.source_data %}
                    <h4>تفاصيل الحدث الأمني:</h4>
                    <ul>
                        {% for key, value in alert.source_data.items() %}
                        <li><strong>{{ key }}:</strong> {{ value }}</li>
                        {% endfor %}
                    </ul>
                    {% endif %}
                    
                    <p class="urgent">يرجى مراجعة هذا التنبيه الأمني فوراً واتخاذ الإجراءات اللازمة لحماية النظام.</p>
                </div>
                <div class="footer">
                    نظام المحاسبة الاحترافي - مراقبة الأمان
                </div>
            </div>
        </body>
        </html>
        """
    
    def _get_health_check_email_template(self):
        """قالب بريد فحص الصحة"""
        return """
        <!DOCTYPE html>
        <html dir="rtl" lang="ar">
        <head>
            <meta charset="UTF-8">
            <style>
                body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }
                .container { max-width: 600px; margin: 0 auto; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                .header { background: #17a2b8; color: white; padding: 20px; text-align: center; }
                .content { padding: 20px; }
                .alert-info { background: #d1ecf1; border-right: 4px solid #17a2b8; padding: 15px; margin: 15px 0; }
                .footer { background: #f8f9fa; padding: 15px; text-align: center; font-size: 12px; color: #666; }
                .timestamp { color: #666; font-size: 12px; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>🏥 تنبيه فحص صحة النظام</h2>
                </div>
                <div class="content">
                    <div class="alert-info">
                        <h3>{{ alert.title }}</h3>
                        <p><strong>الرسالة:</strong> {{ alert.message }}</p>
                        <p><strong>حالة الفحص:</strong> {{ alert.severity }}</p>
                        <p class="timestamp"><strong>الوقت:</strong> {{ alert.created_at.strftime('%Y-%m-%d %H:%M:%S') }}</p>
                    </div>
                    
                    {% if alert.source_data %}
                    <h4>تفاصيل الفحص:</h4>
                    <ul>
                        {% for key, value in alert.source_data.items() %}
                        <li><strong>{{ key }}:</strong> {{ value }}</li>
                        {% endfor %}
                    </ul>
                    {% endif %}
                    
                    <p>يرجى مراجعة صحة النظام واتخاذ الإجراءات اللازمة إذا لزم الأمر.</p>
                </div>
                <div class="footer">
                    نظام المحاسبة الاحترافي - مراقبة الصحة
                </div>
            </div>
        </body>
        </html>
        """
    
    def cleanup_old_alerts(self, days=30):
        """تنظيف التنبيهات القديمة"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # حذف التنبيهات المحلولة القديمة
            deleted_count = SystemAlert.query.filter(
                SystemAlert.status == 'resolved',
                SystemAlert.created_at < cutoff_date
            ).delete()
            
            db.session.commit()
            logger.info(f"Cleaned up {deleted_count} old alerts")
            
            return deleted_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup old alerts: {str(e)}")
            db.session.rollback()
            return 0

# إنشاء مثيل مدير التنبيهات
alert_manager = AlertManager()
