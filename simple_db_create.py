#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from flask import Flask
from database import db, init_db

# حذف قاعدة البيانات القديمة إن وجدت
if os.path.exists('accounting_system.db'):
    os.remove('accounting_system.db')
    print("✅ تم حذف قاعدة البيانات القديمة")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///accounting_system.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# تهيئة قاعدة البيانات
init_db(app)

with app.app_context():
    db.create_all()
    print("✅ تم إنشاء قاعدة البيانات الجديدة")
    
    # إضافة بيانات أساسية
    from database import Customer, Supplier
    
    # التحقق من وجود البيانات أولاً
    existing_customers = Customer.query.count()
    if existing_customers == 0:
        # إضافة عملاء
        customers = [
            Customer(name="أحمد محمد", email="ahmed@example.com", phone="0501234567"),
            Customer(name="فاطمة علي", email="fatima@example.com", phone="0509876543"),
            Customer(name="محمد سعد", email="mohammed@example.com", phone="0505555555")
        ]

        for customer in customers:
            db.session.add(customer)
        print("✅ تم إضافة العملاء")

    existing_suppliers = Supplier.query.count()
    if existing_suppliers == 0:
        # إضافة موردين
        suppliers = [
            Supplier(name="شركة التوريدات المتقدمة", contact_info="info@advanced.com - 0112345678"),
            Supplier(name="مؤسسة الجودة التجارية", contact_info="sales@quality.com - 0113456789"),
            Supplier(name="مكتب الخدمات الشاملة", contact_info="office@services.com - 0114567890")
        ]

        for supplier in suppliers:
            db.session.add(supplier)
        print("✅ تم إضافة الموردين")

    try:
        db.session.commit()
        print("✅ تم حفظ البيانات الأساسية")
    except Exception as e:
        print(f"❌ خطأ في حفظ البيانات: {e}")
        db.session.rollback()
    
print("🎉 تم إنشاء قاعدة البيانات بنجاح!")
