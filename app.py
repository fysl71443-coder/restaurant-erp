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

# استيراد النظام المبسط المتوافق مع Python 3.13
from simple_accounting import app

# للنشر على Render
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
