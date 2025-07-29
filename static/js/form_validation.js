/**
 * نظام التحقق من النماذج والتحقق من البيانات
 * Form Validation and Data Verification System
 */

// قواعد التحقق
const validationRules = {
    required: {
        test: (value) => value !== null && value !== undefined && value.toString().trim() !== '',
        message: 'هذا الحقل مطلوب'
    },
    email: {
        test: (value) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value),
        message: 'يرجى إدخال بريد إلكتروني صحيح'
    },
    phone: {
        test: (value) => /^[\+]?[0-9\s\-\(\)]{10,}$/.test(value),
        message: 'يرجى إدخال رقم هاتف صحيح'
    },
    number: {
        test: (value) => !isNaN(value) && isFinite(value),
        message: 'يرجى إدخال رقم صحيح'
    },
    positive: {
        test: (value) => parseFloat(value) > 0,
        message: 'يجب أن يكون الرقم أكبر من صفر'
    },
    minLength: {
        test: (value, min) => value.toString().length >= min,
        message: (min) => `يجب أن يكون الطول ${min} أحرف على الأقل`
    },
    maxLength: {
        test: (value, max) => value.toString().length <= max,
        message: (max) => `يجب أن لا يتجاوز الطول ${max} حرف`
    },
    date: {
        test: (value) => !isNaN(Date.parse(value)),
        message: 'يرجى إدخال تاريخ صحيح'
    },
    futureDate: {
        test: (value) => new Date(value) > new Date(),
        message: 'يجب أن يكون التاريخ في المستقبل'
    },
    pastDate: {
        test: (value) => new Date(value) < new Date(),
        message: 'يجب أن يكون التاريخ في الماضي'
    }
};

// فئة التحقق من النماذج
class FormValidator {
    constructor(form) {
        this.form = form;
        this.errors = {};
        this.isValid = true;
        this.setupEventListeners();
    }

    // إعداد مستمعي الأحداث
    setupEventListeners() {
        // التحقق عند الكتابة
        this.form.querySelectorAll('input, select, textarea').forEach(field => {
            field.addEventListener('blur', () => this.validateField(field));
            field.addEventListener('input', () => this.clearFieldError(field));
        });

        // التحقق عند الإرسال
        this.form.addEventListener('submit', (e) => {
            if (!this.validateForm()) {
                e.preventDefault();
                this.showErrors();
            }
        });
    }

    // التحقق من حقل واحد
    validateField(field) {
        const fieldName = field.name || field.id;
        const value = field.value.trim();
        const rules = this.getFieldRules(field);
        
        this.errors[fieldName] = [];

        // تطبيق قواعد التحقق
        rules.forEach(rule => {
            if (!this.applyRule(value, rule)) {
                this.errors[fieldName].push(rule.message);
            }
        });

        // عرض الأخطاء
        this.displayFieldError(field, this.errors[fieldName]);
        
        return this.errors[fieldName].length === 0;
    }

    // الحصول على قواعد الحقل
    getFieldRules(field) {
        const rules = [];
        const rulesAttr = field.dataset.rules;
        
        if (rulesAttr) {
            const ruleNames = rulesAttr.split('|');
            ruleNames.forEach(ruleName => {
                const [name, param] = ruleName.split(':');
                if (validationRules[name]) {
                    rules.push({
                        name: name,
                        param: param,
                        test: validationRules[name].test,
                        message: typeof validationRules[name].message === 'function' 
                            ? validationRules[name].message(param)
                            : validationRules[name].message
                    });
                }
            });
        }

        // قواعد HTML5 التلقائية
        if (field.required) {
            rules.unshift({
                name: 'required',
                test: validationRules.required.test,
                message: validationRules.required.message
            });
        }

        if (field.type === 'email') {
            rules.push({
                name: 'email',
                test: validationRules.email.test,
                message: validationRules.email.message
            });
        }

        if (field.type === 'number') {
            rules.push({
                name: 'number',
                test: validationRules.number.test,
                message: validationRules.number.message
            });
        }

        return rules;
    }

    // تطبيق قاعدة التحقق
    applyRule(value, rule) {
        if (rule.name === 'required') {
            return rule.test(value);
        }
        
        // تخطي القواعد الأخرى إذا كان الحقل فارغاً وغير مطلوب
        if (!value) return true;
        
        if (rule.param) {
            return rule.test(value, rule.param);
        } else {
            return rule.test(value);
        }
    }

    // عرض خطأ الحقل
    displayFieldError(field, errors) {
        const errorContainer = this.getErrorContainer(field);
        
        if (errors.length > 0) {
            field.classList.add('is-invalid');
            field.classList.remove('is-valid');
            errorContainer.innerHTML = errors.join('<br>');
            errorContainer.style.display = 'block';
        } else {
            field.classList.remove('is-invalid');
            field.classList.add('is-valid');
            errorContainer.style.display = 'none';
        }
    }

    // مسح خطأ الحقل
    clearFieldError(field) {
        const errorContainer = this.getErrorContainer(field);
        field.classList.remove('is-invalid');
        errorContainer.style.display = 'none';
    }

