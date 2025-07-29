#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نظام معالجة النماذج المحسن
Enhanced Form Processing System
"""

from flask import request, jsonify, flash
from functools import wraps
import logging
from datetime import datetime
import re
from decimal import Decimal, InvalidOperation

# إعداد نظام التسجيل
form_logger = logging.getLogger('form_processing')
form_logger.setLevel(logging.INFO)

class ValidationError(Exception):
    """خطأ في التحقق من البيانات"""
    def __init__(self, field, message):
        self.field = field
        self.message = message
        super().__init__(f"{field}: {message}")

class FormProcessor:
    """معالج النماذج المحسن"""
    
    def __init__(self):
        self.errors = {}
        self.cleaned_data = {}
        self.is_valid = True
    
    def validate_required(self, field_name, value, custom_message=None):
        """التحقق من الحقول المطلوبة"""
        if not value or str(value).strip() == '':
            message = custom_message or f"حقل {field_name} مطلوب"
            self.add_error(field_name, message)
            return False
        return True
    
    def validate_email(self, field_name, value, required=True):
        """التحقق من البريد الإلكتروني"""
        if not value and not required:
            return True
        
        if not value:
            self.add_error(field_name, "البريد الإلكتروني مطلوب")
            return False
        
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, value):
            self.add_error(field_name, "يرجى إدخال بريد إلكتروني صحيح")
            return False
        
        return True
    
    def validate_phone(self, field_name, value, required=True):
        """التحقق من رقم الهاتف"""
        if not value and not required:
            return True
        
        if not value:
            self.add_error(field_name, "رقم الهاتف مطلوب")
            return False
        
        # إزالة المسافات والرموز
        clean_phone = re.sub(r'[\s\-\(\)]', '', value)
        
        # التحقق من الطول والأرقام
        if not re.match(r'^[\+]?[0-9]{10,15}$', clean_phone):
            self.add_error(field_name, "يرجى إدخال رقم هاتف صحيح")
            return False
        
        return True
    
    def validate_number(self, field_name, value, min_value=None, max_value=None, required=True):
        """التحقق من الأرقام"""
        if not value and not required:
            return True
        
        if not value:
            self.add_error(field_name, f"حقل {field_name} مطلوب")
            return False
        
        try:
            num_value = float(value)
            
            if min_value is not None and num_value < min_value:
                self.add_error(field_name, f"القيمة يجب أن تكون أكبر من أو تساوي {min_value}")
                return False
            
            if max_value is not None and num_value > max_value:
                self.add_error(field_name, f"القيمة يجب أن تكون أقل من أو تساوي {max_value}")
                return False
            
            return True
            
        except (ValueError, TypeError):
            self.add_error(field_name, "يرجى إدخال رقم صحيح")
            return False
    
    def validate_decimal(self, field_name, value, decimal_places=2, required=True):
        """التحقق من الأرقام العشرية"""
        if not value and not required:
            return True
        
        if not value:
            self.add_error(field_name, f"حقل {field_name} مطلوب")
            return False
        
        try:
            decimal_value = Decimal(str(value))
            
            # التحقق من عدد الخانات العشرية
            if decimal_value.as_tuple().exponent < -decimal_places:
                self.add_error(field_name, f"عدد الخانات العشرية لا يجب أن يتجاوز {decimal_places}")
                return False
            
            return True
            
        except (InvalidOperation, ValueError):
            self.add_error(field_name, "يرجى إدخال رقم عشري صحيح")
            return False
    
    def validate_date(self, field_name, value, date_format='%Y-%m-%d', required=True):
        """التحقق من التاريخ"""
        if not value and not required:
            return True
        
        if not value:
            self.add_error(field_name, f"حقل {field_name} مطلوب")
            return False
        
        try:
            datetime.strptime(value, date_format)
            return True
        except ValueError:
            self.add_error(field_name, "يرجى إدخال تاريخ صحيح")
            return False
    
    def validate_choice(self, field_name, value, choices, required=True):
        """التحقق من الخيارات المحددة"""
        if not value and not required:
            return True
        
        if not value:
            self.add_error(field_name, f"حقل {field_name} مطلوب")
            return False
        
        if value not in choices:
            self.add_error(field_name, "يرجى اختيار قيمة صحيحة")
            return False
        
        return True
    
    def validate_length(self, field_name, value, min_length=None, max_length=None, required=True):
        """التحقق من طول النص"""
        if not value and not required:
            return True
        
        if not value:
            self.add_error(field_name, f"حقل {field_name} مطلوب")
            return False
        
        length = len(str(value))
        
        if min_length is not None and length < min_length:
            self.add_error(field_name, f"الطول يجب أن يكون {min_length} أحرف على الأقل")
            return False
        
        if max_length is not None and length > max_length:
            self.add_error(field_name, f"الطول يجب أن لا يتجاوز {max_length} حرف")
            return False
        
        return True
    
    def validate_arabic_text(self, field_name, value, required=True):
        """التحقق من النص العربي"""
        if not value and not required:
            return True
        
        if not value:
            self.add_error(field_name, f"حقل {field_name} مطلوب")
            return False
        
        # التحقق من وجود أحرف عربية
        arabic_pattern = r'[\u0600-\u06FF]'
        if not re.search(arabic_pattern, value):
            self.add_error(field_name, "يرجى إدخال نص باللغة العربية")
            return False
        
        return True
    
    def add_error(self, field_name, message):
        """إضافة خطأ"""
        if field_name not in self.errors:
            self.errors[field_name] = []
        self.errors[field_name].append(message)
        self.is_valid = False
    
    def clean_data(self, field_name, value, data_type='string'):
        """تنظيف البيانات"""
        if not value:
            return None
        
        try:
            if data_type == 'string':
                cleaned = str(value).strip()
            elif data_type == 'int':
                cleaned = int(value)
            elif data_type == 'float':
                cleaned = float(value)
            elif data_type == 'decimal':
                cleaned = Decimal(str(value))
            elif data_type == 'date':
                cleaned = datetime.strptime(value, '%Y-%m-%d').date()
            elif data_type == 'datetime':
                cleaned = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
            elif data_type == 'bool':
                cleaned = value.lower() in ['true', '1', 'yes', 'on']
            else:
                cleaned = value
            
            self.cleaned_data[field_name] = cleaned
            return cleaned
            
        except (ValueError, TypeError, InvalidOperation) as e:
            self.add_error(field_name, f"خطأ في تحويل البيانات: {str(e)}")
            return None
    
    def get_errors_json(self):
        """الحصول على الأخطاء بصيغة JSON"""
        return {
            'success': False,
            'errors': self.errors,
            'message': 'يوجد أخطاء في البيانات المدخلة'
        }
    
    def get_success_json(self, message="تم الحفظ بنجاح", data=None):
        """الحصول على رد النجاح بصيغة JSON"""
        response = {
            'success': True,
            'message': message
        }
        if data:
            response['data'] = data
        return response

def validate_form(validation_rules):
    """Decorator للتحقق من النماذج"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            processor = FormProcessor()
            
            # تطبيق قواعد التحقق
            for field_name, rules in validation_rules.items():
                value = request.form.get(field_name)
                
                # التحقق من القواعد
                for rule in rules:
                    rule_type = rule.get('type')
                    required = rule.get('required', True)
                    
                    if rule_type == 'required':
                        processor.validate_required(field_name, value, rule.get('message'))
                    elif rule_type == 'email':
                        processor.validate_email(field_name, value, required)
                    elif rule_type == 'phone':
                        processor.validate_phone(field_name, value, required)
                    elif rule_type == 'number':
                        processor.validate_number(
                            field_name, value, 
                            rule.get('min'), rule.get('max'), required
                        )
                    elif rule_type == 'decimal':
                        processor.validate_decimal(
                            field_name, value, 
                            rule.get('decimal_places', 2), required
                        )
                    elif rule_type == 'date':
                        processor.validate_date(
                            field_name, value, 
                            rule.get('format', '%Y-%m-%d'), required
                        )
                    elif rule_type == 'choice':
                        processor.validate_choice(
                            field_name, value, rule.get('choices', []), required
                        )
                    elif rule_type == 'length':
                        processor.validate_length(
                            field_name, value,
                            rule.get('min'), rule.get('max'), required
                        )
                    elif rule_type == 'arabic':
                        processor.validate_arabic_text(field_name, value, required)
                
                # تنظيف البيانات
                data_type = rules[0].get('data_type', 'string') if rules else 'string'
                processor.clean_data(field_name, value, data_type)
            
            # إذا كانت هناك أخطاء
            if not processor.is_valid:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify(processor.get_errors_json())
                else:
                    for field, errors in processor.errors.items():
                        for error in errors:
                            flash(f"{field}: {error}", 'error')
                    return func(*args, **kwargs)
            
            # إضافة البيانات المنظفة إلى kwargs
            kwargs['cleaned_data'] = processor.cleaned_data
            kwargs['form_processor'] = processor
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator

