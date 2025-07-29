#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نظام النسخ الاحتياطي
Backup System
"""

from flask import Blueprint

# إنشاء blueprint للنسخ الاحتياطي
backup_bp = Blueprint('backup', __name__, url_prefix='/backup')

# استيراد المسارات
from . import routes

__all__ = ['backup_bp']
