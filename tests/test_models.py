#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبارات النماذج
Model Tests
"""

import unittest
from datetime import datetime
from app import create_app, db
from app.models.user_enhanced import User
from app.models.system_monitoring import SystemLog, PerformanceMetric, SystemAlert

class TestModels(unittest.TestCase):
    """اختبارات النماذج"""
    
    def setUp(self):
        """إعداد الاختبار"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        db.create_all()
    
    def tearDown(self):
        """تنظيف بعد الاختبار"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_user_model(self):
        """اختبار نموذج المستخدم"""
        # إنشاء مستخدم جديد
        user = User(
            username='testuser',
            email='test@example.com',
            first_name='Test',
            last_name='User'
        )
        user.set_password('testpassword')
        
        db.session.add(user)
        db.session.commit()
        
        # اختبار البيانات
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('testpassword'))
        self.assertFalse(user.check_password('wrongpassword'))
        
        # اختبار الاسم الكامل
        self.assertEqual(user.display_name, 'Test User')
    
    def test_user_password_hashing(self):
        """اختبار تشفير كلمة المرور"""
        user = User(username='testuser')
        user.set_password('testpassword')
        
        # التأكد من أن كلمة المرور مشفرة
        self.assertNotEqual(user.password_hash, 'testpassword')
        self.assertTrue(user.check_password('testpassword'))
    
    def test_system_log_model(self):
        """اختبار نموذج سجلات النظام"""
        log = SystemLog(
            level='INFO',
            logger_name='test_logger',
            message='Test log message'
        )
        
        db.session.add(log)
        db.session.commit()
        
        # اختبار البيانات
        self.assertEqual(log.level, 'INFO')
        self.assertEqual(log.logger_name, 'test_logger')
        self.assertEqual(log.message, 'Test log message')
        self.assertIsNotNone(log.timestamp)
    
    def test_performance_metric_model(self):
        """اختبار نموذج مقاييس الأداء"""
        metric = PerformanceMetric(
            metric_name='response_time',
            value=150.5,
            unit='ms',
            category='api'
        )
        
        db.session.add(metric)
        db.session.commit()
        
        # اختبار البيانات
        self.assertEqual(metric.metric_name, 'response_time')
        self.assertEqual(metric.value, 150.5)
        self.assertEqual(metric.unit, 'ms')
        self.assertEqual(metric.category, 'api')
    
    def test_system_alert_model(self):
        """اختبار نموذج تنبيهات النظام"""
        alert = SystemAlert(
            alert_type='error',
            severity='high',
            title='Test Alert',
            message='This is a test alert'
        )
        
        db.session.add(alert)
        db.session.commit()
        
        # اختبار البيانات
        self.assertEqual(alert.alert_type, 'error')
        self.assertEqual(alert.severity, 'high')
        self.assertEqual(alert.title, 'Test Alert')
        self.assertEqual(alert.status, 'active')
    
    def test_user_relationships(self):
        """اختبار علاقات المستخدم"""
        user = User(username='testuser', email='test@example.com')
        db.session.add(user)
        db.session.commit()
        
        # إنشاء سجل مرتبط بالمستخدم
        log = SystemLog(
            level='INFO',
            logger_name='test',
            message='User action',
            user_id=user.id
        )
        db.session.add(log)
        db.session.commit()
        
        # اختبار العلاقة
        self.assertEqual(len(user.system_logs), 1)
        self.assertEqual(log.user, user)

if __name__ == '__main__':
    unittest.main()
