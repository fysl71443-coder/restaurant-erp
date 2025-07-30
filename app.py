#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نقطة دخول نظام المحاسبة الاحترافي - محسن لـ Render
Entry point for Professional Accounting System - Render Optimized
"""

import os
import sys

# إضافة المسار الحالي
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # استيراد النظام الرئيسي
    from accounting_system_pro import app, init_database
    
    # تهيئة قاعدة البيانات عند الاستيراد
    with app.app_context():
        init_database()
    
    # للنشر على Render
    if __name__ == '__main__':
        port = int(os.environ.get('PORT', 5000))
        app.run(host='0.0.0.0', port=port, debug=False)
        
except ImportError as e:
    print(f"خطأ في الاستيراد: {e}")
    # إنشاء تطبيق بسيط في حالة فشل الاستيراد
    from flask import Flask
    app = Flask(__name__)
    
    @app.route('/')
    def hello():
        return '''
        <h1>نظام المحاسبة الاحترافي</h1>
        <p>يتم تحميل النظام...</p>
        <p>إذا استمرت هذه الرسالة، يرجى التحقق من السجلات.</p>
        '''
    
    if __name__ == '__main__':
        port = int(os.environ.get('PORT', 5000))
        app.run(host='0.0.0.0', port=port, debug=False)
