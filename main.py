#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نقطة دخول نظام المحاسبة الاحترافي
Entry point for Professional Accounting System
"""

# استيراد النظام الرئيسي
from accounting_system_pro import app, init_database

if __name__ == '__main__':
    # تهيئة قاعدة البيانات
    init_database()
    
    # تشغيل التطبيق
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
else:
    # للنشر على Render
    init_database()
