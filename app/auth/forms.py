#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نماذج المصادقة
Authentication Forms
"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, HiddenField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from app.models.user_enhanced import User
from app.security.validators import validate_password_strength, validate_email_format

class LoginForm(FlaskForm):
    """نموذج تسجيل الدخول"""
    username = StringField(
        'اسم المستخدم أو البريد الإلكتروني',
        validators=[DataRequired(message='هذا الحقل مطلوب')],
        render_kw={'placeholder': 'أدخل اسم المستخدم أو البريد الإلكتروني'}
    )
    
    password = PasswordField(
        'كلمة المرور',
        validators=[DataRequired(message='هذا الحقل مطلوب')],
        render_kw={'placeholder': 'أدخل كلمة المرور'}
    )
    
    remember_me = BooleanField('تذكرني')
    
    submit = SubmitField('تسجيل الدخول')

class TwoFactorForm(FlaskForm):
    """نموذج المصادقة الثنائية"""
    token = StringField(
        'رمز المصادقة الثنائية',
        validators=[
            DataRequired(message='هذا الحقل مطلوب'),
            Length(min=6, max=6, message='الرمز يجب أن يكون 6 أرقام')
        ],
        render_kw={'placeholder': '000000', 'maxlength': '6', 'pattern': '[0-9]{6}'}
    )
    
    submit = SubmitField('تأكيد')

class RegistrationForm(FlaskForm):
    """نموذج التسجيل"""
    username = StringField(
        'اسم المستخدم',
        validators=[
            DataRequired(message='هذا الحقل مطلوب'),
            Length(min=3, max=20, message='اسم المستخدم يجب أن يكون بين 3 و 20 حرف')
        ],
        render_kw={'placeholder': 'أدخل اسم المستخدم'}
    )
    
    email = StringField(
        'البريد الإلكتروني',
        validators=[
            DataRequired(message='هذا الحقل مطلوب'),
            Email(message='البريد الإلكتروني غير صحيح')
        ],
        render_kw={'placeholder': 'أدخل البريد الإلكتروني'}
    )
    
    first_name = StringField(
        'الاسم الأول',
        validators=[
            DataRequired(message='هذا الحقل مطلوب'),
            Length(min=2, max=50, message='الاسم يجب أن يكون بين 2 و 50 حرف')
        ],
        render_kw={'placeholder': 'أدخل الاسم الأول'}
    )
    
    last_name = StringField(
        'الاسم الأخير',
        validators=[
            DataRequired(message='هذا الحقل مطلوب'),
            Length(min=2, max=50, message='الاسم يجب أن يكون بين 2 و 50 حرف')
        ],
        render_kw={'placeholder': 'أدخل الاسم الأخير'}
    )
    
    password = PasswordField(
        'كلمة المرور',
        validators=[
            DataRequired(message='هذا الحقل مطلوب'),
            Length(min=8, message='كلمة المرور يجب أن تكون 8 أحرف على الأقل')
        ],
        render_kw={'placeholder': 'أدخل كلمة المرور'}
    )
    
    password_confirm = PasswordField(
        'تأكيد كلمة المرور',
        validators=[
            DataRequired(message='هذا الحقل مطلوب'),
            EqualTo('password', message='كلمات المرور غير متطابقة')
        ],
        render_kw={'placeholder': 'أعد إدخال كلمة المرور'}
    )
    
    submit = SubmitField('إنشاء الحساب')
    
    def validate_username(self, username):
        """التحقق من عدم وجود اسم المستخدم"""
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('اسم المستخدم موجود بالفعل')
    
    def validate_email(self, email):
        """التحقق من عدم وجود البريد الإلكتروني"""
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('البريد الإلكتروني موجود بالفعل')
        
        # التحقق من صحة البريد الإلكتروني
        result = validate_email_format(email.data)
        if not result['is_valid']:
            raise ValidationError(result['error'])
    
    def validate_password(self, password):
        """التحقق من قوة كلمة المرور"""
        result = validate_password_strength(password.data)
        if not result['is_valid']:
            raise ValidationError(result['errors'][0])

class ForgotPasswordForm(FlaskForm):
    """نموذج نسيان كلمة المرور"""
    email = StringField(
        'البريد الإلكتروني',
        validators=[
            DataRequired(message='هذا الحقل مطلوب'),
            Email(message='البريد الإلكتروني غير صحيح')
        ],
        render_kw={'placeholder': 'أدخل البريد الإلكتروني'}
    )
    
    submit = SubmitField('إرسال رابط إعادة التعيين')
    
    def validate_email(self, email):
        """التحقق من وجود البريد الإلكتروني"""
        user = User.query.filter_by(email=email.data).first()
        if not user:
            raise ValidationError('البريد الإلكتروني غير موجود')

class ResetPasswordForm(FlaskForm):
    """نموذج إعادة تعيين كلمة المرور"""
    password = PasswordField(
        'كلمة المرور الجديدة',
        validators=[
            DataRequired(message='هذا الحقل مطلوب'),
            Length(min=8, message='كلمة المرور يجب أن تكون 8 أحرف على الأقل')
        ],
        render_kw={'placeholder': 'أدخل كلمة المرور الجديدة'}
    )
    
    password_confirm = PasswordField(
        'تأكيد كلمة المرور',
        validators=[
            DataRequired(message='هذا الحقل مطلوب'),
            EqualTo('password', message='كلمات المرور غير متطابقة')
        ],
        render_kw={'placeholder': 'أعد إدخال كلمة المرور'}
    )
    
    submit = SubmitField('تعيين كلمة المرور')
    
    def validate_password(self, password):
        """التحقق من قوة كلمة المرور"""
        result = validate_password_strength(password.data)
        if not result['is_valid']:
            raise ValidationError(result['errors'][0])

