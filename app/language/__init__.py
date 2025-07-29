#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نظام اللغات المتعددة
Multi-Language System
"""

from flask import Blueprint

# إنشاء blueprint للغات
language_bp = Blueprint('language', __name__, url_prefix='/language')

# استيراد المسارات
from . import routes

__all__ = ['language_bp']
