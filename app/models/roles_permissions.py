#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نماذج الأدوار والصلاحيات
Roles and Permissions Models
"""

from datetime import datetime
from sqlalchemy import Index, event, func
from app import db
from app.models.base import BaseModel, AuditMixin

class Role(BaseModel, AuditMixin):
    """نموذج الأدوار"""
    
    __tablename__ = 'roles'
    
    # معلومات الدور
    name = db.Column(db.String(50), unique=True, nullable=False, index=True)
    display_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    
    # حالة الدور
    is_active = db.Column(db.Boolean, default=True, nullable=False, index=True)
    is_system = db.Column(db.Boolean, default=False, nullable=False)  # أدوار النظام الأساسية
    
    # ترتيب العرض
    sort_order = db.Column(db.Integer, default=0, nullable=False)
    
    # لون الدور للعرض
    color = db.Column(db.String(7), default='#007bff', nullable=False)  # HEX color
    
    # العلاقات
    users = db.relationship('UserRole', backref='role', lazy='dynamic', cascade='all, delete-orphan')
    permissions = db.relationship('RolePermission', backref='role', lazy='dynamic', cascade='all, delete-orphan')
    
    # فهارس محسنة
    __table_args__ = (
        Index('idx_role_name_active', 'name', 'is_active'),
        Index('idx_role_system_order', 'is_system', 'sort_order'),
    )
    
    def has_permission(self, permission_name):
        """فحص إذا كان الدور لديه صلاحية معينة"""
        return self.permissions.join(Permission).filter(Permission.name == permission_name).first() is not None
    
    def add_permission(self, permission):
        """إضافة صلاحية للدور"""
        if isinstance(permission, str):
            permission = Permission.query.filter_by(name=permission).first()
        
        if permission and not self.has_permission(permission.name):
            role_permission = RolePermission(role_id=self.id, permission_id=permission.id)
            db.session.add(role_permission)
            
            # تسجيل إضافة الصلاحية
            self.log_change('permission_added', {
                'role_name': self.name,
                'permission_name': permission.name
            })
    
    def remove_permission(self, permission):
        """إزالة صلاحية من الدور"""
        if isinstance(permission, str):
            permission = Permission.query.filter_by(name=permission).first()
        
        if permission:
            role_permission = self.permissions.filter_by(permission_id=permission.id).first()
            if role_permission:
                db.session.delete(role_permission)
                
                # تسجيل إزالة الصلاحية
                self.log_change('permission_removed', {
                    'role_name': self.name,
                    'permission_name': permission.name
                })
    
    def get_permissions(self):
        """الحصول على جميع صلاحيات الدور"""
        return [rp.permission for rp in self.permissions]
    
    def get_users_count(self):
        """الحصول على عدد المستخدمين في هذا الدور"""
        return self.users.count()
    
    @classmethod
    def create_default_roles(cls):
        """إنشاء الأدوار الافتراضية"""
        default_roles = [
            {
                'name': 'admin',
                'display_name': 'مدير النظام',
                'description': 'مدير النظام مع جميع الصلاحيات',
                'is_system': True,
                'sort_order': 1,
                'color': '#dc3545'
            },
            {
                'name': 'manager',
                'display_name': 'مدير',
                'description': 'مدير مع صلاحيات إدارية محدودة',
                'is_system': True,
                'sort_order': 2,
                'color': '#fd7e14'
            },
            {
                'name': 'accountant',
                'display_name': 'محاسب',
                'description': 'محاسب مع صلاحيات مالية',
                'is_system': True,
                'sort_order': 3,
                'color': '#28a745'
            },
            {
                'name': 'employee',
                'display_name': 'موظف',
                'description': 'موظف مع صلاحيات أساسية',
                'is_system': True,
                'sort_order': 4,
                'color': '#007bff'
            },
            {
                'name': 'viewer',
                'display_name': 'مشاهد',
                'description': 'مشاهد مع صلاحيات قراءة فقط',
                'is_system': True,
                'sort_order': 5,
                'color': '#6c757d'
            }
        ]
        
        for role_data in default_roles:
            existing_role = cls.query.filter_by(name=role_data['name']).first()
            if not existing_role:
                role = cls(**role_data)
                db.session.add(role)
        
        db.session.commit()
    
    def to_dict(self):
        """تحويل إلى قاموس"""
        data = super().to_dict()
        data['permissions'] = [perm.name for perm in self.get_permissions()]
        data['users_count'] = self.get_users_count()
        return data
    
    def __repr__(self):
        return f'<Role {self.name}>'

class Permission(BaseModel, AuditMixin):
    """نموذج الصلاحيات"""
    
    __tablename__ = 'permissions'
    
    # معلومات الصلاحية
    name = db.Column(db.String(100), unique=True, nullable=False, index=True)
    display_name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    
    # فئة الصلاحية
    category = db.Column(db.String(50), nullable=False, index=True)
    
    # حالة الصلاحية
    is_active = db.Column(db.Boolean, default=True, nullable=False, index=True)
    is_system = db.Column(db.Boolean, default=False, nullable=False)
    
    # ترتيب العرض
    sort_order = db.Column(db.Integer, default=0, nullable=False)
    
    # العلاقات
    roles = db.relationship('RolePermission', backref='permission', lazy='dynamic', cascade='all, delete-orphan')
    
    # فهارس محسنة
    __table_args__ = (
        Index('idx_permission_name_active', 'name', 'is_active'),
        Index('idx_permission_category_order', 'category', 'sort_order'),
    )
    
    # فئات الصلاحيات
    CATEGORIES = {
        'users': 'إدارة المستخدمين',
        'customers': 'إدارة العملاء',
        'suppliers': 'إدارة الموردين',
        'products': 'إدارة المنتجات',
        'invoices': 'إدارة الفواتير',
        'payments': 'إدارة المدفوعات',
        'reports': 'التقارير',
        'settings': 'الإعدادات',
        'system': 'إدارة النظام'
    }
    
    @classmethod
    def create_default_permissions(cls):
        """إنشاء الصلاحيات الافتراضية"""
        default_permissions = [
            # إدارة المستخدمين
            ('users.view', 'عرض المستخدمين', 'users', 'عرض قائمة المستخدمين', 1),
            ('users.create', 'إنشاء مستخدم', 'users', 'إنشاء مستخدم جديد', 2),
            ('users.edit', 'تعديل مستخدم', 'users', 'تعديل بيانات المستخدم', 3),
            ('users.delete', 'حذف مستخدم', 'users', 'حذف مستخدم', 4),
            ('users.manage_roles', 'إدارة أدوار المستخدمين', 'users', 'تعيين وإزالة الأدوار', 5),
            
            # إدارة العملاء
            ('customers.view', 'عرض العملاء', 'customers', 'عرض قائمة العملاء', 1),
            ('customers.create', 'إنشاء عميل', 'customers', 'إنشاء عميل جديد', 2),
            ('customers.edit', 'تعديل عميل', 'customers', 'تعديل بيانات العميل', 3),
            ('customers.delete', 'حذف عميل', 'customers', 'حذف عميل', 4),
            
            # إدارة الموردين
            ('suppliers.view', 'عرض الموردين', 'suppliers', 'عرض قائمة الموردين', 1),
            ('suppliers.create', 'إنشاء مورد', 'suppliers', 'إنشاء مورد جديد', 2),
            ('suppliers.edit', 'تعديل مورد', 'suppliers', 'تعديل بيانات المورد', 3),
            ('suppliers.delete', 'حذف مورد', 'suppliers', 'حذف مورد', 4),
            
            # إدارة المنتجات
            ('products.view', 'عرض المنتجات', 'products', 'عرض قائمة المنتجات', 1),
            ('products.create', 'إنشاء منتج', 'products', 'إنشاء منتج جديد', 2),
            ('products.edit', 'تعديل منتج', 'products', 'تعديل بيانات المنتج', 3),
            ('products.delete', 'حذف منتج', 'products', 'حذف منتج', 4),
            ('products.manage_inventory', 'إدارة المخزون', 'products', 'إدارة كميات المخزون', 5),
            
            # إدارة الفواتير
            ('invoices.view', 'عرض الفواتير', 'invoices', 'عرض قائمة الفواتير', 1),
            ('invoices.create', 'إنشاء فاتورة', 'invoices', 'إنشاء فاتورة جديدة', 2),
            ('invoices.edit', 'تعديل فاتورة', 'invoices', 'تعديل بيانات الفاتورة', 3),
            ('invoices.delete', 'حذف فاتورة', 'invoices', 'حذف فاتورة', 4),
            ('invoices.approve', 'اعتماد فاتورة', 'invoices', 'اعتماد الفواتير', 5),
            ('invoices.print', 'طباعة فاتورة', 'invoices', 'طباعة الفواتير', 6),
            
            # إدارة المدفوعات
            ('payments.view', 'عرض المدفوعات', 'payments', 'عرض قائمة المدفوعات', 1),
            ('payments.create', 'إنشاء دفعة', 'payments', 'إنشاء دفعة جديدة', 2),
            ('payments.edit', 'تعديل دفعة', 'payments', 'تعديل بيانات الدفعة', 3),
            ('payments.delete', 'حذف دفعة', 'payments', 'حذف دفعة', 4),
            ('payments.verify', 'التحقق من الدفعات', 'payments', 'التحقق من صحة الدفعات', 5),
            
            # التقارير
            ('reports.view', 'عرض التقارير', 'reports', 'عرض التقارير المالية', 1),
            ('reports.export', 'تصدير التقارير', 'reports', 'تصدير التقارير', 2),
            ('reports.advanced', 'التقارير المتقدمة', 'reports', 'الوصول للتقارير المتقدمة', 3),
            
            # الإعدادات
            ('settings.view', 'عرض الإعدادات', 'settings', 'عرض إعدادات النظام', 1),
            ('settings.edit', 'تعديل الإعدادات', 'settings', 'تعديل إعدادات النظام', 2),
            ('settings.backup', 'النسخ الاحتياطي', 'settings', 'إنشاء واستعادة النسخ الاحتياطية', 3),
            
            # إدارة النظام
            ('system.admin', 'إدارة النظام', 'system', 'إدارة كاملة للنظام', 1),
            ('system.audit', 'سجلات المراجعة', 'system', 'عرض سجلات المراجعة', 2),
            ('system.maintenance', 'صيانة النظام', 'system', 'صيانة وتحديث النظام', 3),
        ]
        
        for name, display_name, category, description, sort_order in default_permissions:
            existing_permission = cls.query.filter_by(name=name).first()
            if not existing_permission:
                permission = cls(
                    name=name,
                    display_name=display_name,
                    category=category,
                    description=description,
                    sort_order=sort_order,
                    is_system=True
                )
                db.session.add(permission)
        
        db.session.commit()
    
    def get_category_display(self):
        """الحصول على اسم الفئة للعرض"""
        return self.CATEGORIES.get(self.category, self.category)
    
    def to_dict(self):
        """تحويل إلى قاموس"""
        data = super().to_dict()
        data['category_display'] = self.get_category_display()
        return data
    
    def __repr__(self):
        return f'<Permission {self.name}>'

class UserRole(BaseModel, AuditMixin):
    """جدول ربط المستخدمين بالأدوار"""
    
    __tablename__ = 'user_roles'
    
    # المفاتيح الخارجية
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False, index=True)
    
    # معلومات التعيين
    assigned_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=True)  # انتهاء صلاحية الدور
    
    # حالة التعيين
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # العلاقات
    assigned_by = db.relationship('User', foreign_keys=[assigned_by_id], lazy='select')
    
    # فهارس محسنة
    __table_args__ = (
        Index('idx_user_role_user_role', 'user_id', 'role_id'),
        Index('idx_user_role_active_expires', 'is_active', 'expires_at'),
        db.UniqueConstraint('user_id', 'role_id', name='uq_user_role'),
    )
    
    def is_expired(self):
        """فحص إذا كان الدور منتهي الصلاحية"""
        if self.expires_at:
            return datetime.utcnow() > self.expires_at
        return False
    
    def __repr__(self):
        return f'<UserRole user_id={self.user_id} role_id={self.role_id}>'

class RolePermission(BaseModel, AuditMixin):
    """جدول ربط الأدوار بالصلاحيات"""
    
    __tablename__ = 'role_permissions'
    
    # المفاتيح الخارجية
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False, index=True)
    permission_id = db.Column(db.Integer, db.ForeignKey('permissions.id'), nullable=False, index=True)
    
    # معلومات التعيين
    assigned_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # حالة التعيين
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # العلاقات
    assigned_by = db.relationship('User', foreign_keys=[assigned_by_id], lazy='select')
    
    # فهارس محسنة
    __table_args__ = (
        Index('idx_role_permission_role_perm', 'role_id', 'permission_id'),
        Index('idx_role_permission_active', 'is_active'),
        db.UniqueConstraint('role_id', 'permission_id', name='uq_role_permission'),
    )
    
    def __repr__(self):
        return f'<RolePermission role_id={self.role_id} permission_id={self.permission_id}>'

class LoginHistory(BaseModel):
    """سجل تسجيل الدخول"""
    
    __tablename__ = 'login_history'
    
    # معلومات المستخدم
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    # معلومات تسجيل الدخول
    login_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    ip_address = db.Column(db.String(45), nullable=True)  # IPv6 support
    user_agent = db.Column(db.Text, nullable=True)
    
    # نتيجة تسجيل الدخول
    success = db.Column(db.Boolean, nullable=False, index=True)
    failure_reason = db.Column(db.String(100), nullable=True)
    
    # معلومات الجلسة
    session_id = db.Column(db.String(100), nullable=True)
    logout_at = db.Column(db.DateTime, nullable=True)
    
    # معلومات إضافية
    location = db.Column(db.String(100), nullable=True)  # الموقع الجغرافي
    device_type = db.Column(db.String(50), nullable=True)  # نوع الجهاز
    
    # فهارس محسنة
    __table_args__ = (
        Index('idx_login_history_user_date', 'user_id', 'login_at'),
        Index('idx_login_history_success_date', 'success', 'login_at'),
        Index('idx_login_history_ip', 'ip_address'),
    )
    
    def __repr__(self):
        return f'<LoginHistory user_id={self.user_id} at={self.login_at}>'

# الأحداث التلقائية
@event.listens_for(UserRole, 'after_insert')
def log_user_role_assignment(mapper, connection, target):
    """تسجيل تعيين دور للمستخدم"""
    target.log_change('role_assigned', {
        'user_id': target.user_id,
        'role_id': target.role_id,
        'assigned_by': target.assigned_by_id
    })

@event.listens_for(UserRole, 'after_delete')
def log_user_role_removal(mapper, connection, target):
    """تسجيل إزالة دور من المستخدم"""
    target.log_change('role_removed', {
        'user_id': target.user_id,
        'role_id': target.role_id
    })

@event.listens_for(RolePermission, 'after_insert')
def log_role_permission_assignment(mapper, connection, target):
    """تسجيل تعيين صلاحية للدور"""
    target.log_change('permission_assigned', {
        'role_id': target.role_id,
        'permission_id': target.permission_id,
        'assigned_by': target.assigned_by_id
    })

@event.listens_for(RolePermission, 'after_delete')
def log_role_permission_removal(mapper, connection, target):
    """تسجيل إزالة صلاحية من الدور"""
    target.log_change('permission_removed', {
        'role_id': target.role_id,
        'permission_id': target.permission_id
    })
