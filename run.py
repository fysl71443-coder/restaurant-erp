#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
تشغيل التطبيق الاحترافي
Professional Application Runner
"""

import os
import sys
import click
from flask.cli import with_appcontext
from app import create_app, db
from app.models import User, SystemSettings
from config import config

def create_application():
    """إنشاء تطبيق Flask مع الإعدادات المناسبة"""
    config_name = os.environ.get('FLASK_ENV') or 'development'
    app = create_app(config[config_name])
    return app

app = create_application()

@app.cli.command()
@click.option('--drop', is_flag=True, help='حذف الجداول الموجودة أولاً')
def init_db(drop):
    """تهيئة قاعدة البيانات"""
    if drop:
        click.echo('حذف الجداول الموجودة...')
        db.drop_all()
    
    click.echo('إنشاء الجداول...')
    db.create_all()
    
    # إنشاء المجلدات المطلوبة
    folders = ['logs', 'backups', 'uploads', 'static/uploads']
    for folder in folders:
        if not os.path.exists(folder):
            os.makedirs(folder)
            click.echo(f'تم إنشاء مجلد: {folder}')
    
    click.echo('✅ تم تهيئة قاعدة البيانات بنجاح')

@app.cli.command()
@click.option('--username', prompt='اسم المستخدم', help='اسم المستخدم للمدير')
@click.option('--email', prompt='البريد الإلكتروني', help='البريد الإلكتروني للمدير')
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='كلمة المرور')
@click.option('--full-name', prompt='الاسم الكامل', help='الاسم الكامل للمدير')
def create_admin(username, email, password, full_name):
    """إنشاء مستخدم مدير جديد"""
    
    # التحقق من وجود المستخدم
    if User.query.filter_by(username=username).first():
        click.echo(f'❌ المستخدم {username} موجود بالفعل')
        return
    
    if User.query.filter_by(email=email).first():
        click.echo(f'❌ البريد الإلكتروني {email} مستخدم بالفعل')
        return
    
    # إنشاء المستخدم المدير
    admin = User(
        username=username,
        email=email,
        full_name=full_name,
        role='super_admin',
        department='إدارة',
        is_active=True,
        can_view_reports=True,
        can_manage_invoices=True,
        can_manage_customers=True,
        can_manage_products=True,
        can_manage_employees=True,
        can_manage_payroll=True,
        can_manage_settings=True,
        can_manage_users=True
    )
    admin.set_password(password)
    
    db.session.add(admin)
    db.session.commit()
    
    click.echo(f'✅ تم إنشاء المستخدم المدير: {username}')

@app.cli.command()
def create_sample_data():
    """إنشاء بيانات تجريبية للاختبار"""
    from app.utils.sample_data import create_sample_data as create_data
    
    try:
        create_data()
        click.echo('✅ تم إنشاء البيانات التجريبية بنجاح')
    except Exception as e:
        click.echo(f'❌ خطأ في إنشاء البيانات التجريبية: {str(e)}')

@app.cli.command()
@click.option('--output', default='backup.sql', help='ملف النسخة الاحتياطية')
def backup_db(output):
    """إنشاء نسخة احتياطية من قاعدة البيانات"""
    from app.utils.backup import create_backup
    
    try:
        backup_file = create_backup(output)
        click.echo(f'✅ تم إنشاء النسخة الاحتياطية: {backup_file}')
    except Exception as e:
        click.echo(f'❌ خطأ في إنشاء النسخة الاحتياطية: {str(e)}')

@app.cli.command()
@click.option('--input', required=True, help='ملف النسخة الاحتياطية للاستعادة')
def restore_db(input):
    """استعادة قاعدة البيانات من نسخة احتياطية"""
    from app.utils.backup import restore_backup
    
    if not os.path.exists(input):
        click.echo(f'❌ الملف غير موجود: {input}')
        return
    
    if click.confirm('هل أنت متأكد من استعادة قاعدة البيانات؟ سيتم حذف البيانات الحالية.'):
        try:
            restore_backup(input)
            click.echo('✅ تم استعادة قاعدة البيانات بنجاح')
        except Exception as e:
            click.echo(f'❌ خطأ في استعادة قاعدة البيانات: {str(e)}')

@app.cli.command()
def test():
    """تشغيل الاختبارات"""
    import pytest
    
    # تشغيل الاختبارات
    exit_code = pytest.main(['-v', 'tests/'])
    
    if exit_code == 0:
        click.echo('✅ جميع الاختبارات نجحت')
    else:
        click.echo('❌ بعض الاختبارات فشلت')
    
    sys.exit(exit_code)

@app.cli.command()
def check_health():
    """فحص صحة التطبيق"""
    from app.utils.health_check import run_health_checks
    
    try:
        results = run_health_checks()
        
        all_passed = True
        for check_name, result in results.items():
            status = '✅' if result['status'] == 'ok' else '❌'
            click.echo(f'{status} {check_name}: {result["message"]}')
            if result['status'] != 'ok':
                all_passed = False
        
        if all_passed:
            click.echo('\n🎉 جميع فحوصات الصحة نجحت')
        else:
            click.echo('\n⚠️ بعض فحوصات الصحة فشلت')
            sys.exit(1)
            
    except Exception as e:
        click.echo(f'❌ خطأ في فحص الصحة: {str(e)}')
        sys.exit(1)

@app.cli.command()
@click.option('--port', default=5000, help='رقم المنفذ')
@click.option('--host', default='127.0.0.1', help='عنوان المضيف')
@click.option('--debug', is_flag=True, help='تفعيل وضع التطوير')
def serve(port, host, debug):
    """تشغيل الخادم"""
    
    # فحص صحة التطبيق قبل التشغيل
    click.echo('فحص صحة التطبيق...')
    try:
        from app.utils.health_check import run_health_checks
        results = run_health_checks()
        
        critical_failed = False
        for check_name, result in results.items():
            if result['status'] != 'ok' and result.get('critical', False):
                click.echo(f'❌ فحص حرج فشل: {check_name}')
                critical_failed = True
        
        if critical_failed:
            click.echo('❌ لا يمكن تشغيل التطبيق بسبب فشل فحوصات حرجة')
            sys.exit(1)
            
    except Exception as e:
        click.echo(f'⚠️ تحذير: لا يمكن فحص صحة التطبيق: {str(e)}')
    
    # تشغيل الخادم
    click.echo(f'🚀 تشغيل الخادم على http://{host}:{port}')
    
    if debug or app.config.get('DEBUG'):
        app.run(host=host, port=port, debug=True)
    else:
        # استخدام خادم إنتاج
        try:
            from waitress import serve as waitress_serve
            click.echo('استخدام خادم Waitress للإنتاج...')
            waitress_serve(app, host=host, port=port)
        except ImportError:
            click.echo('تحذير: Waitress غير مثبت، استخدام خادم Flask التطويري...')
            app.run(host=host, port=port, debug=False)

@app.cli.command()
def deploy():
    """إعداد التطبيق للنشر"""
    
    click.echo('🚀 إعداد التطبيق للنشر...')
    
    # فحص المتطلبات
    required_env_vars = ['SECRET_KEY', 'DATABASE_URL']
    missing_vars = []
    
    for var in required_env_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        click.echo(f'❌ متغيرات البيئة المطلوبة مفقودة: {", ".join(missing_vars)}')
        return
    
    # تهيئة قاعدة البيانات
    click.echo('تهيئة قاعدة البيانات...')
    db.create_all()
    
    # إنشاء المجلدات المطلوبة
    folders = ['logs', 'backups', 'uploads']
    for folder in folders:
        if not os.path.exists(folder):
            os.makedirs(folder)
    
    # فحص الصحة النهائي
    click.echo('فحص صحة التطبيق...')
    from app.utils.health_check import run_health_checks
    results = run_health_checks()
    
    all_passed = True
    for check_name, result in results.items():
        if result['status'] != 'ok':
            all_passed = False
            click.echo(f'❌ {check_name}: {result["message"]}')
    
    if all_passed:
        click.echo('✅ التطبيق جاهز للنشر!')
    else:
        click.echo('❌ التطبيق غير جاهز للنشر')
        sys.exit(1)

@app.cli.command()
def shell():
    """فتح shell تفاعلي مع سياق التطبيق"""
    import code
    
    # إضافة المتغيرات المفيدة للسياق
    context = {
        'app': app,
        'db': db,
        'User': User,
        'SystemSettings': SystemSettings
    }
    
    # إضافة جميع النماذج
    from app import models
    for attr_name in dir(models):
        attr = getattr(models, attr_name)
        if hasattr(attr, '__tablename__'):
            context[attr_name] = attr
    
    click.echo('🐍 Shell تفاعلي مع سياق التطبيق')
    click.echo('المتغيرات المتاحة: app, db, User, SystemSettings, وجميع النماذج')
    
    code.interact(local=context)

@app.cli.command()
def upgrade_db():
    """ترقية قاعدة البيانات مع الميزات الجديدة"""
    click.echo('🔄 ترقية قاعدة البيانات...')

    try:
        import subprocess
        result = subprocess.run([
            sys.executable, 'scripts/upgrade_database.py'
        ], capture_output=True, text=True)

        if result.returncode == 0:
            click.echo('✅ تمت ترقية قاعدة البيانات بنجاح!')
        else:
            click.echo(f'❌ فشلت ترقية قاعدة البيانات: {result.stderr}')
    except Exception as e:
        click.echo(f'❌ خطأ في ترقية قاعدة البيانات: {str(e)}')

@app.cli.command()
def security_test():
    """تشغيل اختبارات الأمان الشاملة"""
    click.echo('🔐 تشغيل اختبارات الأمان...')

    try:
        import subprocess
        result = subprocess.run([
            sys.executable, 'scripts/security_test.py'
        ], capture_output=True, text=True)

        if result.returncode == 0:
            click.echo('✅ جميع اختبارات الأمان نجحت!')
        else:
            click.echo('⚠️  بعض اختبارات الأمان فشلت. راجع السجلات للتفاصيل.')
    except Exception as e:
        click.echo(f'❌ خطأ في تشغيل اختبارات الأمان: {str(e)}')

@app.cli.command()
@click.option('--key', required=True, help='مفتاح الإعداد')
@click.option('--value', required=True, help='قيمة الإعداد')
@click.option('--category', default='general', help='فئة الإعداد')
def set_setting(key, value, category):
    """تعيين إعداد النظام"""
    from app.models.system_settings import SystemSettings

    try:
        setting = SystemSettings.set_setting(key, value, category)
        click.echo(f'✅ تم تعيين الإعداد: {key} = {value}')
    except Exception as e:
        click.echo(f'❌ خطأ في تعيين الإعداد: {str(e)}')

@app.cli.command()
@click.option('--key', help='مفتاح الإعداد المحدد')
@click.option('--category', help='فئة الإعدادات')
def get_settings(key, category):
    """عرض إعدادات النظام"""
    from app.models.system_settings import SystemSettings

    try:
        if key:
            # عرض إعداد محدد
            value = SystemSettings.get_setting(key)
            click.echo(f'{key}: {value}')
        elif category:
            # عرض إعدادات فئة محددة
            settings = SystemSettings.get_category_settings(category)
            for setting in settings:
                click.echo(f'{setting.key}: {setting.get_display_value()}')
        else:
            # عرض جميع الفئات
            categories = SystemSettings.get_all_categories()
            click.echo('الفئات المتاحة:')
            for cat in categories:
                click.echo(f'  - {cat}')
    except Exception as e:
        click.echo(f'❌ خطأ في عرض الإعدادات: {str(e)}')

@app.cli.command()
def system_info():
    """عرض معلومات النظام"""
    import platform
    import psutil
    from app.models.system_settings import SystemSettings

    click.echo('📊 معلومات النظام:')
    click.echo(f'🖥️  نظام التشغيل: {platform.system()} {platform.release()}')
    click.echo(f'🐍 إصدار Python: {platform.python_version()}')
    click.echo(f'💾 الذاكرة المتاحة: {psutil.virtual_memory().available // (1024**3)} GB')
    click.echo(f'💿 مساحة القرص المتاحة: {psutil.disk_usage("/").free // (1024**3)} GB')

    with app.app_context():
        app_name = SystemSettings.get_setting('app_name', 'نظام المحاسبة')
        app_version = SystemSettings.get_setting('app_version', '2.0.0')
        click.echo(f'📱 اسم التطبيق: {app_name}')
        click.echo(f'🔢 إصدار التطبيق: {app_version}')

if __name__ == '__main__':
    # تشغيل التطبيق مباشرة
    if len(sys.argv) == 1:
        # إذا لم يتم تمرير أي معاملات، تشغيل الخادم
        app.run(debug=True)
    else:
        # تشغيل أوامر CLI
        app.cli()
