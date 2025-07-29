#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نظام السجلات والمراقبة المتقدم
Advanced Logging and Monitoring System
"""

from flask import Blueprint

# إنشاء blueprint للسجلات
logging_bp = Blueprint('logging', __name__, url_prefix='/logging')

# استيراد المسارات
from . import routes

__all__ = ['logging_bp']
