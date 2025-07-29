#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
سكريبت تهيئة نظام المصادقة والصلاحيات
Authentication and Authorization System Initialization Script
"""

import os
import sys
import logging
from datetime import datetime

# إضافة مسار التطبيق
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models.user_enhanced import User
from app.models.roles_permissions import Role, Permission, UserRole, RolePermission
from app.security.encryption import encryption_manager

# إعداد السجلات
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/auth_system_init.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AuthSystemInitializer:
    """مهيئ نظام المصادقة والصلاحيات"""
    
    def __init__(self, app):
        self.app = app
        self.db = db
    
    def create_default_permissions(self):
        """إنشاء الصلاحيات الافتراضية"""
        logger.info("إنشاء الصلاحيات الافتراضية...")
        
        with self.app.app_context():
            Permission.create_default_permissions()
            logger.info("تم إنشاء الصلاحيات الافتراضية بنجاح")
    
    def create_default_roles(self):
        """إنشاء الأدوار الافتراضية"""
        logger.info("إنشاء الأدوار الافتراضية...")
        
        with self.app.app_context():
            Role.create_default_roles()
            logger.info("تم إنشاء الأدوار الافتراضية بنجاح")
    
    def assign_permissions_to_roles(self):
        """تعيين الصلاحيات للأدوار"""
        logger.info("تعيين الصلاحيات للأدوار...")
        
        with self.app.app_context():
            # صلاحيات المدير (جميع الصلاحيات)
            admin_role = Role.query.filter_by(name='admin').first()
            if admin_role:
                all_permissions = Permission.query.all()
                for permission in all_permissions:
                    admin_role.add_permission(permission)
            
            # صلاحيات المدير العام
            manager_role = Role.query.filter_by(name='manager').first()
            if manager_role:
                manager_permissions = [
                    'users.view', 'users.create', 'users.edit',
                    'customers.view', 'customers.create', 'customers.edit', 'customers.delete',
                    'suppliers.view', 'suppliers.create', 'suppliers.edit', 'suppliers.delete',
                    'products.view', 'products.create', 'products.edit', 'products.delete', 'products.manage_inventory',
                    'invoices.view', 'invoices.create', 'invoices.edit', 'invoices.approve', 'invoices.print',
                    'payments.view', 'payments.create', 'payments.edit', 'payments.verify',
                    'reports.view', 'reports.export', 'reports.advanced',
                    'settings.view', 'settings.edit'
                ]
                
                for perm_name in manager_permissions:
                    permission = Permission.query.filter_by(name=perm_name).first()
                    if permission:
                        manager_role.add_permission(permission)
            
            # صلاحيات المحاسب
            accountant_role = Role.query.filter_by(name='accountant').first()
            if accountant_role:
                accountant_permissions = [
                    'customers.view', 'customers.create', 'customers.edit',
                    'suppliers.view', 'suppliers.create', 'suppliers.edit',
                    'products.view',
                    'invoices.view', 'invoices.create', 'invoices.edit', 'invoices.print',
                    'payments.view', 'payments.create', 'payments.edit', 'payments.verify',
                    'reports.view', 'reports.export'
                ]
                
                for perm_name in accountant_permissions:
                    permission = Permission.query.filter_by(name=perm_name).first()
                    if permission:
                        accountant_role.add_permission(permission)
            
            # صلاحيات الموظف
            employee_role = Role.query.filter_by(name='employee').first()
            if employee_role:
                employee_permissions = [
                    'customers.view', 'customers.create', 'customers.edit',
                    'products.view',
                    'invoices.view', 'invoices.create', 'invoices.edit',
                    'payments.view', 'payments.create',
                    'reports.view'
                ]
                
                for perm_name in employee_permissions:
                    permission = Permission.query.filter_by(name=perm_name).first()
                    if permission:
                        employee_role.add_permission(permission)
            
            # صلاحيات المشاهد
            viewer_role = Role.query.filter_by(name='viewer').first()
            if viewer_role:
                viewer_permissions = [
                    'customers.view',
                    'products.view',
                    'invoices.view',
                    'payments.view',
                    'reports.view'
                ]
                
                for perm_name in viewer_permissions:
                    permission = Permission.query.filter_by(name=perm_name).first()
                    if permission:
                        viewer_role.add_permission(permission)
            
            db.session.commit()
            logger.info("تم تعيين الصلاحيات للأدوار بنجاح")
    
    def create_admin_user(self):
        """إنشاء مستخدم مدير افتراضي"""
        logger.info("إنشاء مستخدم المدير الافتراضي...")
        
        with self.app.app_context():
            # فحص إذا كان هناك مدير موجود
            admin_user = User.query.filter_by(username='admin').first()
            
            if not admin_user:
                # إنشاء مستخدم مدير جديد
                admin_user = User(
                    username='admin',
                    email='admin@accounting-system.com',
                    first_name='مدير',
                    last_name='النظام',
                    is_active=True,
                    is_admin=True,
                    is_verified=True
                )
                admin_user.set_password('Admin@123456')
                
                db.session.add(admin_user)
                db.session.commit()
                
                # تعيين دور المدير
                admin_role = Role.query.filter_by(name='admin').first()
                if admin_role:
                    user_role = UserRole(
                        user_id=admin_user.id,
                        role_id=admin_role.id
                    )
                    db.session.add(user_role)
                    db.session.commit()
                
                logger.info("تم إنشاء مستخدم المدير الافتراضي:")
                logger.info("  اسم المستخدم: admin")
                logger.info("  كلمة المرور: Admin@123456")
                logger.info("  البريد الإلكتروني: admin@accounting-system.com")
                logger.warning("⚠️  يرجى تغيير كلمة المرور فوراً بعد تسجيل الدخول!")
            
            else:
                logger.info("مستخدم المدير موجود بالفعل")
    
    def create_demo_users(self):
        """إنشاء مستخدمين تجريبيين"""
        logger.info("إنشاء مستخدمين تجريبيين...")
        
        with self.app.app_context():
            demo_users = [
                {
                    'username': 'manager',
                    'email': 'manager@accounting-system.com',
                    'first_name': 'أحمد',
                    'last_name': 'المدير',
                    'role': 'manager',
                    'password': 'Manager@123'
                },
                {
                    'username': 'accountant',
                    'email': 'accountant@accounting-system.com',
                    'first_name': 'فاطمة',
                    'last_name': 'المحاسبة',
                    'role': 'accountant',
                    'password': 'Accountant@123'
                },
                {
                    'username': 'employee',
                    'email': 'employee@accounting-system.com',
                    'first_name': 'محمد',
                    'last_name': 'الموظف',
                    'role': 'employee',
                    'password': 'Employee@123'
                },
                {
                    'username': 'viewer',
                    'email': 'viewer@accounting-system.com',
                    'first_name': 'سارة',
                    'last_name': 'المشاهدة',
                    'role': 'viewer',
                    'password': 'Viewer@123'
                }
            ]
            
            for user_data in demo_users:
                existing_user = User.query.filter_by(username=user_data['username']).first()
                
                if not existing_user:
                    # إنشاء المستخدم
                    user = User(
                        username=user_data['username'],
                        email=user_data['email'],
                        first_name=user_data['first_name'],
                        last_name=user_data['last_name'],
                        is_active=True,
                        is_verified=True
                    )
                    user.set_password(user_data['password'])
                    
                    db.session.add(user)
                    db.session.commit()
                    
                    # تعيين الدور
                    role = Role.query.filter_by(name=user_data['role']).first()
                    if role:
                        user_role = UserRole(
                            user_id=user.id,
                            role_id=role.id
                        )
                        db.session.add(user_role)
                        db.session.commit()
                    
                    logger.info(f"تم إنشاء المستخدم التجريبي: {user_data['username']}")
    
    def verify_system_integrity(self):
        """التحقق من سلامة النظام"""
        logger.info("التحقق من سلامة النظام...")
        
        with self.app.app_context():
            # فحص الأدوار
            roles_count = Role.query.count()
            logger.info(f"عدد الأدوار: {roles_count}")
            
            # فحص الصلاحيات
            permissions_count = Permission.query.count()
            logger.info(f"عدد الصلاحيات: {permissions_count}")
            
            # فحص المستخدمين
            users_count = User.query.count()
            active_users = User.query.filter_by(is_active=True).count()
            admin_users = User.query.filter_by(is_admin=True).count()
            
            logger.info(f"عدد المستخدمين: {users_count}")
            logger.info(f"المستخدمين النشطين: {active_users}")
            logger.info(f"المديرين: {admin_users}")
            
            # فحص تعيين الأدوار
            user_roles_count = UserRole.query.count()
            logger.info(f"تعيينات الأدوار: {user_roles_count}")
            
            # فحص تعيين الصلاحيات
            role_permissions_count = RolePermission.query.count()
            logger.info(f"تعيينات الصلاحيات: {role_permissions_count}")
            
            # التحقق من وجود مدير واحد على الأقل
            if admin_users == 0:
                logger.error("⚠️  لا يوجد مديرين في النظام!")
                return False
            
            logger.info("✅ النظام سليم ومكتمل")
            return True
    
    def run_initialization(self):
        """تشغيل عملية التهيئة الكاملة"""
        logger.info("🚀 بدء تهيئة نظام المصادقة والصلاحيات...")
        
        try:
            # 1. إنشاء الصلاحيات الافتراضية
            self.create_default_permissions()
            
            # 2. إنشاء الأدوار الافتراضية
            self.create_default_roles()
            
            # 3. تعيين الصلاحيات للأدوار
            self.assign_permissions_to_roles()
            
            # 4. إنشاء مستخدم المدير
            self.create_admin_user()
            
            # 5. إنشاء مستخدمين تجريبيين
            self.create_demo_users()
            
            # 6. التحقق من سلامة النظام
            if self.verify_system_integrity():
                logger.info("🎉 تمت تهيئة نظام المصادقة والصلاحيات بنجاح!")
                return True
            else:
                logger.error("❌ فشلت تهيئة النظام!")
                return False
                
        except Exception as e:
            logger.error(f"خطأ في تهيئة النظام: {str(e)}")
            return False

def main():
    """الدالة الرئيسية"""
    # إنشاء التطبيق
    app = create_app()
    
    # تهيئة مدير التشفير
    encryption_manager.init_app(app)
    
    # إنشاء مهيئ النظام
    initializer = AuthSystemInitializer(app)
    
    # تشغيل التهيئة
    success = initializer.run_initialization()
    
    if success:
        print("\n✅ تمت تهيئة نظام المصادقة والصلاحيات بنجاح!")
        print("\n📋 بيانات تسجيل الدخول:")
        print("┌─────────────────────────────────────────┐")
        print("│ المدير الرئيسي:                        │")
        print("│   اسم المستخدم: admin                  │")
        print("│   كلمة المرور: Admin@123456            │")
        print("├─────────────────────────────────────────┤")
        print("│ المستخدمين التجريبيين:                 │")
        print("│   manager / Manager@123                 │")
        print("│   accountant / Accountant@123           │")
        print("│   employee / Employee@123               │")
        print("│   viewer / Viewer@123                   │")
        print("└─────────────────────────────────────────┘")
        print("\n⚠️  يرجى تغيير كلمات المرور فوراً!")
    else:
        print("\n❌ فشلت تهيئة نظام المصادقة والصلاحيات!")
        print("📝 راجع ملف السجلات: logs/auth_system_init.log")
    
    return success

if __name__ == '__main__':
    # إنشاء مجلد السجلات إذا لم يكن موجود
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # تشغيل التهيئة
    success = main()
    sys.exit(0 if success else 1)