# قواعد التحقق الشائعة للنظام المحاسبي
CUSTOMER_VALIDATION_RULES = {
    'name': [
        {'type': 'required', 'message': 'اسم العميل مطلوب'},
        {'type': 'length', 'min': 2, 'max': 100},
        {'type': 'arabic', 'required': False}
    ],
    'email': [
        {'type': 'email', 'required': False}
    ],
    'phone': [
        {'type': 'phone', 'required': False}
    ]
}

INVOICE_VALIDATION_RULES = {
    'customer_id': [
        {'type': 'required', 'message': 'العميل مطلوب'},
        {'type': 'number', 'min': 1, 'data_type': 'int'}
    ],
    'date': [
        {'type': 'required', 'message': 'تاريخ الفاتورة مطلوب'},
        {'type': 'date', 'data_type': 'date'}
    ],
    'total_amount': [
        {'type': 'required', 'message': 'المبلغ الإجمالي مطلوب'},
        {'type': 'decimal', 'decimal_places': 2, 'data_type': 'decimal'},
        {'type': 'number', 'min': 0.01}
    ],
    'vat_amount': [
        {'type': 'decimal', 'decimal_places': 2, 'required': False, 'data_type': 'decimal'},
        {'type': 'number', 'min': 0, 'required': False}
    ]
}

EMPLOYEE_VALIDATION_RULES = {
    'name': [
        {'type': 'required', 'message': 'اسم الموظف مطلوب'},
        {'type': 'length', 'min': 2, 'max': 100},
        {'type': 'arabic'}
    ],
    'email': [
        {'type': 'email', 'required': False}
    ],
    'phone': [
        {'type': 'phone', 'required': False}
    ],
    'salary': [
        {'type': 'required', 'message': 'الراتب مطلوب'},
        {'type': 'decimal', 'decimal_places': 2, 'data_type': 'decimal'},
        {'type': 'number', 'min': 0.01}
    ],
    'hire_date': [
        {'type': 'required', 'message': 'تاريخ التوظيف مطلوب'},
        {'type': 'date', 'data_type': 'date'}
    ]
}
