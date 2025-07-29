#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
مسارات الإدارة
Administration Routes
"""

from flask import render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
from app import db
from app.admin import admin_bp
from app.auth.forms import UserManagementForm, RoleManagementForm
from app.models.user_enhanced import User
from app.models.roles_permissions import Role, Permission, UserRole, RolePermission, LoginHistory
from app.security.decorators import permission_required
from app.security.validators import sanitize_input
from datetime import datetime, timedelta

@admin_bp.before_request
@login_required
def require_admin():
    """التأكد من أن المستخدم مدير"""
    if not current_user.has_permission('system.admin') and not current_user.is_admin:
        flash('ليس لديك صلاحية للوصول إلى لوحة الإدارة.', 'error')
        return redirect(url_for('main.index'))

@admin_bp.route('/')
@permission_required('system.admin')
def dashboard():
    """لوحة تحكم الإدارة"""
    # إحصائيات عامة
    stats = {
        'total_users': User.query.count(),
        'active_users': User.query.filter_by(is_active=True).count(),
        'total_roles': Role.query.count(),
        'total_permissions': Permission.query.count(),
        'recent_logins': LoginHistory.query.filter(
            LoginHistory.login_at > datetime.utcnow() - timedelta(days=7)
        ).count()
    }
    
    # المستخدمين الجدد (آخر 30 يوم)
    new_users = User.query.filter(
        User.created_at > datetime.utcnow() - timedelta(days=30)
    ).order_by(User.created_at.desc()).limit(10).all()
    
    # آخر عمليات تسجيل الدخول
    recent_logins = LoginHistory.query.filter_by(success=True)\
        .order_by(LoginHistory.login_at.desc()).limit(10).all()
    
    # محاولات الدخول الفاشلة
    failed_logins = LoginHistory.query.filter_by(success=False)\
        .filter(LoginHistory.login_at > datetime.utcnow() - timedelta(days=1))\
        .count()
    
    return render_template('admin/dashboard.html',
                         stats=stats,
                         new_users=new_users,
                         recent_logins=recent_logins,
                         failed_logins=failed_logins)

@admin_bp.route('/users')
@permission_required('users.view')
def users():
    """إدارة المستخدمين"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # فلترة المستخدمين
    query = User.query
    
    # البحث
    search = request.args.get('search', '').strip()
    if search:
        query = query.filter(
            (User.username.contains(search)) |
            (User.email.contains(search)) |
            (User.first_name.contains(search)) |
            (User.last_name.contains(search))
        )
    
    # فلترة حسب الحالة
    status = request.args.get('status')
    if status == 'active':
        query = query.filter_by(is_active=True)
    elif status == 'inactive':
        query = query.filter_by(is_active=False)
    elif status == 'admin':
        query = query.filter_by(is_admin=True)
    
    # فلترة حسب الدور
    role_id = request.args.get('role', type=int)
    if role_id:
        query = query.join(UserRole).filter(UserRole.role_id == role_id)
    
    users_pagination = query.order_by(User.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    # الأدوار للفلترة
    roles = Role.query.filter_by(is_active=True).all()
    
    return render_template('admin/users.html',
                         users=users_pagination,
                         roles=roles,
                         search=search,
                         status=status,
                         role_id=role_id)

@admin_bp.route('/users/create', methods=['GET', 'POST'])
@permission_required('users.create')
def create_user():
    """إنشاء مستخدم جديد"""
    form = UserManagementForm()
    
    if form.validate_on_submit():
        # فحص عدم وجود اسم المستخدم أو البريد الإلكتروني
        existing_user = User.query.filter(
            (User.username == form.username.data) |
            (User.email == form.email.data)
        ).first()
        
        if existing_user:
            flash('اسم المستخدم أو البريد الإلكتروني موجود بالفعل.', 'error')
            return render_template('admin/create_user.html', form=form)
        
        # إنشاء المستخدم
        user = User(
            username=sanitize_input(form.username.data),
            email=sanitize_input(form.email.data.lower()),
            first_name=sanitize_input(form.first_name.data),
            last_name=sanitize_input(form.last_name.data),
            is_active=form.is_active.data,
            is_admin=form.is_admin.data
        )
        
        # تعيين كلمة مرور افتراضية
        user.set_password('temp123456')
        
        db.session.add(user)
        db.session.commit()
        
        # تعيين دور افتراضي
        default_role = Role.query.filter_by(name='viewer').first()
        if default_role:
            user_role = UserRole(user_id=user.id, role_id=default_role.id)
            db.session.add(user_role)
            db.session.commit()
        
        flash(f'تم إنشاء المستخدم {user.username} بنجاح. كلمة المرور المؤقتة: temp123456', 'success')
        return redirect(url_for('admin.users'))
    
    return render_template('admin/create_user.html', form=form)

@admin_bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@permission_required('users.edit')
def edit_user(user_id):
    """تعديل مستخدم"""
    user = User.query.get_or_404(user_id)
    form = UserManagementForm()
    
    if form.validate_on_submit():
        # فحص عدم تضارب اسم المستخدم أو البريد الإلكتروني
        existing_user = User.query.filter(
            ((User.username == form.username.data) |
             (User.email == form.email.data)) &
            (User.id != user_id)
        ).first()
        
        if existing_user:
            flash('اسم المستخدم أو البريد الإلكتروني موجود بالفعل.', 'error')
            return render_template('admin/edit_user.html', form=form, user=user)
        
        # تحديث البيانات
        user.username = sanitize_input(form.username.data)
        user.email = sanitize_input(form.email.data.lower())
        user.first_name = sanitize_input(form.first_name.data)
        user.last_name = sanitize_input(form.last_name.data)
        user.is_active = form.is_active.data
        user.is_admin = form.is_admin.data
        
        db.session.commit()
        flash(f'تم تحديث المستخدم {user.username} بنجاح.', 'success')
        return redirect(url_for('admin.users'))
    
    # ملء النموذج بالبيانات الحالية
    form.username.data = user.username
    form.email.data = user.email
    form.first_name.data = user.first_name
    form.last_name.data = user.last_name
    form.is_active.data = user.is_active
    form.is_admin.data = user.is_admin
    
    return render_template('admin/edit_user.html', form=form, user=user)

@admin_bp.route('/users/<int:user_id>/roles', methods=['GET', 'POST'])
@permission_required('users.manage_roles')
def manage_user_roles(user_id):
    """إدارة أدوار المستخدم"""
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        role_ids = request.form.getlist('roles')
        
        # حذف الأدوار الحالية
        UserRole.query.filter_by(user_id=user_id).delete()
        
        # إضافة الأدوار الجديدة
        for role_id in role_ids:
            user_role = UserRole(
                user_id=user_id,
                role_id=int(role_id),
                assigned_by_id=current_user.id
            )
            db.session.add(user_role)
        
        db.session.commit()
        flash(f'تم تحديث أدوار المستخدم {user.username} بنجاح.', 'success')
        return redirect(url_for('admin.users'))
    
    # الأدوار المتاحة
    available_roles = Role.query.filter_by(is_active=True).all()
    
    # الأدوار الحالية للمستخدم
    current_roles = [ur.role_id for ur in user.roles]
    
    return render_template('admin/manage_user_roles.html',
                         user=user,
                         available_roles=available_roles,
                         current_roles=current_roles)

@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@permission_required('users.delete')
def delete_user(user_id):
    """حذف مستخدم"""
    user = User.query.get_or_404(user_id)
    
    # منع حذف المدير الحالي
    if user.id == current_user.id:
        flash('لا يمكنك حذف حسابك الخاص.', 'error')
        return redirect(url_for('admin.users'))
    
    # منع حذف المدير الوحيد
    if user.is_admin:
        admin_count = User.query.filter_by(is_admin=True, is_active=True).count()
        if admin_count <= 1:
            flash('لا يمكن حذف المدير الوحيد في النظام.', 'error')
            return redirect(url_for('admin.users'))
    
    username = user.username
    db.session.delete(user)
    db.session.commit()
    
    flash(f'تم حذف المستخدم {username} بنجاح.', 'success')
    return redirect(url_for('admin.users'))

@admin_bp.route('/roles')
@permission_required('system.admin')
def roles():
    """إدارة الأدوار"""
    roles_list = Role.query.order_by(Role.sort_order, Role.name).all()
    return render_template('admin/roles.html', roles=roles_list)

@admin_bp.route('/roles/create', methods=['GET', 'POST'])
@permission_required('system.admin')
def create_role():
    """إنشاء دور جديد"""
    form = RoleManagementForm()
    
    if form.validate_on_submit():
        # فحص عدم وجود الدور
        existing_role = Role.query.filter_by(name=form.name.data).first()
        if existing_role:
            flash('اسم الدور موجود بالفعل.', 'error')
            return render_template('admin/create_role.html', form=form)
        
        # إنشاء الدور
        role = Role(
            name=sanitize_input(form.name.data),
            display_name=sanitize_input(form.display_name.data),
            description=sanitize_input(form.description.data),
            color=form.color.data,
            is_active=form.is_active.data
        )
        
        db.session.add(role)
        db.session.commit()
        
        flash(f'تم إنشاء الدور {role.display_name} بنجاح.', 'success')
        return redirect(url_for('admin.roles'))
    
    return render_template('admin/create_role.html', form=form)

@admin_bp.route('/roles/<int:role_id>/permissions', methods=['GET', 'POST'])
@permission_required('system.admin')
def manage_role_permissions(role_id):
    """إدارة صلاحيات الدور"""
    role = Role.query.get_or_404(role_id)
    
    if request.method == 'POST':
        permission_ids = request.form.getlist('permissions')
        
        # حذف الصلاحيات الحالية
        RolePermission.query.filter_by(role_id=role_id).delete()
        
        # إضافة الصلاحيات الجديدة
        for permission_id in permission_ids:
            role_permission = RolePermission(
                role_id=role_id,
                permission_id=int(permission_id),
                assigned_by_id=current_user.id
            )
            db.session.add(role_permission)
        
        db.session.commit()
        flash(f'تم تحديث صلاحيات الدور {role.display_name} بنجاح.', 'success')
        return redirect(url_for('admin.roles'))
    
    # الصلاحيات المتاحة مجمعة حسب الفئة
    permissions_by_category = {}
    all_permissions = Permission.query.filter_by(is_active=True)\
        .order_by(Permission.category, Permission.sort_order).all()
    
    for permission in all_permissions:
        category = permission.category
        if category not in permissions_by_category:
            permissions_by_category[category] = {
                'name': permission.get_category_display(),
                'permissions': []
            }
        permissions_by_category[category]['permissions'].append(permission)
    
    # الصلاحيات الحالية للدور
    current_permissions = [rp.permission_id for rp in role.permissions]
    
    return render_template('admin/manage_role_permissions.html',
                         role=role,
                         permissions_by_category=permissions_by_category,
                         current_permissions=current_permissions)

@admin_bp.route('/permissions')
@permission_required('system.admin')
def permissions():
    """عرض الصلاحيات"""
    # الصلاحيات مجمعة حسب الفئة
    permissions_by_category = {}
    all_permissions = Permission.query.order_by(Permission.category, Permission.sort_order).all()
    
    for permission in all_permissions:
        category = permission.category
        if category not in permissions_by_category:
            permissions_by_category[category] = {
                'name': permission.get_category_display(),
                'permissions': []
            }
        permissions_by_category[category]['permissions'].append(permission)
    
    return render_template('admin/permissions.html',
                         permissions_by_category=permissions_by_category)

@admin_bp.route('/login-history')
@permission_required('system.audit')
def login_history():
    """سجل تسجيل الدخول"""
    page = request.args.get('page', 1, type=int)
    per_page = 50
    
    # فلترة السجلات
    query = LoginHistory.query
    
    # فلترة حسب المستخدم
    user_id = request.args.get('user_id', type=int)
    if user_id:
        query = query.filter_by(user_id=user_id)
    
    # فلترة حسب النجاح/الفشل
    success = request.args.get('success')
    if success == 'true':
        query = query.filter_by(success=True)
    elif success == 'false':
        query = query.filter_by(success=False)
    
    # فلترة حسب التاريخ
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    
    if date_from:
        try:
            date_from = datetime.strptime(date_from, '%Y-%m-%d')
            query = query.filter(LoginHistory.login_at >= date_from)
        except ValueError:
            pass
    
    if date_to:
        try:
            date_to = datetime.strptime(date_to, '%Y-%m-%d')
            query = query.filter(LoginHistory.login_at <= date_to)
        except ValueError:
            pass
    
    history_pagination = query.order_by(LoginHistory.login_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('admin/login_history.html',
                         history=history_pagination,
                         user_id=user_id,
                         success=success,
                         date_from=date_from,
                         date_to=date_to)

# API Routes
@admin_bp.route('/api/users/<int:user_id>/toggle-status', methods=['POST'])
@permission_required('users.edit')
def api_toggle_user_status(user_id):
    """تبديل حالة المستخدم"""
    user = User.query.get_or_404(user_id)
    
    # منع إلغاء تفعيل المدير الحالي
    if user.id == current_user.id and user.is_active:
        return jsonify({'success': False, 'message': 'لا يمكنك إلغاء تفعيل حسابك الخاص'})
    
    user.is_active = not user.is_active
    db.session.commit()
    
    status = 'مفعل' if user.is_active else 'معطل'
    return jsonify({
        'success': True,
        'message': f'تم {status} المستخدم {user.username}',
        'is_active': user.is_active
    })

@admin_bp.route('/api/users/<int:user_id>/reset-password', methods=['POST'])
@permission_required('users.edit')
def api_reset_user_password(user_id):
    """إعادة تعيين كلمة مرور المستخدم"""
    user = User.query.get_or_404(user_id)
    
    # إنشاء كلمة مرور مؤقتة
    temp_password = 'temp' + secrets.token_hex(4)
    user.set_password(temp_password)
    
    # إلغاء جميع الجلسات
    user.invalidate_session()
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': f'تم إعادة تعيين كلمة مرور المستخدم {user.username}',
        'temp_password': temp_password
    })

@admin_bp.route('/api/stats')
@permission_required('system.admin')
def api_stats():
    """إحصائيات النظام"""
    stats = {
        'users': {
            'total': User.query.count(),
            'active': User.query.filter_by(is_active=True).count(),
            'inactive': User.query.filter_by(is_active=False).count(),
            'admins': User.query.filter_by(is_admin=True).count()
        },
        'logins': {
            'today': LoginHistory.query.filter(
                LoginHistory.login_at > datetime.utcnow().replace(hour=0, minute=0, second=0)
            ).count(),
            'week': LoginHistory.query.filter(
                LoginHistory.login_at > datetime.utcnow() - timedelta(days=7)
            ).count(),
            'failed_today': LoginHistory.query.filter(
                LoginHistory.login_at > datetime.utcnow().replace(hour=0, minute=0, second=0),
                LoginHistory.success == False
            ).count()
        }
    }
    
    return jsonify(stats)
