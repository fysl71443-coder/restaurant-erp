#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار مبسط للتحسينات
Simple Test for Improvements
"""

import os
import json
from datetime import datetime

def test_files():
    """اختبار وجود الملفات"""
    print("🔍 اختبار وجود الملفات...")
    
    files = [
        'background_tasks.py',
        'form_processing.py', 
        'performance_optimizations.py',
        'static/js/ajax_operations.js',
        'static/js/form_validation.js',
        'static/js/lazy_loading.js',
        'requirements.txt',
        'SERVER_PERFORMANCE_IMPROVEMENTS_REPORT.md'
    ]
    
    results = {}
    for file_path in files:
        exists = os.path.exists(file_path)
        results[file_path] = exists
        status = "✅" if exists else "❌"
        print(f"  {status} {file_path}")
    
    return results

def test_imports():
    """اختبار الاستيرادات"""
    print("\n📦 اختبار الاستيرادات...")
    
    tests = {}
    
    # اختبار database
    try:
        from database import db, configure_db_optimizations
        tests['database'] = True
        print("  ✅ database.py")
    except Exception as e:
        tests['database'] = False
        print(f"  ❌ database.py: {str(e)}")
    
    # اختبار performance_optimizations
    try:
        from performance_optimizations import cache_result, measure_performance
        tests['performance'] = True
        print("  ✅ performance_optimizations.py")
    except Exception as e:
        tests['performance'] = False
        print(f"  ❌ performance_optimizations.py: {str(e)}")
    
    # اختبار form_processing
    try:
        from form_processing import FormProcessor
        tests['form_processing'] = True
        print("  ✅ form_processing.py")
    except Exception as e:
        tests['form_processing'] = False
        print(f"  ❌ form_processing.py: {str(e)}")
    
    return tests

def test_js_content():
    """اختبار محتوى ملفات JavaScript"""
    print("\n🌐 اختبار ملفات JavaScript...")
    
    js_tests = {}
    
    # اختبار ajax_operations.js
    if os.path.exists('static/js/ajax_operations.js'):
        with open('static/js/ajax_operations.js', 'r', encoding='utf-8') as f:
            content = f.read()
        has_ajax = 'submitFormAjax' in content and 'setupLiveSearch' in content
        js_tests['ajax_operations'] = has_ajax
        status = "✅" if has_ajax else "❌"
        print(f"  {status} ajax_operations.js")
    else:
        js_tests['ajax_operations'] = False
        print("  ❌ ajax_operations.js - غير موجود")
    
    # اختبار form_validation.js
    if os.path.exists('static/js/form_validation.js'):
        with open('static/js/form_validation.js', 'r', encoding='utf-8') as f:
            content = f.read()
        has_validation = 'FormValidator' in content and 'RealTimeValidator' in content
        js_tests['form_validation'] = has_validation
        status = "✅" if has_validation else "❌"
        print(f"  {status} form_validation.js")
    else:
        js_tests['form_validation'] = False
        print("  ❌ form_validation.js - غير موجود")
    
    # اختبار lazy_loading.js
    if os.path.exists('static/js/lazy_loading.js'):
        with open('static/js/lazy_loading.js', 'r', encoding='utf-8') as f:
            content = f.read()
        has_lazy = 'LazyLoader' in content and 'LazyCardLoader' in content
        js_tests['lazy_loading'] = has_lazy
        status = "✅" if has_lazy else "❌"
        print(f"  {status} lazy_loading.js")
    else:
        js_tests['lazy_loading'] = False
        print("  ❌ lazy_loading.js - غير موجود")
    
    return js_tests

def main():
    """الدالة الرئيسية"""
    print("🚀 اختبار التحسينات المنجزة")
    print("=" * 40)
    
    # تشغيل الاختبارات
    file_results = test_files()
    import_results = test_imports()
    js_results = test_js_content()
    
    # حساب النتائج
    all_results = {**file_results, **import_results, **js_results}
    total = len(all_results)
    passed = sum(1 for result in all_results.values() if result)
    success_rate = (passed / total) * 100 if total > 0 else 0
    
    print(f"\n📊 النتائج النهائية:")
    print(f"  📈 إجمالي الاختبارات: {total}")
    print(f"  ✅ الاختبارات الناجحة: {passed}")
    print(f"  📊 معدل النجاح: {success_rate:.1f}%")
    
    # حفظ التقرير
    report = {
        'test_date': datetime.now().isoformat(),
        'results': {
            'files': file_results,
            'imports': import_results,
            'javascript': js_results
        },
        'summary': {
            'total': total,
            'passed': passed,
            'success_rate': round(success_rate, 1)
        }
    }
    
    with open('simple_test_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n📄 تم حفظ التقرير في: simple_test_report.json")
    print("=" * 40)
    print("✅ انتهى الاختبار بنجاح!")

if __name__ == "__main__":
    main()
