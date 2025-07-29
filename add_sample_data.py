#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
إضافة بيانات تجريبية للفواتير
"""

from app import app, db
from database import Customer, Supplier, Invoice, PurchaseInvoice
from datetime import datetime
import random

def add_sample_data():
    """إضافة بيانات تجريبية"""
    with app.app_context():
        print("📊 إضافة بيانات تجريبية للفواتير...")
        
        try:
            # إضافة عملاء إذا لم يكونوا موجودين
            if Customer.query.count() == 0:
                customers = [
                    Customer(name='شركة التجارة المتقدمة', email='info@advanced.com', phone='0501234567'),
                    Customer(name='مؤسسة الأعمال الحديثة', email='contact@modern.com', phone='0507654321'),
                    Customer(name='شركة الخدمات المتكاملة', email='services@integrated.com', phone='0551234567')
                ]
                
                for customer in customers:
                    db.session.add(customer)
                print("✅ تم إضافة العملاء")
            
            # إضافة موردين إذا لم يكونوا موجودين
            if Supplier.query.count() == 0:
                suppliers = [
                    Supplier(name='شركة الإمداد الحديثة', contact_info='supply@modern.com'),
                    Supplier(name='مؤسسة التوريد المتقدمة', contact_info='advanced@supply.com'),
                    Supplier(name='شركة المواد الأساسية', contact_info='materials@basic.com')
                ]
                
                for supplier in suppliers:
                    db.session.add(supplier)
                print("✅ تم إضافة الموردين")
            
            db.session.commit()
            print("🎉 تم إضافة البيانات التجريبية بنجاح!")
            
        except Exception as e:
            print(f"❌ خطأ في إضافة البيانات: {str(e)}")
            db.session.rollback()

if __name__ == "__main__":
    add_sample_data()
