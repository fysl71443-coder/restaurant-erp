#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
إعادة إنشاء قاعدة البيانات بشكل بسيط
"""

import os
from app import app, db

def simple_reset():
    """إعادة إنشاء قاعدة البيانات بشكل بسيط"""
    with app.app_context():
        print("🔄 إعادة إنشاء قاعدة البيانات...")
        
        # حذف قاعدة البيانات الموجودة
        db_files = ['accounting.db', 'instance/accounting_system.db']
        for db_file in db_files:
            if os.path.exists(db_file):
                os.remove(db_file)
                print(f"✅ تم حذف {db_file}")
        
        # إنشاء قاعدة البيانات الجديدة
        db.create_all()
        print("✅ تم إنشاء قاعدة البيانات الجديدة")
        
        print("🎉 تم إعادة إنشاء قاعدة البيانات بنجاح!")

if __name__ == "__main__":
    simple_reset()
