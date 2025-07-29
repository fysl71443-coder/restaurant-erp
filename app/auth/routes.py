#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
مسارات المصادقة
Authentication Routes
"""

from flask import render_template, redirect, url_for, flash, request, session, jsonify, current_app
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.auth import auth_bp
from app.auth.forms import *
from app.auth.utils import *
from app.models.user_enhanced import User
from app.models.roles_permissions import Role, Permission, UserRole, LoginHistory
from app.security.decorators import permission_required, rate_limit
from app.security.validators import sanitize_input
import secrets

@auth_bp.route('/login', methods=['GET', 'POST'])
@rate_limit(max_requests=10, window=300)  # 10 محاولات كل 5 دقائق
def login():
    """تسجيل الدخول"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        # تنظيف المدخلات
        username = sanitize_input(form.username.data)
        password = form.password.data
        
        # البحث عن المستخدم
        user = User.query.filter(
            (User.username == username) | (User.email == username)
        ).first()
        
        # الحصول على عنوان IP
        ip_address = get_client_ip()
        
        if user and user.check_password(password):
            # فحص إذا كان الحساب مقفل
            if user.is_locked():
                flash('الحساب مقفل مؤقتاً. يرجى المحاولة لاحقاً.', 'error')
                user.record_login_attempt(success=False, ip_address=ip_address)
                return render_template('auth/login.html', form=form)
            
            # فحص إذا كان الحساب نشط
            if not user.is_active:
                flash('الحساب غير نشط. يرجى التواصل مع المدير.', 'error')
                user.record_login_attempt(success=False, ip_address=ip_address)
                return render_template('auth/login.html', form=form)
            
            # تسجيل محاولة دخول ناجحة
            user.record_login_attempt(success=True, ip_address=ip_address)
            
            # فحص المصادقة الثنائية
            if user.two_factor_enabled:
                session['pending_user_id'] = user.id
                session['pending_remember'] = form.remember_me.data
                return redirect(url_for('auth.two_factor'))
            
            # تسجيل الدخول
            login_user(user, remember=form.remember_me.data)
            
            # إنشاء سجل دخول
            create_login_history(user, ip_address, success=True)
            
            flash(f'مرحباً {user.display_name}!', 'success')
            
            # إعادة التوجيه للصفحة المطلوبة
            next_page = request.args.get('next')
            if next_page and is_safe_url(next_page):
                return redirect(next_page)
            
            return redirect(url_for('main.index'))
        
        else:
            # تسجيل محاولة دخول فاشلة
            if user:
                user.record_login_attempt(success=False, ip_address=ip_address)
                create_login_history(user, ip_address, success=False, failure_reason='wrong_password')
            else:
                create_login_history(None, ip_address, success=False, failure_reason='user_not_found')
            
            flash('اسم المستخدم أو كلمة المرور غير صحيحة.', 'error')
    
    return render_template('auth/login.html', form=form)

