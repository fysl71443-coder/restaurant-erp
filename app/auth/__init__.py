#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نظام المصادقة المتقدم
Advanced Authentication System
"""

from flask import Blueprint

# إنشاء blueprint للمصادقة
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# استيراد المسارات
from . import routes, forms, utils

__all__ = ['auth_bp']
