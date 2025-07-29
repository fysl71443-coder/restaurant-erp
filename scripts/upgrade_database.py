#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
سكريبت ترقية قاعدة البيانات
Database Upgrade Script
"""

import os
import sys
import logging
from datetime import datetime
from sqlalchemy import text, inspect

# إضافة مسار التطبيق
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import *
from app.security.encryption import encryption_manager

# إعداد السجلات
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/database_upgrade.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DatabaseUpgrader:
    """مدير ترقية قاعدة البيانات"""
    
    def __init__(self, app):
        self.app = app
        self.db = db
        
    def check_database_exists(self):
        """فحص وجود قاعدة البيانات"""
        try:
            with self.app.app_context():
                # محاولة الاتصال بقاعدة البيانات
                self.db.engine.execute(text('SELECT 1'))
                return True
        except Exception as e:
            logger.error(f"خطأ في الاتصال بقاعدة البيانات: {e}")
            return False
    
    def backup_database(self):
        """إنشاء نسخة احتياطية من قاعدة البيانات"""
        try:
            backup_dir = 'backups'
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = f"{backup_dir}/backup_before_upgrade_{timestamp}.sql"
            
            # للـ SQLite
            if 'sqlite' in self.app.config['DATABASE_URL']:
                import shutil
                db_file = self.app.config['DATABASE_URL'].replace('sqlite:///', '')
                shutil.copy2(db_file, f"{backup_dir}/backup_before_upgrade_{timestamp}.db")
                logger.info(f"تم إنشاء نسخة احتياطية: {backup_file}")
                return True
            
            # للـ PostgreSQL
            elif 'postgresql' in self.app.config['DATABASE_URL']:
                import subprocess
                cmd = f"pg_dump {self.app.config['DATABASE_URL']} > {backup_file}"
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                if result.returncode == 0:
                    logger.info(f"تم إنشاء نسخة احتياطية: {backup_file}")
                    return True
                else:
                    logger.error(f"فشل في إنشاء النسخة الاحتياطية: {result.stderr}")
                    return False
            
            # للـ MySQL
            elif 'mysql' in self.app.config['DATABASE_URL']:
                import subprocess
                # استخراج معلومات الاتصال من URL
                from urllib.parse import urlparse
                parsed = urlparse(self.app.config['DATABASE_URL'])
                
                cmd = f"mysqldump -h {parsed.hostname} -u {parsed.username} -p{parsed.password} {parsed.path[1:]} > {backup_file}"
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                if result.returncode == 0:
                    logger.info(f"تم إنشاء نسخة احتياطية: {backup_file}")
                    return True
                else:
                    logger.error(f"فشل في إنشاء النسخة الاحتياطية: {result.stderr}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء النسخة الاحتياطية: {e}")
            return False
    
    def get_existing_tables(self):
        """الحصول على الجداول الموجودة"""
        try:
            with self.app.app_context():
                inspector = inspect(self.db.engine)
                return inspector.get_table_names()
        except Exception as e:
            logger.error(f"خطأ في الحصول على الجداول: {e}")
            return []
    
    def create_new_tables(self):
        """إنشاء الجداول الجديدة"""
        try:
            with self.app.app_context():
                # إنشاء جميع الجداول
                self.db.create_all()
                logger.info("تم إنشاء الجداول الجديدة بنجاح")
                return True
        except Exception as e:
            logger.error(f"خطأ في إنشاء الجداول: {e}")
            return False
    
    def migrate_existing_data(self):
        """ترحيل البيانات الموجودة"""
        try:
            with self.app.app_context():
                existing_tables = self.get_existing_tables()
                
                # ترحيل بيانات المستخدمين
                if 'user' in existing_tables:
                    self.migrate_users()
                
                # ترحيل بيانات العملاء
                if 'customer' in existing_tables:
                    self.migrate_customers()
                
                # ترحيل بيانات الفواتير
                if 'invoice' in existing_tables:
                    self.migrate_invoices()
                
                # ترحيل بيانات المدفوعات
                if 'payment' in existing_tables:
                    self.migrate_payments()
                
                logger.info("تم ترحيل البيانات بنجاح")
                return True
                
        except Exception as e:
            logger.error(f"خطأ في ترحيل البيانات: {e}")
            return False
    
    def migrate_users(self):
        """ترحيل بيانات المستخدمين"""
        try:
            # فحص إذا كانت هناك بيانات مستخدمين قديمة
            old_users = self.db.session.execute(text("SELECT * FROM user")).fetchall()
            
            for old_user in old_users:
                # فحص إذا كان المستخدم موجود بالفعل
                existing_user = User.query.filter_by(username=old_user.username).first()
                if not existing_user:
                    # إنشاء مستخدم جديد بالبيانات المحسنة
                    new_user = User(
                        username=old_user.username,
                        email=getattr(old_user, 'email', ''),
                        password_hash=old_user.password_hash,
                        is_active=getattr(old_user, 'is_active', True),
                        created_at=getattr(old_user, 'created_at', datetime.utcnow())
                    )
                    self.db.session.add(new_user)
            
            self.db.session.commit()
            logger.info("تم ترحيل بيانات المستخدمين")
            
        except Exception as e:
            logger.error(f"خطأ في ترحيل المستخدمين: {e}")
            self.db.session.rollback()
    
    def migrate_customers(self):
        """ترحيل بيانات العملاء"""
        try:
            # فحص إذا كانت هناك بيانات عملاء قديمة
            old_customers = self.db.session.execute(text("SELECT * FROM customer")).fetchall()
            
            for old_customer in old_customers:
                # فحص إذا كان العميل موجود بالفعل
                existing_customer = Customer.query.filter_by(name=old_customer.name).first()
                if not existing_customer:
                    # إنشاء عميل جديد بالبيانات المحسنة
                    new_customer = Customer(
                        name=old_customer.name,
                        email=getattr(old_customer, 'email', ''),
                        phone=getattr(old_customer, 'phone', ''),
                        address=getattr(old_customer, 'address', ''),
                        created_at=getattr(old_customer, 'created_at', datetime.utcnow())
                    )
                    self.db.session.add(new_customer)
            
            self.db.session.commit()
            logger.info("تم ترحيل بيانات العملاء")
            
        except Exception as e:
            logger.error(f"خطأ في ترحيل العملاء: {e}")
            self.db.session.rollback()
    
    def migrate_invoices(self):
        """ترحيل بيانات الفواتير"""
        try:
            # فحص إذا كانت هناك بيانات فواتير قديمة
            old_invoices = self.db.session.execute(text("SELECT * FROM invoice")).fetchall()
            
            for old_invoice in old_invoices:
                # فحص إذا كانت الفاتورة موجودة بالفعل
                existing_invoice = Invoice.query.filter_by(
                    invoice_number=getattr(old_invoice, 'invoice_number', '')
                ).first()
                
                if not existing_invoice:
                    # إنشاء فاتورة جديدة بالبيانات المحسنة
                    new_invoice = Invoice(
                        customer_name=old_invoice.customer_name,
                        date=getattr(old_invoice, 'date', datetime.utcnow()),
                        total_amount=getattr(old_invoice, 'total_amount', 0.0),
                        status=getattr(old_invoice, 'status', 'draft'),
                        created_at=getattr(old_invoice, 'created_at', datetime.utcnow())
                    )
                    self.db.session.add(new_invoice)
            
            self.db.session.commit()
            logger.info("تم ترحيل بيانات الفواتير")
            
        except Exception as e:
            logger.error(f"خطأ في ترحيل الفواتير: {e}")
            self.db.session.rollback()
    
    def migrate_payments(self):
        """ترحيل بيانات المدفوعات"""
        try:
            # فحص إذا كانت هناك بيانات مدفوعات قديمة
            old_payments = self.db.session.execute(text("SELECT * FROM payment")).fetchall()
            
            for old_payment in old_payments:
                # إنشاء دفعة جديدة بالبيانات المحسنة
                new_payment = Payment(
                    amount=old_payment.amount,
                    payment_type=getattr(old_payment, 'payment_type', 'received'),
                    payment_method=getattr(old_payment, 'payment_method', 'cash'),
                    date=getattr(old_payment, 'date', datetime.utcnow()),
                    created_at=getattr(old_payment, 'created_at', datetime.utcnow())
                )
                self.db.session.add(new_payment)
            
            self.db.session.commit()
            logger.info("تم ترحيل بيانات المدفوعات")
            
        except Exception as e:
            logger.error(f"خطأ في ترحيل المدفوعات: {e}")
            self.db.session.rollback()
    
    def initialize_system_settings(self):
        """تهيئة إعدادات النظام"""
        try:
            with self.app.app_context():
                SystemSettings.initialize_default_settings()
                logger.info("تم تهيئة إعدادات النظام")
                return True
        except Exception as e:
            logger.error(f"خطأ في تهيئة إعدادات النظام: {e}")
            return False
    
    def create_admin_user(self):
        """إنشاء مستخدم مدير افتراضي"""
        try:
            with self.app.app_context():
                # فحص إذا كان هناك مستخدم مدير
                admin_user = User.query.filter_by(username='admin').first()
                if not admin_user:
                    admin_user = User(
                        username='admin',
                        email='admin@example.com',
                        first_name='مدير',
                        last_name='النظام',
                        is_active=True,
                        is_admin=True
                    )
                    admin_user.set_password('admin123')
                    self.db.session.add(admin_user)
                    self.db.session.commit()
                    logger.info("تم إنشاء مستخدم المدير الافتراضي")
                    logger.warning("يرجى تغيير كلمة مرور المدير الافتراضية!")
                
                return True
        except Exception as e:
            logger.error(f"خطأ في إنشاء مستخدم المدير: {e}")
            return False
    
    def run_upgrade(self):
        """تشغيل عملية الترقية الكاملة"""
        logger.info("بدء عملية ترقية قاعدة البيانات...")
        
        # 1. فحص وجود قاعدة البيانات
        if not self.check_database_exists():
            logger.error("لا يمكن الاتصال بقاعدة البيانات")
            return False
        
        # 2. إنشاء نسخة احتياطية
        logger.info("إنشاء نسخة احتياطية...")
        if not self.backup_database():
            logger.error("فشل في إنشاء النسخة الاحتياطية")
            return False
        
        # 3. إنشاء الجداول الجديدة
        logger.info("إنشاء الجداول الجديدة...")
        if not self.create_new_tables():
            logger.error("فشل في إنشاء الجداول الجديدة")
            return False
        
        # 4. ترحيل البيانات الموجودة
        logger.info("ترحيل البيانات الموجودة...")
        if not self.migrate_existing_data():
            logger.error("فشل في ترحيل البيانات")
            return False
        
        # 5. تهيئة إعدادات النظام
        logger.info("تهيئة إعدادات النظام...")
        if not self.initialize_system_settings():
            logger.error("فشل في تهيئة إعدادات النظام")
            return False
        
        # 6. إنشاء مستخدم مدير افتراضي
        logger.info("إنشاء مستخدم المدير...")
        if not self.create_admin_user():
            logger.error("فشل في إنشاء مستخدم المدير")
            return False
        
        logger.info("تمت عملية ترقية قاعدة البيانات بنجاح! 🎉")
        return True

def main():
    """الدالة الرئيسية"""
    # إنشاء التطبيق
    app = create_app()
    
    # تهيئة مدير التشفير
    encryption_manager.init_app(app)
    
    # إنشاء مدير الترقية
    upgrader = DatabaseUpgrader(app)
    
    # تشغيل الترقية
    success = upgrader.run_upgrade()
    
    if success:
        print("\n✅ تمت ترقية قاعدة البيانات بنجاح!")
        print("📋 تفاصيل المستخدم الافتراضي:")
        print("   اسم المستخدم: admin")
        print("   كلمة المرور: admin123")
        print("⚠️  يرجى تغيير كلمة المرور فوراً!")
    else:
        print("\n❌ فشلت عملية ترقية قاعدة البيانات!")
        print("📝 راجع ملف السجلات: logs/database_upgrade.log")
    
    return success

if __name__ == '__main__':
    # إنشاء مجلد السجلات إذا لم يكن موجود
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # تشغيل الترقية
    success = main()
    sys.exit(0 if success else 1)
