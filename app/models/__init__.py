#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نماذج قاعدة البيانات الاحترافية
Professional Database Models
"""

# النماذج الأساسية المحسنة
from app.models.base import BaseModel, AuditMixin, EncryptedMixin
from app.models.user import User, Role, Permission, UserRole, RolePermission
from app.models.audit_log import AuditLog

# النماذج المحسنة الجديدة
from app.models.customer import Customer
from app.models.invoice import Invoice
from app.models.invoice_item import InvoiceItem
from app.models.payment import Payment
from app.models.system_settings import SystemSettings

# النماذج الموجودة (سيتم تحديثها لاحقاً)
try:
    from app.models.supplier import Supplier
except ImportError:
    Supplier = None

try:
    from app.models.product import Product
except ImportError:
    Product = None

try:
    from app.models.purchase_invoice import PurchaseInvoice
except ImportError:
    PurchaseInvoice = None

try:
    from app.models.expense import Expense
except ImportError:
    Expense = None

try:
    from app.models.employee import Employee
except ImportError:
    Employee = None

try:
    from app.models.attendance import Attendance
except ImportError:
    Attendance = None

try:
    from app.models.payroll import Payroll
except ImportError:
    Payroll = None

try:
    from app.models.leave import Leave
except ImportError:
    Leave = None

__all__ = [
    # النماذج الأساسية المحسنة
    'BaseModel',
    'AuditMixin',
    'EncryptedMixin',
    'User',
    'Role',
    'Permission',
    'UserRole',
    'RolePermission',
    'AuditLog',

    # النماذج المحسنة الجديدة
    'Customer',
    'Invoice',
    'InvoiceItem',
    'Payment',
    'SystemSettings',

    # النماذج الموجودة (قد تكون None إذا لم تكن موجودة)
    'Supplier',
    'Product',
    'PurchaseInvoice',
    'Expense',
    'Employee',
    'Attendance',
    'Payroll',
    'Leave'
]
