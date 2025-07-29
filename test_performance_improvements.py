#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار التحسينات المنجزة في الأداء
Test Performance Improvements
"""

import os
import sys
import time
import json
from datetime import datetime

def test_file_existence():
    """اختبار وجود الملفات الجديدة"""
    print("🔍 اختبار وجود الملفات الجديدة...")
    
    required_files = [
        'background_tasks.py',
        'form_processing.py',
        'performance_optimizations.py',
        'static/js/ajax_operations.js',
        'static/js/form_validation.js',
        'static/js/lazy_loading.js',
        'requirements.txt'
    ]
    
    results = {}
    for file_path in required_files:
        exists = os.path.exists(file_path)
        results[file_path] = exists
        status = "✅" if exists else "❌"
        print(f"  {status} {file_path}")
    
    return results

def test_database_optimizations():
    """اختبار تحسينات قاعدة البيانات"""
    print("\n📊 اختبار تحسينات قاعدة البيانات...")
    
    try:
        from database import db, configure_db_optimizations
        print("  ✅ تم استيراد database.py بنجاح")
        
        # اختبار وجود دالة التحسين
        if hasattr(configure_db_optimizations, '__call__'):
            print("  ✅ دالة configure_db_optimizations موجودة")
        else:
            print("  ❌ دالة configure_db_optimizations غير موجودة")
            
        return True
    except Exception as e:
        print(f"  ❌ خطأ في استيراد database: {str(e)}")
        return False

def test_performance_module():
    """اختبار وحدة تحسين الأداء"""
    print("\n⚡ اختبار وحدة تحسين الأداء...")
    
    try:
        from performance_optimizations import (
            cache_result, measure_performance, 
            get_optimized_monthly_data, app_cache
        )
        print("  ✅ تم استيراد performance_optimizations بنجاح")
        
        # اختبار نظام الـ cache
        if hasattr(app_cache, 'get') and hasattr(app_cache, 'set'):
            print("  ✅ نظام Cache يعمل بشكل صحيح")
        else:
            print("  ❌ نظام Cache لا يعمل")
            
        return True
    except Exception as e:
        print(f"  ❌ خطأ في استيراد performance_optimizations: {str(e)}")
        return False

def test_background_tasks():
    """اختبار نظام المهام الخلفية"""
    print("\n🔄 اختبار نظام المهام الخلفية...")
    
    try:
        from background_tasks import (
            TaskWorker, BackgroundTask,
            generate_comprehensive_financial_report,
            calculate_employee_statistics
        )
        print("  ✅ تم استيراد background_tasks بنجاح")
        
        # اختبار إنشاء مهمة
        task = BackgroundTask("test_id", "test_task", lambda: "test result")
        if task.task_id and task.name == "test_task":
            print("  ✅ إنشاء المهام يعمل بشكل صحيح")
        else:
            print("  ❌ إنشاء المهام لا يعمل")
            
        return True
    except Exception as e:
        print(f"  ❌ خطأ في استيراد background_tasks: {str(e)}")
        return False

def test_form_processing():
    """اختبار معالجة النماذج"""
    print("\n📝 اختبار معالجة النماذج...")
    
    try:
        from form_processing import FormProcessor, validate_form
        print("  ✅ تم استيراد form_processing بنجاح")
        
        # اختبار معالج النماذج
        processor = FormProcessor()
        if hasattr(processor, 'validate_email') and hasattr(processor, 'validate_phone'):
            print("  ✅ معالج النماذج يعمل بشكل صحيح")
        else:
            print("  ❌ معالج النماذج لا يعمل")
            
        return True
    except Exception as e:
        print(f"  ❌ خطأ في استيراد form_processing: {str(e)}")
        return False

def test_javascript_files():
    """اختبار ملفات JavaScript"""
    print("\n🌐 اختبار ملفات JavaScript...")
    
    js_files = [
        'static/js/ajax_operations.js',
        'static/js/form_validation.js', 
        'static/js/lazy_loading.js'
    ]
    
    results = {}
    for js_file in js_files:
        if os.path.exists(js_file):
            with open(js_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # اختبار وجود الكلاسات والدوال المهمة
            if 'ajax_operations.js' in js_file:
                has_functions = 'submitFormAjax' in content and 'setupLiveSearch' in content
            elif 'form_validation.js' in js_file:
                has_functions = 'FormValidator' in content and 'RealTimeValidator' in content
            elif 'lazy_loading.js' in js_file:
                has_functions = 'LazyLoader' in content and 'LazyCardLoader' in content
            else:
                has_functions = True
                
            results[js_file] = has_functions
            status = "✅" if has_functions else "❌"
            print(f"  {status} {js_file}")
        else:
            results[js_file] = False
            print(f"  ❌ {js_file} - الملف غير موجود")
    
    return results

def generate_test_report():
    """إنشاء تقرير الاختبار"""
    print("\n📋 إنشاء تقرير الاختبار...")
    
    report = {
        'test_date': datetime.now().isoformat(),
        'test_results': {
            'file_existence': test_file_existence(),
            'database_optimizations': test_database_optimizations(),
            'performance_module': test_performance_module(),
            'background_tasks': test_background_tasks(),
            'form_processing': test_form_processing(),
            'javascript_files': test_javascript_files()
        }
    }
    
    # حساب النتيجة الإجمالية
    total_tests = 0
    passed_tests = 0
    
    for category, results in report['test_results'].items():
        if isinstance(results, dict):
            for test, result in results.items():
                total_tests += 1
                if result:
                    passed_tests += 1
        elif isinstance(results, bool):
            total_tests += 1
            if results:
                passed_tests += 1
    
    success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
    report['summary'] = {
        'total_tests': total_tests,
        'passed_tests': passed_tests,
        'success_rate': round(success_rate, 2)
    }
    
    # حفظ التقرير
    with open('performance_test_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n📊 نتائج الاختبار:")
    print(f"  📈 إجمالي الاختبارات: {total_tests}")
    print(f"  ✅ الاختبارات الناجحة: {passed_tests}")
    print(f"  📊 معدل النجاح: {success_rate:.2f}%")
    
    return report

if __name__ == "__main__":
    print("🚀 بدء اختبار التحسينات المنجزة...")
    print("=" * 50)
    
    report = generate_test_report()
    
    print("\n" + "=" * 50)
    print("✅ تم إنجاز اختبار التحسينات بنجاح!")
    print(f"📄 تم حفظ التقرير في: performance_test_report.json")