class ChangePasswordForm(FlaskForm):
    """نموذج تغيير كلمة المرور"""
    current_password = PasswordField(
        'كلمة المرور الحالية',
        validators=[DataRequired(message='هذا الحقل مطلوب')],
        render_kw={'placeholder': 'أدخل كلمة المرور الحالية'}
    )
    
    new_password = PasswordField(
        'كلمة المرور الجديدة',
        validators=[
            DataRequired(message='هذا الحقل مطلوب'),
            Length(min=8, message='كلمة المرور يجب أن تكون 8 أحرف على الأقل')
        ],
        render_kw={'placeholder': 'أدخل كلمة المرور الجديدة'}
    )
    
    new_password_confirm = PasswordField(
        'تأكيد كلمة المرور الجديدة',
        validators=[
            DataRequired(message='هذا الحقل مطلوب'),
            EqualTo('new_password', message='كلمات المرور غير متطابقة')
        ],
        render_kw={'placeholder': 'أعد إدخال كلمة المرور الجديدة'}
    )
    
    submit = SubmitField('تغيير كلمة المرور')
    
    def validate_new_password(self, new_password):
        """التحقق من قوة كلمة المرور الجديدة"""
        result = validate_password_strength(new_password.data)
        if not result['is_valid']:
            raise ValidationError(result['errors'][0])

class TwoFactorSetupForm(FlaskForm):
    """نموذج إعداد المصادقة الثنائية"""
    token = StringField(
        'رمز التأكيد',
        validators=[
            DataRequired(message='هذا الحقل مطلوب'),
            Length(min=6, max=6, message='الرمز يجب أن يكون 6 أرقام')
        ],
        render_kw={'placeholder': '000000', 'maxlength': '6', 'pattern': '[0-9]{6}'}
    )
    
    submit = SubmitField('تفعيل المصادقة الثنائية')

class ProfileForm(FlaskForm):
    """نموذج تحديث الملف الشخصي"""
    first_name = StringField(
        'الاسم الأول',
        validators=[
            DataRequired(message='هذا الحقل مطلوب'),
            Length(min=2, max=50, message='الاسم يجب أن يكون بين 2 و 50 حرف')
        ],
        render_kw={'placeholder': 'أدخل الاسم الأول'}
    )
    
    last_name = StringField(
        'الاسم الأخير',
        validators=[
            DataRequired(message='هذا الحقل مطلوب'),
            Length(min=2, max=50, message='الاسم يجب أن يكون بين 2 و 50 حرف')
        ],
        render_kw={'placeholder': 'أدخل الاسم الأخير'}
    )
    
    email = StringField(
        'البريد الإلكتروني',
        validators=[
            DataRequired(message='هذا الحقل مطلوب'),
            Email(message='البريد الإلكتروني غير صحيح')
        ],
        render_kw={'placeholder': 'أدخل البريد الإلكتروني'}
    )
    
    phone = StringField(
        'رقم الهاتف',
        validators=[Length(max=20, message='رقم الهاتف طويل جداً')],
        render_kw={'placeholder': 'أدخل رقم الهاتف'}
    )
    
    submit = SubmitField('حفظ التغييرات')

class UserManagementForm(FlaskForm):
    """نموذج إدارة المستخدمين"""
    username = StringField(
        'اسم المستخدم',
        validators=[
            DataRequired(message='هذا الحقل مطلوب'),
            Length(min=3, max=20, message='اسم المستخدم يجب أن يكون بين 3 و 20 حرف')
        ]
    )
    
    email = StringField(
        'البريد الإلكتروني',
        validators=[
            DataRequired(message='هذا الحقل مطلوب'),
            Email(message='البريد الإلكتروني غير صحيح')
        ]
    )
    
    first_name = StringField(
        'الاسم الأول',
        validators=[
            DataRequired(message='هذا الحقل مطلوب'),
            Length(min=2, max=50, message='الاسم يجب أن يكون بين 2 و 50 حرف')
        ]
    )
    
    last_name = StringField(
        'الاسم الأخير',
        validators=[
            DataRequired(message='هذا الحقل مطلوب'),
            Length(min=2, max=50, message='الاسم يجب أن يكون بين 2 و 50 حرف')
        ]
    )
    
    is_active = BooleanField('نشط')
    is_admin = BooleanField('مدير')
    
    submit = SubmitField('حفظ')

class RoleManagementForm(FlaskForm):
    """نموذج إدارة الأدوار"""
    name = StringField(
        'اسم الدور',
        validators=[
            DataRequired(message='هذا الحقل مطلوب'),
            Length(min=2, max=50, message='اسم الدور يجب أن يكون بين 2 و 50 حرف')
        ]
    )
    
    display_name = StringField(
        'اسم العرض',
        validators=[
            DataRequired(message='هذا الحقل مطلوب'),
            Length(min=2, max=100, message='اسم العرض يجب أن يكون بين 2 و 100 حرف')
        ]
    )
    
    description = StringField(
        'الوصف',
        validators=[Length(max=500, message='الوصف طويل جداً')]
    )
    
    color = StringField(
        'اللون',
        validators=[Length(min=7, max=7, message='اللون يجب أن يكون بتنسيق HEX')],
        render_kw={'type': 'color'}
    )
    
    is_active = BooleanField('نشط')
    
    submit = SubmitField('حفظ')
