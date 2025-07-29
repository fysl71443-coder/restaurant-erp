#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
سكريبت اختبار الأمان الشامل
Comprehensive Security Testing Script
"""

import os
import sys
import time
import requests
import logging
from datetime import datetime

# إضافة مسار التطبيق
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import User, Customer, Invoice, Payment
from app.security.validators import *
from app.security.encryption import *

# إعداد السجلات
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/security_test.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SecurityTester:
    """مختبر الأمان الشامل"""
    
    def __init__(self, app):
        self.app = app
        self.db = db
        self.test_results = {
            'passed': 0,
            'failed': 0,
            'warnings': 0,
            'details': []
        }
    
    def log_test(self, test_name, status, message, severity='info'):
        """تسجيل نتيجة الاختبار"""
        result = {
            'test': test_name,
            'status': status,
            'message': message,
            'severity': severity,
            'timestamp': datetime.now().isoformat()
        }
        
        self.test_results['details'].append(result)
        
        if status == 'PASS':
            self.test_results['passed'] += 1
            logger.info(f"✅ {test_name}: {message}")
        elif status == 'FAIL':
            self.test_results['failed'] += 1
            logger.error(f"❌ {test_name}: {message}")
        elif status == 'WARN':
            self.test_results['warnings'] += 1
            logger.warning(f"⚠️ {test_name}: {message}")
    
    def test_password_validation(self):
        """اختبار التحقق من كلمات المرور"""
        logger.info("🔐 اختبار التحقق من كلمات المرور...")
        
        # كلمات مرور ضعيفة
        weak_passwords = [
            'password',
            '123456',
            'abc123',
            'qwerty',
            'admin',
            '12345678'
        ]
        
        for password in weak_passwords:
            result = validate_password_strength(password)
            if result['is_valid']:
                self.log_test(
                    'Password Validation',
                    'FAIL',
                    f'كلمة المرور الضعيفة "{password}" تم قبولها',
                    'critical'
                )
            else:
                self.log_test(
                    'Password Validation',
                    'PASS',
                    f'كلمة المرور الضعيفة "{password}" تم رفضها بنجاح'
                )
        
        # كلمة مرور قوية
        strong_password = 'MyStr0ng!P@ssw0rd2024'
        result = validate_password_strength(strong_password)
        if result['is_valid']:
            self.log_test(
                'Password Validation',
                'PASS',
                'كلمة المرور القوية تم قبولها بنجاح'
            )
        else:
            self.log_test(
                'Password Validation',
                'FAIL',
                'كلمة المرور القوية تم رفضها خطأً',
                'critical'
            )
    
    def test_email_validation(self):
        """اختبار التحقق من البريد الإلكتروني"""
        logger.info("📧 اختبار التحقق من البريد الإلكتروني...")
        
        # بريد إلكتروني صحيح
        valid_emails = [
            'user@example.com',
            'test.email@domain.co.uk',
            'user+tag@example.org'
        ]
        
        for email in valid_emails:
            result = validate_email_format(email)
            if result['is_valid']:
                self.log_test(
                    'Email Validation',
                    'PASS',
                    f'البريد الإلكتروني الصحيح "{email}" تم قبوله'
                )
            else:
                self.log_test(
                    'Email Validation',
                    'FAIL',
                    f'البريد الإلكتروني الصحيح "{email}" تم رفضه خطأً',
                    'critical'
                )
        
        # بريد إلكتروني غير صحيح
        invalid_emails = [
            'invalid-email',
            '@domain.com',
            'user@',
            'user..double.dot@example.com'
        ]
        
        for email in invalid_emails:
            result = validate_email_format(email)
            if not result['is_valid']:
                self.log_test(
                    'Email Validation',
                    'PASS',
                    f'البريد الإلكتروني غير الصحيح "{email}" تم رفضه بنجاح'
                )
            else:
                self.log_test(
                    'Email Validation',
                    'FAIL',
                    f'البريد الإلكتروني غير الصحيح "{email}" تم قبوله خطأً',
                    'critical'
                )
    
    def test_sql_injection_protection(self):
        """اختبار الحماية من حقن SQL"""
        logger.info("💉 اختبار الحماية من حقن SQL...")
        
        sql_injection_attempts = [
            "'; DROP TABLE users; --",
            "1' OR '1'='1",
            "admin'--",
            "1' UNION SELECT * FROM users--",
            "'; INSERT INTO users VALUES('hacker','password'); --"
        ]
        
        for injection in sql_injection_attempts:
            result = check_sql_injection(injection)
            if not result['is_safe']:
                self.log_test(
                    'SQL Injection Protection',
                    'PASS',
                    f'محاولة حقن SQL تم اكتشافها: {injection[:20]}...'
                )
            else:
                self.log_test(
                    'SQL Injection Protection',
                    'FAIL',
                    f'محاولة حقن SQL لم يتم اكتشافها: {injection[:20]}...',
                    'critical'
                )
    
    def test_xss_protection(self):
        """اختبار الحماية من XSS"""
        logger.info("🔗 اختبار الحماية من XSS...")
        
        xss_attempts = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')",
            "<svg onload=alert('XSS')>",
            "<iframe src=javascript:alert('XSS')></iframe>"
        ]
        
        for xss in xss_attempts:
            result = check_xss_attempt(xss)
            if not result['is_safe']:
                self.log_test(
                    'XSS Protection',
                    'PASS',
                    f'محاولة XSS تم اكتشافها: {xss[:20]}...'
                )
            else:
                self.log_test(
                    'XSS Protection',
                    'FAIL',
                    f'محاولة XSS لم يتم اكتشافها: {xss[:20]}...',
                    'critical'
                )
    
    def test_data_encryption(self):
        """اختبار تشفير البيانات"""
        logger.info("🔒 اختبار تشفير البيانات...")
        
        # اختبار التشفير الأساسي
        test_data = "بيانات حساسة للاختبار"
        encrypted = encrypt_sensitive_data(test_data)
        decrypted = decrypt_sensitive_data(encrypted)
        
        if decrypted == test_data:
            self.log_test(
                'Data Encryption',
                'PASS',
                'تشفير وفك تشفير البيانات يعمل بنجاح'
            )
        else:
            self.log_test(
                'Data Encryption',
                'FAIL',
                'فشل في تشفير أو فك تشفير البيانات',
                'critical'
            )
        
        # اختبار تشفير كلمات المرور
        password = "test_password_123"
        hashed = hash_password(password)
        
        if verify_password(password, hashed):
            self.log_test(
                'Password Hashing',
                'PASS',
                'تشفير والتحقق من كلمات المرور يعمل بنجاح'
            )
        else:
            self.log_test(
                'Password Hashing',
                'FAIL',
                'فشل في تشفير أو التحقق من كلمات المرور',
                'critical'
            )
    
    def test_secure_tokens(self):
        """اختبار الرموز الآمنة"""
        logger.info("🎫 اختبار الرموز الآمنة...")
        
        # اختبار إنشاء الرموز
        token = generate_secure_token()
        if len(token) >= 32:
            self.log_test(
                'Secure Token Generation',
                'PASS',
                f'تم إنشاء رمز آمن بطول {len(token)}'
            )
        else:
            self.log_test(
                'Secure Token Generation',
                'FAIL',
                f'الرمز المُنشأ قصير جداً: {len(token)}',
                'warning'
            )
        
        # اختبار رموز CSRF
        csrf_token = generate_csrf_token()
        if len(csrf_token) >= 16:
            self.log_test(
                'CSRF Token Generation',
                'PASS',
                f'تم إنشاء رمز CSRF بطول {len(csrf_token)}'
            )
        else:
            self.log_test(
                'CSRF Token Generation',
                'FAIL',
                f'رمز CSRF قصير جداً: {len(csrf_token)}',
                'warning'
            )
    
    def test_input_sanitization(self):
        """اختبار تنظيف المدخلات"""
        logger.info("🧹 اختبار تنظيف المدخلات...")
        
        # مدخلات ضارة
        malicious_inputs = [
            "<script>alert('test')</script>",
            "javascript:void(0)",
            "<img src=x onerror=alert(1)>",
            "<?php echo 'test'; ?>"
        ]
        
        for malicious_input in malicious_inputs:
            sanitized = sanitize_input(malicious_input, allow_html=False)
            
            if '<script>' not in sanitized and 'javascript:' not in sanitized:
                self.log_test(
                    'Input Sanitization',
                    'PASS',
                    f'تم تنظيف المدخل الضار بنجاح'
                )
            else:
                self.log_test(
                    'Input Sanitization',
                    'FAIL',
                    f'فشل في تنظيف المدخل الضار: {malicious_input[:20]}...',
                    'critical'
                )
    
    def test_database_models_security(self):
        """اختبار أمان نماذج قاعدة البيانات"""
        logger.info("🗄️ اختبار أمان نماذج قاعدة البيانات...")
        
        with self.app.app_context():
            try:
                # اختبار تشفير البيانات الحساسة في نموذج العميل
                customer = Customer(
                    name="عميل اختبار",
                    email="test@example.com",
                    phone="0501234567"
                )
                
                # تعيين بيانات حساسة
                customer.credit_limit = 50000.0
                customer.bank_account = "1234567890"
                customer.iban = "SA1234567890123456789012"
                
                db.session.add(customer)
                db.session.commit()
                
                # التحقق من التشفير
                if customer._credit_limit and customer._bank_account and customer._iban:
                    self.log_test(
                        'Database Encryption',
                        'PASS',
                        'البيانات الحساسة يتم تشفيرها في قاعدة البيانات'
                    )
                else:
                    self.log_test(
                        'Database Encryption',
                        'FAIL',
                        'البيانات الحساسة لا يتم تشفيرها',
                        'critical'
                    )
                
                # التحقق من فك التشفير
                if (customer.credit_limit == 50000.0 and 
                    customer.bank_account == "1234567890" and 
                    customer.iban == "SA1234567890123456789012"):
                    self.log_test(
                        'Database Decryption',
                        'PASS',
                        'فك تشفير البيانات الحساسة يعمل بنجاح'
                    )
                else:
                    self.log_test(
                        'Database Decryption',
                        'FAIL',
                        'فشل في فك تشفير البيانات الحساسة',
                        'critical'
                    )
                
                # تنظيف البيانات
                db.session.delete(customer)
                db.session.commit()
                
            except Exception as e:
                self.log_test(
                    'Database Models Security',
                    'FAIL',
                    f'خطأ في اختبار أمان النماذج: {str(e)}',
                    'critical'
                )
    
    def test_audit_logging(self):
        """اختبار سجلات المراجعة"""
        logger.info("📝 اختبار سجلات المراجعة...")
        
        with self.app.app_context():
            try:
                from app.models.audit_log import AuditLog
                
                # إنشاء سجل مراجعة
                AuditLog.log_action(
                    table_name='test_table',
                    record_id=1,
                    action='test_action',
                    details={'test': 'data'},
                    category='security_test'
                )
                
                # التحقق من وجود السجل
                log_entry = AuditLog.query.filter_by(
                    table_name='test_table',
                    action='test_action'
                ).first()
                
                if log_entry:
                    self.log_test(
                        'Audit Logging',
                        'PASS',
                        'سجلات المراجعة تعمل بنجاح'
                    )
                    
                    # تنظيف السجل
                    db.session.delete(log_entry)
                    db.session.commit()
                else:
                    self.log_test(
                        'Audit Logging',
                        'FAIL',
                        'فشل في إنشاء سجلات المراجعة',
                        'critical'
                    )
                
            except Exception as e:
                self.log_test(
                    'Audit Logging',
                    'FAIL',
                    f'خطأ في اختبار سجلات المراجعة: {str(e)}',
                    'critical'
                )
    
    def run_all_tests(self):
        """تشغيل جميع الاختبارات"""
        logger.info("🚀 بدء اختبارات الأمان الشاملة...")
        start_time = time.time()
        
        # تشغيل جميع الاختبارات
        self.test_password_validation()
        self.test_email_validation()
        self.test_sql_injection_protection()
        self.test_xss_protection()
        self.test_data_encryption()
        self.test_secure_tokens()
        self.test_input_sanitization()
        self.test_database_models_security()
        self.test_audit_logging()
        
        end_time = time.time()
        duration = end_time - start_time
        
        # إنشاء التقرير النهائي
        self.generate_report(duration)
    
    def generate_report(self, duration):
        """إنشاء تقرير الأمان"""
        total_tests = self.test_results['passed'] + self.test_results['failed'] + self.test_results['warnings']
        
        logger.info("📊 تقرير اختبارات الأمان:")
        logger.info(f"⏱️  مدة الاختبار: {duration:.2f} ثانية")
        logger.info(f"📈 إجمالي الاختبارات: {total_tests}")
        logger.info(f"✅ نجح: {self.test_results['passed']}")
        logger.info(f"❌ فشل: {self.test_results['failed']}")
        logger.info(f"⚠️  تحذيرات: {self.test_results['warnings']}")
        
        # حساب النسبة المئوية للنجاح
        if total_tests > 0:
            success_rate = (self.test_results['passed'] / total_tests) * 100
            logger.info(f"📊 معدل النجاح: {success_rate:.1f}%")
            
            if success_rate >= 95:
                logger.info("🎉 ممتاز! النظام آمن جداً")
            elif success_rate >= 85:
                logger.info("👍 جيد! النظام آمن مع بعض التحسينات المطلوبة")
            elif success_rate >= 70:
                logger.info("⚠️  متوسط! يحتاج النظام لتحسينات أمنية")
            else:
                logger.error("🚨 ضعيف! النظام يحتاج لتحسينات أمنية عاجلة")
        
        # حفظ التقرير في ملف
        self.save_report_to_file()
    
    def save_report_to_file(self):
        """حفظ التقرير في ملف"""
        try:
            report_file = f"logs/security_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            import json
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(self.test_results, f, ensure_ascii=False, indent=2)
            
            logger.info(f"💾 تم حفظ التقرير في: {report_file}")
            
        except Exception as e:
            logger.error(f"خطأ في حفظ التقرير: {e}")

def main():
    """الدالة الرئيسية"""
    # إنشاء التطبيق
    app = create_app()
    
    # تهيئة مدير التشفير
    encryption_manager.init_app(app)
    
    # إنشاء مختبر الأمان
    tester = SecurityTester(app)
    
    # تشغيل الاختبارات
    tester.run_all_tests()
    
    # إرجاع النتيجة
    return tester.test_results['failed'] == 0

if __name__ == '__main__':
    # إنشاء مجلد السجلات إذا لم يكن موجود
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # تشغيل الاختبارات
    success = main()
    
    if success:
        print("\n🎉 جميع اختبارات الأمان نجحت!")
    else:
        print("\n⚠️  بعض اختبارات الأمان فشلت. راجع السجلات للتفاصيل.")
    
    sys.exit(0 if success else 1)
