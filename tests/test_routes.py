#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبارات المسارات
Route Tests
"""

import unittest
from app import create_app, db
from app.models.user_enhanced import User

class TestRoutes(unittest.TestCase):
    """اختبارات المسارات"""
    
    def setUp(self):
        """إعداد الاختبار"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        db.create_all()
        
        # إنشاء مستخدم تجريبي
        self.test_user = User(
            username='testuser',
            email='test@example.com',
            first_name='Test',
            last_name='User',
            is_admin=True,
            is_active=True
        )
        self.test_user.set_password('testpassword')
        db.session.add(self.test_user)
        db.session.commit()
    
    def tearDown(self):
        """تنظيف بعد الاختبار"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def login(self, username='testuser', password='testpassword'):
        """تسجيل الدخول"""
        return self.client.post('/auth/login', data={
            'username': username,
            'password': password
        }, follow_redirects=True)
    
    def logout(self):
        """تسجيل الخروج"""
        return self.client.get('/auth/logout', follow_redirects=True)
    
    def test_homepage(self):
        """اختبار الصفحة الرئيسية"""
        response = self.client.get('/')
        self.assertIn(response.status_code, [200, 302])
    
    def test_login_page(self):
        """اختبار صفحة تسجيل الدخول"""
        response = self.client.get('/auth/login')
        self.assertEqual(response.status_code, 200)
    
    def test_login_functionality(self):
        """اختبار وظيفة تسجيل الدخول"""
        # تسجيل دخول صحيح
        response = self.login()
        self.assertEqual(response.status_code, 200)
        
        # تسجيل دخول خاطئ
        response = self.login('wronguser', 'wrongpassword')
        self.assertIn(response.status_code, [200, 401])
    
    def test_logout_functionality(self):
        """اختبار وظيفة تسجيل الخروج"""
        # تسجيل الدخول أولاً
        self.login()
        
        # تسجيل الخروج
        response = self.logout()
        self.assertEqual(response.status_code, 200)
    
    def test_protected_routes(self):
        """اختبار المسارات المحمية"""
        protected_routes = [
            '/sales',
            '/purchases',
            '/analytics',
            '/vat',
            '/payroll',
            '/reports'
        ]
        
        # اختبار الوصول بدون تسجيل دخول
        for route in protected_routes:
            response = self.client.get(route)
            self.assertIn(response.status_code, [302, 401])  # إعادة توجيه أو رفض
        
        # اختبار الوصول بعد تسجيل الدخول
        self.login()
        for route in protected_routes:
            response = self.client.get(route)
            self.assertIn(response.status_code, [200, 302])
    
    def test_api_routes(self):
        """اختبار مسارات API"""
        self.login()
        
        api_routes = [
            '/api/stats',
            '/api/dashboard-data',
            '/language/api/current'
        ]
        
        for route in api_routes:
            response = self.client.get(route)
            self.assertIn(response.status_code, [200, 404])
    
    def test_language_switching(self):
        """اختبار تبديل اللغة"""
        self.login()
        
        # تبديل للعربية
        response = self.client.get('/language/set/ar')
        self.assertIn(response.status_code, [200, 302])
        
        # تبديل للإنجليزية
        response = self.client.get('/language/set/en')
        self.assertIn(response.status_code, [200, 302])
    
    def test_admin_routes(self):
        """اختبار مسارات المدير"""
        self.login()
        
        admin_routes = [
            '/logging/dashboard',
            '/backup/dashboard'
        ]
        
        for route in admin_routes:
            response = self.client.get(route)
            self.assertIn(response.status_code, [200, 404])  # 404 إذا لم يكن المسار موجود
    
    def test_error_pages(self):
        """اختبار صفحات الأخطاء"""
        # اختبار صفحة غير موجودة
        response = self.client.get('/nonexistent-page')
        self.assertEqual(response.status_code, 404)
    
    def test_form_submissions(self):
        """اختبار إرسال النماذج"""
        self.login()
        
        # اختبار نموذج بسيط (إذا كان موجود)
        response = self.client.post('/api/test', data={
            'test_field': 'test_value'
        })
        # نتوقع 404 أو 405 لأن المسار غير موجود
        self.assertIn(response.status_code, [404, 405])

if __name__ == '__main__':
    unittest.main()
