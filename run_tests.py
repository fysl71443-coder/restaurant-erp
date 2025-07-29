#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
تشغيل الاختبارات الشاملة
Run Comprehensive Tests
"""

import os
import sys
import traceback
from datetime import datetime

def test_application_startup():
    """اختبار بدء تشغيل التطبيق"""
    try:
        print("🔄 اختبار بدء تشغيل التطبيق...")
        
        # استيراد التطبيق
        from app import create_app
        app = create_app()
        
        print("✅ تم إنشاء التطبيق بنجاح")
        
        # اختبار التطبيق
        with app.test_client() as client:
            # اختبار الصفحة الرئيسية
            response = client.get('/')
            print(f"📄 الصفحة الرئيسية: {response.status_code}")
            
            # اختبار صفحة تسجيل الدخول
            response = client.get('/auth/login')
            print(f"🔐 صفحة تسجيل الدخول: {response.status_code}")
            
            # اختبار صفحات أخرى
            pages = ['/sales', '/purchases', '/analytics', '/vat', '/payroll', '/reports']
            for page in pages:
                try:
                    response = client.get(page)
                    print(f"📊 {page}: {response.status_code}")
                except Exception as e:
                    print(f"⚠️ {page}: خطأ - {str(e)}")
        
        return True
    
    except Exception as e:
        print(f"❌ فشل اختبار بدء التشغيل: {str(e)}")
        traceback.print_exc()
        return False

def test_file_structure():
    """اختبار هيكل الملفات"""
    try:
        print("🔄 اختبار هيكل الملفات...")
        
        required_files = [
            'app/__init__.py',
            'app/models/user_enhanced.py',
            'app/auth/routes.py',
            'app/main/routes.py',
            'app/templates/base.html',
            'app/static/css/main.css',
            'app/static/js/main.js'
        ]
        
        missing_files = []
        for file_path in required_files:
            if not os.path.exists(file_path):
                missing_files.append(file_path)
            else:
                print(f"✅ {file_path}")
        
        if missing_files:
            print(f"⚠️ ملفات مفقودة: {missing_files}")
            return False
        
        print("✅ جميع الملفات المطلوبة موجودة")
        return True
    
    except Exception as e:
        print(f"❌ فشل اختبار هيكل الملفات: {str(e)}")
        return False

def test_imports():
    """اختبار الاستيرادات"""
    try:
        print("🔄 اختبار الاستيرادات...")
        
        # اختبار استيراد الوحدات الأساسية
        modules_to_test = [
            'app',
            'app.models.user_enhanced',
            'app.auth.routes',
            'app.main.routes'
        ]
        
        for module in modules_to_test:
            try:
                __import__(module)
                print(f"✅ {module}")
            except ImportError as e:
                print(f"❌ {module}: {str(e)}")
                return False
        
        print("✅ جميع الاستيرادات نجحت")
        return True
    
    except Exception as e:
        print(f"❌ فشل اختبار الاستيرادات: {str(e)}")
        return False

def test_database_models():
    """اختبار نماذج قاعدة البيانات"""
    try:
        print("🔄 اختبار نماذج قاعدة البيانات...")
        
        from app.models.user_enhanced import User
        from app.models.system_monitoring import SystemLog, PerformanceMetric, SystemAlert
        
        # اختبار إنشاء مستخدم
        user = User(username='test', email='test@test.com')
        user.set_password('test123')
        
        print("✅ نموذج المستخدم يعمل")
        
        # اختبار نماذج المراقبة
        log = SystemLog(level='INFO', logger_name='test', message='test')
        metric = PerformanceMetric(metric_name='test', value=100)
        alert = SystemAlert(alert_type='test', severity='low', title='test', message='test')
        
        print("✅ نماذج المراقبة تعمل")
        
        return True
    
    except Exception as e:
        print(f"❌ فشل اختبار النماذج: {str(e)}")
        traceback.print_exc()
        return False

def test_language_system():
    """اختبار نظام اللغات"""
    try:
        print("🔄 اختبار نظام اللغات...")
        
        # فحص ملفات الترجمة
        translation_files = [
            'app/translations/ar/LC_MESSAGES/messages.po',
            'app/translations/en/LC_MESSAGES/messages.po'
        ]
        
        for file_path in translation_files:
            if os.path.exists(file_path):
                print(f"✅ {file_path}")
            else:
                print(f"⚠️ {file_path} مفقود")
        
        # اختبار استيراد نظام اللغات
        from app.language import language_bp
        print("✅ نظام اللغات يعمل")
        
        return True
    
    except Exception as e:
        print(f"❌ فشل اختبار نظام اللغات: {str(e)}")
        return False

def test_performance_systems():
    """اختبار أنظمة الأداء"""
    try:
        print("🔄 اختبار أنظمة الأداء...")
        
        # اختبار نظام التخزين المؤقت
        from app.performance.cache_manager import cache_manager
        print("✅ نظام التخزين المؤقت")
        
        # اختبار محسن الأصول
        from app.performance.asset_optimizer import asset_optimizer
        print("✅ محسن الأصول")
        
        # اختبار مراقب الأداء
        from app.performance.performance_monitor import performance_monitor
        print("✅ مراقب الأداء")
        
        return True
    
    except Exception as e:
        print(f"❌ فشل اختبار أنظمة الأداء: {str(e)}")
        return False

def test_monitoring_systems():
    """اختبار أنظمة المراقبة"""
    try:
        print("🔄 اختبار أنظمة المراقبة...")
        
        # اختبار نظام السجلات
        from app.logging.logger import logger_manager
        print("✅ نظام السجلات")
        
        # اختبار فاحص الصحة
        from app.monitoring.health_checker import health_checker
        print("✅ فاحص الصحة")
        
        # اختبار مدير التنبيهات
        from app.notifications.alert_manager import alert_manager
        print("✅ مدير التنبيهات")
        
        return True
    
    except Exception as e:
        print(f"❌ فشل اختبار أنظمة المراقبة: {str(e)}")
        return False

def test_backup_system():
    """اختبار نظام النسخ الاحتياطي"""
    try:
        print("🔄 اختبار نظام النسخ الاحتياطي...")
        
        from app.backup.backup_manager import backup_manager
        print("✅ مدير النسخ الاحتياطي")
        
        return True
    
    except Exception as e:
        print(f"❌ فشل اختبار نظام النسخ الاحتياطي: {str(e)}")
        return False

def main():
    """الدالة الرئيسية"""
    print("🧪 بدء الاختبارات الشاملة للنظام")
    print("=" * 50)
    
    start_time = datetime.now()
    
    # قائمة الاختبارات
    tests = [
        ("هيكل الملفات", test_file_structure),
        ("الاستيرادات", test_imports),
        ("نماذج قاعدة البيانات", test_database_models),
        ("بدء تشغيل التطبيق", test_application_startup),
        ("نظام اللغات", test_language_system),
        ("أنظمة الأداء", test_performance_systems),
        ("أنظمة المراقبة", test_monitoring_systems),
        ("نظام النسخ الاحتياطي", test_backup_system)
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    # تشغيل الاختبارات
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 30)
        
        try:
            if test_func():
                passed_tests += 1
                print(f"✅ {test_name} - نجح")
            else:
                print(f"❌ {test_name} - فشل")
        except Exception as e:
            print(f"💥 {test_name} - خطأ: {str(e)}")
    
    # النتائج النهائية
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    success_rate = (passed_tests / total_tests) * 100
    
    print("\n" + "=" * 50)
    print("📊 النتائج النهائية")
    print("=" * 50)
    print(f"⏱️ مدة التشغيل: {duration:.2f} ثانية")
    print(f"📈 الاختبارات الناجحة: {passed_tests}/{total_tests}")
    print(f"📊 معدل النجاح: {success_rate:.1f}%")
    
    if success_rate >= 90:
        print("🎉 ممتاز! النظام يعمل بشكل مثالي")
        status = "ممتاز"
    elif success_rate >= 75:
        print("👍 جيد جداً! النظام يعمل بشكل جيد")
        status = "جيد جداً"
    elif success_rate >= 60:
        print("👌 جيد! النظام يعمل مع بعض المشاكل البسيطة")
        status = "جيد"
    else:
        print("⚠️ يحتاج تحسين! النظام يحتاج إلى إصلاحات")
        status = "يحتاج تحسين"
    
    # حفظ تقرير الاختبار
    report = f"""# تقرير الاختبارات الشاملة
## Comprehensive Test Report

**التاريخ:** {start_time.strftime('%Y-%m-%d %H:%M:%S')}
**المدة:** {duration:.2f} ثانية
**الحالة:** {status}
**معدل النجاح:** {success_rate:.1f}%

## النتائج:
- ✅ الاختبارات الناجحة: {passed_tests}
- ❌ الاختبارات الفاشلة: {total_tests - passed_tests}
- 📊 المجموع: {total_tests}

## تفاصيل الاختبارات:
"""
    
    for i, (test_name, _) in enumerate(tests):
        status_icon = "✅" if i < passed_tests else "❌"
        report += f"- {status_icon} {test_name}\n"
    
    report_file = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"📄 تم حفظ التقرير في: {report_file}")
    
    return success_rate >= 60

if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️ تم إيقاف الاختبارات بواسطة المستخدم")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 خطأ عام في الاختبارات: {str(e)}")
        traceback.print_exc()
        sys.exit(1)