@auth_bp.route('/two-factor', methods=['GET', 'POST'])
@rate_limit(max_requests=5, window=300)  # 5 محاولات كل 5 دقائق
def two_factor():
    """المصادقة الثنائية"""
    if 'pending_user_id' not in session:
        return redirect(url_for('auth.login'))
    
    user = User.query.get(session['pending_user_id'])
    if not user or not user.two_factor_enabled:
        session.pop('pending_user_id', None)
        return redirect(url_for('auth.login'))
    
    form = TwoFactorForm()
    
    if form.validate_on_submit():
        token = form.token.data
        
        if user.verify_two_factor_token(token):
            # تسجيل الدخول
            remember = session.pop('pending_remember', False)
            session.pop('pending_user_id', None)
            
            login_user(user, remember=remember)
            
            # تحديث سجل الدخول
            ip_address = get_client_ip()
            create_login_history(user, ip_address, success=True)
            
            flash(f'مرحباً {user.display_name}!', 'success')
            
            # إعادة التوجيه
            next_page = request.args.get('next')
            if next_page and is_safe_url(next_page):
                return redirect(next_page)
            
            return redirect(url_for('main.index'))
        
        else:
            flash('رمز المصادقة الثنائية غير صحيح.', 'error')
    
    return render_template('auth/two_factor.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    """تسجيل الخروج"""
    if current_user.is_authenticated:
        # تحديث سجل الدخول
        update_logout_time(current_user)
        
        # إلغاء الجلسة
        current_user.invalidate_session()
        
        flash('تم تسجيل الخروج بنجاح.', 'info')
    
    logout_user()
    return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """التسجيل"""
    # فحص إذا كان التسجيل مفعل
    if not current_app.config.get('REGISTRATION_ENABLED', True):
        flash('التسجيل غير متاح حالياً.', 'error')
        return redirect(url_for('auth.login'))
    
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegistrationForm()
    
    if form.validate_on_submit():
        # إنشاء مستخدم جديد
        user = User(
            username=sanitize_input(form.username.data),
            email=sanitize_input(form.email.data.lower()),
            first_name=sanitize_input(form.first_name.data),
            last_name=sanitize_input(form.last_name.data)
        )
        user.set_password(form.password.data)
        
        # إنشاء رمز تأكيد البريد الإلكتروني
        verification_token = user.generate_email_verification_token()
        
        db.session.add(user)
        db.session.commit()
        
        # تعيين دور افتراضي
        default_role = Role.query.filter_by(name='viewer').first()
        if default_role:
            user_role = UserRole(user_id=user.id, role_id=default_role.id)
            db.session.add(user_role)
            db.session.commit()
        
        # إرسال بريد تأكيد (سيتم تطبيقه لاحقاً)
        # send_verification_email(user, verification_token)
        
        flash('تم إنشاء الحساب بنجاح! يرجى تأكيد البريد الإلكتروني.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', form=form)

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
@rate_limit(max_requests=3, window=300)  # 3 محاولات كل 5 دقائق
def forgot_password():
    """نسيان كلمة المرور"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = ForgotPasswordForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        
        if user:
            # إنشاء رمز إعادة التعيين
            reset_token = user.generate_reset_token()
            
            # إرسال بريد إعادة التعيين (سيتم تطبيقه لاحقاً)
            # send_reset_email(user, reset_token)
            
            flash('تم إرسال رابط إعادة تعيين كلمة المرور إلى بريدك الإلكتروني.', 'info')
        else:
            flash('البريد الإلكتروني غير موجود.', 'error')
        
        return redirect(url_for('auth.login'))
    
    return render_template('auth/forgot_password.html', form=form)

@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """إعادة تعيين كلمة المرور"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    user = User.query.filter_by(reset_token=token).first()
    
    if not user or not user.verify_reset_token(token):
        flash('رابط إعادة التعيين غير صحيح أو منتهي الصلاحية.', 'error')
        return redirect(url_for('auth.forgot_password'))
    
    form = ResetPasswordForm()
    
    if form.validate_on_submit():
        user.reset_password(form.password.data)
        flash('تم تعيين كلمة المرور الجديدة بنجاح.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password.html', form=form)

@auth_bp.route('/verify-email/<token>')
def verify_email(token):
    """تأكيد البريد الإلكتروني"""
    user = User.query.filter_by(email_verification_token=token).first()
    
    if not user:
        flash('رابط التأكيد غير صحيح.', 'error')
        return redirect(url_for('auth.login'))
    
    if user.verify_email(token):
        flash('تم تأكيد البريد الإلكتروني بنجاح.', 'success')
    else:
        flash('رابط التأكيد غير صحيح.', 'error')
    
    return redirect(url_for('auth.login'))

@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """الملف الشخصي"""
    form = ProfileForm()
    
    if form.validate_on_submit():
        current_user.first_name = sanitize_input(form.first_name.data)
        current_user.last_name = sanitize_input(form.last_name.data)
        current_user.email = sanitize_input(form.email.data.lower())
        current_user.phone = sanitize_input(form.phone.data) if form.phone.data else None
        
        db.session.commit()
        flash('تم تحديث الملف الشخصي بنجاح.', 'success')
        return redirect(url_for('auth.profile'))
    
    # ملء النموذج بالبيانات الحالية
    form.first_name.data = current_user.first_name
    form.last_name.data = current_user.last_name
    form.email.data = current_user.email
    form.phone.data = current_user.phone
    
    return render_template('auth/profile.html', form=form)

@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """تغيير كلمة المرور"""
    form = ChangePasswordForm()
    
    if form.validate_on_submit():
        if current_user.check_password(form.current_password.data):
            current_user.set_password(form.new_password.data)
            db.session.commit()
            
            flash('تم تغيير كلمة المرور بنجاح.', 'success')
            return redirect(url_for('auth.profile'))
        else:
            flash('كلمة المرور الحالية غير صحيحة.', 'error')
    
    return render_template('auth/change_password.html', form=form)

@auth_bp.route('/setup-2fa', methods=['GET', 'POST'])
@login_required
def setup_two_factor():
    """إعداد المصادقة الثنائية"""
    if current_user.two_factor_enabled:
        flash('المصادقة الثنائية مفعلة بالفعل.', 'info')
        return redirect(url_for('auth.profile'))
    
    # إعداد المصادقة الثنائية
    secret, backup_codes = current_user.setup_two_factor()
    qr_code = current_user.get_two_factor_qr_code()
    
    form = TwoFactorSetupForm()
    
    if form.validate_on_submit():
        if current_user.verify_two_factor_token(form.token.data):
            current_user.enable_two_factor()
            flash('تم تفعيل المصادقة الثنائية بنجاح.', 'success')
            return redirect(url_for('auth.profile'))
        else:
            flash('رمز التأكيد غير صحيح.', 'error')
    
    return render_template('auth/setup_2fa.html', 
                         form=form, 
                         qr_code=qr_code, 
                         backup_codes=backup_codes)

@auth_bp.route('/disable-2fa', methods=['POST'])
@login_required
def disable_two_factor():
    """إلغاء تفعيل المصادقة الثنائية"""
    if current_user.two_factor_enabled:
        current_user.disable_two_factor()
        flash('تم إلغاء تفعيل المصادقة الثنائية.', 'info')
    
    return redirect(url_for('auth.profile'))

@auth_bp.route('/login-history')
@login_required
def login_history():
    """سجل تسجيل الدخول"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    history = LoginHistory.query.filter_by(user_id=current_user.id)\
        .order_by(LoginHistory.login_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('auth/login_history.html', history=history)

# API Routes
@auth_bp.route('/api/check-username')
def api_check_username():
    """فحص توفر اسم المستخدم"""
    username = request.args.get('username', '').strip()
    
    if not username:
        return jsonify({'available': False, 'message': 'اسم المستخدم مطلوب'})
    
    user = User.query.filter_by(username=username).first()
    
    return jsonify({
        'available': user is None,
        'message': 'اسم المستخدم متاح' if user is None else 'اسم المستخدم موجود بالفعل'
    })

@auth_bp.route('/api/check-email')
def api_check_email():
    """فحص توفر البريد الإلكتروني"""
    email = request.args.get('email', '').strip().lower()
    
    if not email:
        return jsonify({'available': False, 'message': 'البريد الإلكتروني مطلوب'})
    
    user = User.query.filter_by(email=email).first()
    
    return jsonify({
        'available': user is None,
        'message': 'البريد الإلكتروني متاح' if user is None else 'البريد الإلكتروني موجود بالفعل'
    })

@auth_bp.route('/api/password-strength')
def api_password_strength():
    """فحص قوة كلمة المرور"""
    password = request.args.get('password', '')
    
    if not password:
        return jsonify({'strength': 0, 'message': 'كلمة المرور مطلوبة'})
    
    from app.security.validators import validate_password_strength
    result = validate_password_strength(password)
    
    return jsonify({
        'strength': result['strength_score'],
        'valid': result['is_valid'],
        'errors': result['errors']
    })
