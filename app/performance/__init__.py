#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نظام تحسين الأداء
Performance Optimization System
"""

from flask import Blueprint

# إنشاء blueprint لتحسين الأداء
performance_bp = Blueprint('performance', __name__, url_prefix='/performance')

# استيراد المسارات
from . import routes

__all__ = ['performance_bp']
