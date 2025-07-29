#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ملف تشغيل الخادم
Server Runner
"""

import os
import sys

def main():
    """تشغيل الخادم"""
    print("🚀 بدء تشغيل نظام المحاسبة العربي...")
    print("Starting Arabic Accounting System...")
    
    try:
        # استيراد التطبيق
        from app import app
        
        print("✅ تم تحميل التطبيق بنجاح")
        print("Application loaded successfully")
        
        # تشغيل الخادم
        print("🌐 تشغيل الخادم على العنوان: http://localhost:5000")
        print("Server running at: http://localhost:5000")
        print("=" * 50)
        
        app.run(
            debug=True,
            host='0.0.0.0',
            port=5000,
            threaded=True
        )
        
    except ImportError as e:
        print(f"❌ خطأ في الاستيراد: {e}")
        print(f"Import error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ خطأ في التشغيل: {e}")
        print(f"Runtime error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
