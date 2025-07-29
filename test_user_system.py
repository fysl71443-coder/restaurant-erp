#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار شامل لنظام المستخدمين والإعدادات
يقوم بفحص جميع وظائف النظام والتأكد من عملها بشكل صحيح
"""

import os
import sys
import json
from datetime import datetime, timezone

# إضافة المجلد الحالي للمسار
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
from database import db, User, SystemSettings

class UserSystemTester:
    def __init__(self):
        self.app = app
        self.test_results = {
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'test_details': []
        }
    
    def log_test(self, test_name, passed, message=""):
        """تسجيل نتيجة الاختبار"""
        self.test_results['total_tests'] += 1
        if passed:
            self.test_results['passed_tests'] += 1
            status = "✅ نجح"
        else:
            self.test_results['failed_tests'] += 1
            status = "❌ فشل"
        
        self.test_results['test_details'].append({
            'test_name': test_name,
            'status': status,
            'message': message,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        
        print(f"{status}: {test_name}")
        if message:
            print(f"   {message}")
    
    def test_database_connection(self):
        """اختبار الاتصال بقاعدة البيانات"""
        try:
            with self.app.app_context():
                # محاولة تنفيذ استعلام بسيط
                result = db.session.execute(db.text("SELECT 1")).fetchone()
                if result and result[0] == 1:
                    self.log_test("اتصال قاعدة البيانات", True, "الاتصال يعمل بشكل صحيح")
                    return True
                else:
                    self.log_test("اتصال قاعدة البيانات", False, "فشل في تنفيذ الاستعلام")
                    return False
        except Exception as e:
            self.log_test("اتصال قاعدة البيانات", False, f"خطأ: {str(e)}")
            return False
    
    def test_user_model(self):
        """اختبار نموذج المستخدم"""
        try:
            with self.app.app_context():
                # اختبار إنشاء مستخدم
                test_user = User(
                    username='test_user',
                    email='test@example.com',
                    full_name='مستخدم تجريبي',
                    role='user'
                )
                test_user.set_password('test123')
                
                # اختبار تشفير كلمة المرور
                if test_user.check_password('test123'):
                    self.log_test("تشفير كلمة المرور", True, "التشفير والتحقق يعملان بشكل صحيح")
                else:
                    self.log_test("تشفير كلمة المرور", False, "فشل في التحقق من كلمة المرور")
                    return False
                
                # اختبار الصلاحيات
                if not test_user.has_permission('manage_users'):
                    self.log_test("نظام الصلاحيات", True, "نظام الصلاحيات يعمل بشكل صحيح")
                else:
                    self.log_test("نظام الصلاحيات", False, "خطأ في نظام الصلاحيات")
                    return False
                
                return True
        except Exception as e:
            self.log_test("نموذج المستخدم", False, f"خطأ: {str(e)}")
            return False
    
    def test_system_settings_model(self):
        """اختبار نموذج إعدادات النظام"""
        try:
            with self.app.app_context():
                # اختبار إنشاء إعداد
                test_setting = SystemSettings(
                    setting_key='test_setting',
                    setting_type='string',
                    description='إعداد تجريبي',
                    category='test'
                )
                test_setting.set_value('test_value')
                
                # اختبار الحصول على القيمة
                if test_setting.get_value() == 'test_value':
                    self.log_test("نموذج الإعدادات - النصوص", True, "حفظ واسترجاع النصوص يعمل بشكل صحيح")
                else:
                    self.log_test("نموذج الإعدادات - النصوص", False, "فشل في حفظ أو استرجاع النصوص")
                    return False
                
                # اختبار الإعدادات المنطقية
                bool_setting = SystemSettings(
                    setting_key='test_bool',
                    setting_type='boolean',
                    description='إعداد منطقي تجريبي',
                    category='test'
                )
                bool_setting.set_value(True)
                
                if bool_setting.get_value() is True:
                    self.log_test("نموذج الإعدادات - المنطقية", True, "حفظ واسترجاع القيم المنطقية يعمل بشكل صحيح")
                else:
                    self.log_test("نموذج الإعدادات - المنطقية", False, "فشل في حفظ أو استرجاع القيم المنطقية")
                    return False
                
                # اختبار الإعدادات الرقمية
                int_setting = SystemSettings(
                    setting_key='test_int',
                    setting_type='integer',
                    description='إعداد رقمي تجريبي',
                    category='test'
                )
                int_setting.set_value(42)
                
                if int_setting.get_value() == 42:
                    self.log_test("نموذج الإعدادات - الأرقام", True, "حفظ واسترجاع الأرقام يعمل بشكل صحيح")
                else:
                    self.log_test("نموذج الإعدادات - الأرقام", False, "فشل في حفظ أو استرجاع الأرقام")
                    return False
                
                return True
        except Exception as e:
            self.log_test("نموذج إعدادات النظام", False, f"خطأ: {str(e)}")
            return False
    
    def test_default_admin_user(self):
        """اختبار وجود المستخدم الافتراضي"""
        try:
            with self.app.app_context():
                admin_user = User.query.filter_by(username='admin').first()
                
                if not admin_user:
                    self.log_test("المستخدم الافتراضي", False, "المستخدم 'admin' غير موجود")
                    return False
                
                # اختبار كلمة المرور الافتراضية
                if admin_user.check_password('admin123'):
                    self.log_test("كلمة المرور الافتراضية", True, "كلمة المرور الافتراضية صحيحة")
                else:
                    self.log_test("كلمة المرور الافتراضية", False, "كلمة المرور الافتراضية غير صحيحة")
                    return False
                
                # اختبار الصلاحيات
                if admin_user.role == 'admin' and admin_user.has_permission('manage_users'):
                    self.log_test("صلاحيات المدير", True, "صلاحيات المدير مضبوطة بشكل صحيح")
                else:
                    self.log_test("صلاحيات المدير", False, "خطأ في صلاحيات المدير")
                    return False
                
                return True
        except Exception as e:
            self.log_test("المستخدم الافتراضي", False, f"خطأ: {str(e)}")
            return False
    
    def test_default_settings(self):
        """اختبار الإعدادات الافتراضية"""
        try:
            with self.app.app_context():
                # اختبار وجود الإعدادات الأساسية
                required_settings = [
                    'company_name',
                    'language',
                    'currency',
                    'theme',
                    'timezone'
                ]
                
                missing_settings = []
                for setting_key in required_settings:
                    setting = SystemSettings.query.filter_by(setting_key=setting_key).first()
                    if not setting:
                        missing_settings.append(setting_key)
                
                if not missing_settings:
                    self.log_test("الإعدادات الافتراضية", True, "جميع الإعدادات الأساسية موجودة")
                else:
                    self.log_test("الإعدادات الافتراضية", False, f"إعدادات مفقودة: {', '.join(missing_settings)}")
                    return False
                
                # اختبار تصنيف الإعدادات
                categories = db.session.query(SystemSettings.category).distinct().all()
                category_list = [cat[0] for cat in categories]
                
                expected_categories = ['general', 'appearance', 'security', 'printing', 'localization']
                missing_categories = [cat for cat in expected_categories if cat not in category_list]
                
                if not missing_categories:
                    self.log_test("تصنيف الإعدادات", True, f"جميع التصنيفات موجودة: {', '.join(category_list)}")
                else:
                    self.log_test("تصنيف الإعدادات", False, f"تصنيفات مفقودة: {', '.join(missing_categories)}")
                
                return True
        except Exception as e:
            self.log_test("الإعدادات الافتراضية", False, f"خطأ: {str(e)}")
            return False
    
    def test_flask_login_integration(self):
        """اختبار تكامل Flask-Login"""
        try:
            with self.app.app_context():
                # اختبار وجود login_manager
                if hasattr(self.app, 'login_manager'):
                    self.log_test("Flask-Login Integration", True, "Flask-Login مُعد بشكل صحيح")
                else:
                    self.log_test("Flask-Login Integration", False, "Flask-Login غير مُعد")
                    return False
                
                # اختبار user_loader
                from flask_login import login_manager
                if login_manager._user_callback:
                    self.log_test("User Loader Function", True, "دالة تحميل المستخدم موجودة")
                else:
                    self.log_test("User Loader Function", False, "دالة تحميل المستخدم مفقودة")
                    return False
                
                return True
        except Exception as e:
            self.log_test("Flask-Login Integration", False, f"خطأ: {str(e)}")
            return False
    
    def test_routes_exist(self):
        """اختبار وجود المسارات المطلوبة"""
        try:
            with self.app.app_context():
                # قائمة المسارات المطلوبة
                required_routes = [
                    'login',
                    'logout',
                    'settings',
                    'add_user',
                    'edit_user',
                    'delete_user',
                    'update_settings'
                ]
                
                # الحصول على جميع المسارات المتاحة
                available_routes = []
                for rule in self.app.url_map.iter_rules():
                    if rule.endpoint:
                        available_routes.append(rule.endpoint)
                
                missing_routes = [route for route in required_routes if route not in available_routes]
                
                if not missing_routes:
                    self.log_test("المسارات المطلوبة", True, f"جميع المسارات موجودة ({len(required_routes)} مسار)")
                else:
                    self.log_test("المسارات المطلوبة", False, f"مسارات مفقودة: {', '.join(missing_routes)}")
                    return False
                
                return True
        except Exception as e:
            self.log_test("المسارات المطلوبة", False, f"خطأ: {str(e)}")
            return False
    
    def run_all_tests(self):
        """تشغيل جميع الاختبارات"""
        print("🧪 بدء اختبار نظام المستخدمين والإعدادات")
        print("=" * 60)
        
        # تشغيل الاختبارات
        tests = [
            self.test_database_connection,
            self.test_user_model,
            self.test_system_settings_model,
            self.test_default_admin_user,
            self.test_default_settings,
            self.test_flask_login_integration,
            self.test_routes_exist
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                self.log_test(test.__name__, False, f"خطأ غير متوقع: {str(e)}")
        
        # عرض النتائج
        self.display_results()
        
        return self.test_results['failed_tests'] == 0
    
    def display_results(self):
        """عرض نتائج الاختبارات"""
        print("\n" + "=" * 60)
        print("📊 نتائج الاختبارات")
        print("=" * 60)
        
        total = self.test_results['total_tests']
        passed = self.test_results['passed_tests']
        failed = self.test_results['failed_tests']
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"إجمالي الاختبارات: {total}")
        print(f"الاختبارات الناجحة: {passed}")
        print(f"الاختبارات الفاشلة: {failed}")
        print(f"معدل النجاح: {success_rate:.1f}%")
        
        if failed == 0:
            print("\n🎉 جميع الاختبارات نجحت! النظام جاهز للاستخدام.")
        else:
            print(f"\n⚠️  {failed} اختبار فشل. يرجى مراجعة التفاصيل أعلاه.")
        
        print("=" * 60)
    
    def save_report(self, filename='user_system_test_report.json'):
        """حفظ تقرير الاختبارات"""
        try:
            report = {
                'test_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'system_info': {
                    'python_version': sys.version,
                    'flask_app': str(self.app),
                    'database_uri': self.app.config.get('SQLALCHEMY_DATABASE_URI', 'غير محدد')
                },
                'results': self.test_results
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            
            print(f"💾 تم حفظ تقرير الاختبارات في: {filename}")
            return True
        except Exception as e:
            print(f"❌ فشل في حفظ التقرير: {str(e)}")
            return False

def main():
    """الدالة الرئيسية"""
    tester = UserSystemTester()
    success = tester.run_all_tests()
    tester.save_report()
    
    return success

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
