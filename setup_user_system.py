#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
سكريبت إعداد نظام المستخدمين والإعدادات
يقوم بإنشاء الجداول المطلوبة وإضافة البيانات الافتراضية
"""

import os
import sys
from datetime import datetime, timezone

# إضافة المجلد الحالي للمسار
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
from database import db, User, SystemSettings

def create_tables():
    """إنشاء جميع الجداول"""
    print("🔄 إنشاء جداول قاعدة البيانات...")
    
    with app.app_context():
        try:
            # إنشاء جميع الجداول
            db.create_all()
            print("✅ تم إنشاء جداول قاعدة البيانات بنجاح")
            return True
        except Exception as e:
            print(f"❌ خطأ في إنشاء الجداول: {str(e)}")
            return False

def create_default_admin():
    """إنشاء مستخدم مدير افتراضي"""
    print("🔄 إنشاء المستخدم الافتراضي...")
    
    with app.app_context():
        try:
            # التحقق من وجود المستخدم
            existing_admin = User.query.filter_by(username='admin').first()
            if existing_admin:
                print("⚠️  المستخدم 'admin' موجود بالفعل")
                return True
            
            # إنشاء المستخدم الافتراضي
            admin = User(
                username='admin',
                email='admin@company.com',
                full_name='مدير النظام',
                role='admin',
                department='إدارة',
                phone='+966xxxxxxxxx',
                is_active=True,
                can_view_reports=True,
                can_manage_invoices=True,
                can_manage_customers=True,
                can_manage_products=True,
                can_manage_employees=True,
                can_manage_payroll=True,
                can_manage_settings=True,
                can_manage_users=True,
                created_at=datetime.now(timezone.utc)
            )
            admin.set_password('admin123')  # يجب تغييرها في الإنتاج
            
            db.session.add(admin)
            db.session.commit()
            
            print("✅ تم إنشاء المستخدم الافتراضي:")
            print("   اسم المستخدم: admin")
            print("   كلمة المرور: admin123")
            print("   ⚠️  يرجى تغيير كلمة المرور بعد أول تسجيل دخول!")
            return True
            
        except Exception as e:
            print(f"❌ خطأ في إنشاء المستخدم الافتراضي: {str(e)}")
            db.session.rollback()
            return False

def setup_default_settings():
    """إعداد الإعدادات الافتراضية للنظام"""
    print("🔄 إعداد الإعدادات الافتراضية...")
    
    default_settings = [
        # إعدادات عامة
        ('company_name', 'شركة المحاسبة المتقدمة', 'string', 'اسم الشركة', 'general', True),
        ('company_address', 'الرياض، المملكة العربية السعودية', 'string', 'عنوان الشركة', 'general', True),
        ('company_phone', '+966xxxxxxxxx', 'string', 'هاتف الشركة', 'general', True),
        ('company_email', 'info@company.com', 'string', 'بريد الشركة الإلكتروني', 'general', True),
        ('tax_number', '123456789012345', 'string', 'الرقم الضريبي', 'general', True),
        ('commercial_register', '1010123456', 'string', 'رقم السجل التجاري', 'general', True),
        
        # إعدادات المظهر
        ('theme', 'light', 'string', 'سمة النظام (light/dark)', 'appearance', True),
        ('language', 'ar', 'string', 'لغة النظام', 'appearance', True),
        ('date_format', 'dd/mm/yyyy', 'string', 'تنسيق التاريخ', 'appearance', True),
        ('currency', 'ريال سعودي', 'string', 'العملة الافتراضية', 'appearance', True),
        ('currency_symbol', 'ر.س', 'string', 'رمز العملة', 'appearance', True),
        ('items_per_page', '20', 'integer', 'عدد العناصر في الصفحة', 'appearance', True),
        ('decimal_places', '2', 'integer', 'عدد الخانات العشرية', 'appearance', True),
        
        # إعدادات الأمان
        ('session_timeout', '30', 'integer', 'انتهاء الجلسة (بالدقائق)', 'security', False),
        ('password_min_length', '8', 'integer', 'الحد الأدنى لطول كلمة المرور', 'security', False),
        ('max_login_attempts', '5', 'integer', 'عدد محاولات تسجيل الدخول', 'security', False),
        ('require_password_change', 'false', 'boolean', 'إجبار تغيير كلمة المرور', 'security', False),
        ('enable_two_factor', 'false', 'boolean', 'تفعيل المصادقة الثنائية', 'security', False),
        ('auto_logout', 'true', 'boolean', 'تسجيل خروج تلقائي عند عدم النشاط', 'security', False),
        
        # إعدادات الطباعة
        ('print_logo', 'true', 'boolean', 'طباعة شعار الشركة', 'printing', True),
        ('print_header', 'true', 'boolean', 'طباعة رأس الصفحة', 'printing', True),
        ('print_footer', 'true', 'boolean', 'طباعة تذييل الصفحة', 'printing', True),
        ('paper_size', 'A4', 'string', 'حجم الورق', 'printing', True),
        ('print_margins', '20', 'integer', 'هوامش الطباعة (مم)', 'printing', True),
        ('print_colors', 'false', 'boolean', 'طباعة ملونة', 'printing', True),
        ('watermark', 'false', 'boolean', 'إضافة علامة مائية', 'printing', True),
        
        # إعدادات التوطين
        ('timezone', 'Asia/Riyadh', 'string', 'المنطقة الزمنية', 'localization', True),
        ('first_day_of_week', '6', 'integer', 'أول يوم في الأسبوع (0=أحد، 6=سبت)', 'localization', True),
        ('number_format', '1,234.56', 'string', 'تنسيق الأرقام', 'localization', True),
        ('rtl_support', 'true', 'boolean', 'دعم الكتابة من اليمين لليسار', 'localization', True),
        ('hijri_calendar', 'false', 'boolean', 'استخدام التقويم الهجري', 'localization', True),
        
        # إعدادات النسخ الاحتياطي
        ('auto_backup', 'true', 'boolean', 'النسخ الاحتياطي التلقائي', 'backup', False),
        ('backup_frequency', 'daily', 'string', 'تكرار النسخ الاحتياطي', 'backup', False),
        ('backup_retention', '30', 'integer', 'مدة الاحتفاظ بالنسخ (أيام)', 'backup', False),
        
        # إعدادات الإشعارات
        ('email_notifications', 'true', 'boolean', 'إشعارات البريد الإلكتروني', 'notifications', True),
        ('sms_notifications', 'false', 'boolean', 'إشعارات الرسائل النصية', 'notifications', True),
        ('system_notifications', 'true', 'boolean', 'إشعارات النظام', 'notifications', True),
    ]
    
    with app.app_context():
        try:
            settings_added = 0
            settings_updated = 0
            
            for key, value, setting_type, description, category, is_public in default_settings:
                existing_setting = SystemSettings.query.filter_by(setting_key=key).first()
                
                if existing_setting:
                    # تحديث الوصف والفئة إذا تغيرت
                    if existing_setting.description != description or existing_setting.category != category:
                        existing_setting.description = description
                        existing_setting.category = category
                        existing_setting.is_public = is_public
                        existing_setting.updated_at = datetime.now(timezone.utc)
                        settings_updated += 1
                else:
                    # إنشاء إعداد جديد
                    setting = SystemSettings(
                        setting_key=key,
                        setting_type=setting_type,
                        description=description,
                        category=category,
                        is_public=is_public,
                        created_at=datetime.now(timezone.utc)
                    )
                    setting.set_value(value)
                    db.session.add(setting)
                    settings_added += 1
            
            db.session.commit()
            
            print(f"✅ تم إعداد الإعدادات الافتراضية:")
            print(f"   إعدادات جديدة: {settings_added}")
            print(f"   إعدادات محدثة: {settings_updated}")
            return True
            
        except Exception as e:
            print(f"❌ خطأ في إعداد الإعدادات الافتراضية: {str(e)}")
            db.session.rollback()
            return False

def main():
    """الدالة الرئيسية"""
    print("=" * 60)
    print("🚀 بدء إعداد نظام المستخدمين والإعدادات")
    print("=" * 60)
    
    # التحقق من وجود ملف قاعدة البيانات
    db_path = 'accounting_system.db'
    if os.path.exists(db_path):
        print(f"📁 ملف قاعدة البيانات موجود: {db_path}")
    else:
        print(f"📁 سيتم إنشاء ملف قاعدة البيانات: {db_path}")
    
    success = True
    
    # 1. إنشاء الجداول
    if not create_tables():
        success = False
    
    # 2. إنشاء المستخدم الافتراضي
    if success and not create_default_admin():
        success = False
    
    # 3. إعداد الإعدادات الافتراضية
    if success and not setup_default_settings():
        success = False
    
    print("=" * 60)
    if success:
        print("🎉 تم إعداد نظام المستخدمين والإعدادات بنجاح!")
        print("\n📋 معلومات تسجيل الدخول:")
        print("   الرابط: http://localhost:5000/login")
        print("   اسم المستخدم: admin")
        print("   كلمة المرور: admin123")
        print("\n⚠️  تذكير مهم:")
        print("   - يرجى تغيير كلمة المرور الافتراضية فور تسجيل الدخول")
        print("   - راجع إعدادات النظام وقم بتخصيصها حسب احتياجاتك")
        print("   - تأكد من إعداد النسخ الاحتياطي التلقائي")
    else:
        print("❌ فشل في إعداد النظام. يرجى مراجعة الأخطاء أعلاه.")
    print("=" * 60)
    
    return success

if __name__ == '__main__':
    main()