    // الحصول على حاوي الخطأ
    getErrorContainer(field) {
        const fieldName = field.name || field.id;
        let errorContainer = document.getElementById(`${fieldName}-error`);
        
        if (!errorContainer) {
            errorContainer = document.createElement('div');
            errorContainer.id = `${fieldName}-error`;
            errorContainer.className = 'invalid-feedback';
            field.parentNode.appendChild(errorContainer);
        }
        
        return errorContainer;
    }

    // التحقق من النموذج كاملاً
    validateForm() {
        this.isValid = true;
        this.errors = {};

        this.form.querySelectorAll('input, select, textarea').forEach(field => {
            if (!this.validateField(field)) {
                this.isValid = false;
            }
        });

        return this.isValid;
    }

    // عرض جميع الأخطاء
    showErrors() {
        const errorFields = this.form.querySelectorAll('.is-invalid');
        if (errorFields.length > 0) {
            // التمرير إلى أول حقل خطأ
            errorFields[0].scrollIntoView({ behavior: 'smooth', block: 'center' });
            errorFields[0].focus();
        }
    }

    // إضافة قاعدة تحقق مخصصة
    addCustomRule(name, test, message) {
        validationRules[name] = { test, message };
    }
}

// التحقق من البيانات في الوقت الفعلي
class RealTimeValidator {
    constructor() {
        this.setupGlobalValidation();
    }

    setupGlobalValidation() {
        // التحقق من الأرقام
        document.addEventListener('input', (e) => {
            if (e.target.type === 'number' || e.target.dataset.type === 'number') {
                this.validateNumber(e.target);
            }
        });

        // التحقق من البريد الإلكتروني
        document.addEventListener('input', (e) => {
            if (e.target.type === 'email') {
                this.validateEmail(e.target);
            }
        });

        // التحقق من التواريخ
        document.addEventListener('change', (e) => {
            if (e.target.type === 'date') {
                this.validateDate(e.target);
            }
        });
    }

    validateNumber(field) {
        const value = field.value;
        const isValid = !isNaN(value) && isFinite(value);
        
        if (value && !isValid) {
            this.showFieldFeedback(field, 'يرجى إدخال رقم صحيح', 'error');
        } else if (value && isValid) {
            this.showFieldFeedback(field, 'رقم صحيح', 'success');
        } else {
            this.clearFieldFeedback(field);
        }
    }

    validateEmail(field) {
        const value = field.value;
        const isValid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
        
        if (value && !isValid) {
            this.showFieldFeedback(field, 'يرجى إدخال بريد إلكتروني صحيح', 'error');
        } else if (value && isValid) {
            this.showFieldFeedback(field, 'بريد إلكتروني صحيح', 'success');
        } else {
            this.clearFieldFeedback(field);
        }
    }

    validateDate(field) {
        const value = field.value;
        const date = new Date(value);
        const today = new Date();
        
        if (field.dataset.validateFuture && date <= today) {
            this.showFieldFeedback(field, 'يجب أن يكون التاريخ في المستقبل', 'error');
        } else if (field.dataset.validatePast && date >= today) {
            this.showFieldFeedback(field, 'يجب أن يكون التاريخ في الماضي', 'error');
        } else if (value) {
            this.showFieldFeedback(field, 'تاريخ صحيح', 'success');
        }
    }

    showFieldFeedback(field, message, type) {
        let feedback = field.parentNode.querySelector('.field-feedback');
        
        if (!feedback) {
            feedback = document.createElement('div');
            feedback.className = 'field-feedback';
            field.parentNode.appendChild(feedback);
        }
        
        feedback.textContent = message;
        feedback.className = `field-feedback ${type === 'error' ? 'text-danger' : 'text-success'}`;
        feedback.style.fontSize = '0.875rem';
        feedback.style.marginTop = '0.25rem';
    }

    clearFieldFeedback(field) {
        const feedback = field.parentNode.querySelector('.field-feedback');
        if (feedback) {
            feedback.remove();
        }
    }
}

// تهيئة النظام
document.addEventListener('DOMContentLoaded', function() {
    // تهيئة التحقق في الوقت الفعلي
    new RealTimeValidator();

    // تهيئة التحقق للنماذج
    document.querySelectorAll('form[data-validate="true"]').forEach(form => {
        new FormValidator(form);
    });

    // إضافة قواعد تحقق مخصصة للنظام المحاسبي
    const customRules = {
        arabicName: {
            test: (value) => /^[\u0600-\u06FF\s]+$/.test(value),
            message: 'يرجى إدخال اسم باللغة العربية فقط'
        },
        invoiceNumber: {
            test: (value) => /^[A-Z0-9\-]+$/.test(value),
            message: 'رقم الفاتورة يجب أن يحتوي على أرقام وحروف إنجليزية فقط'
        },
        percentage: {
            test: (value) => {
                const num = parseFloat(value);
                return num >= 0 && num <= 100;
            },
            message: 'النسبة يجب أن تكون بين 0 و 100'
        }
    };

    // إضافة القواعد المخصصة
    Object.keys(customRules).forEach(ruleName => {
        validationRules[ruleName] = customRules[ruleName];
    });

    console.log('نظام التحقق من النماذج تم تهيئته بنجاح');
});
