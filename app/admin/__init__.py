#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نظام الإدارة المتقدم
Advanced Administration System
"""

from flask import Blueprint

# إنشاء blueprint للإدارة
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# استيراد المسارات
from . import routes

__all__ = ['admin_bp']
