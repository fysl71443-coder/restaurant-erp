/*!
 * نظام الترجمة من جانب العميل
 * Client-side Internationalization System
 */

// ========================================
// نظام الترجمة الأساسي
// ========================================

const I18N = {
    // اللغة الحالية
    currentLocale: 'ar',
    
    // الترجمات المحملة
    translations: {},
    
    // اللغات المدعومة
    supportedLocales: ['ar', 'en'],
    
    // اللغات RTL
    rtlLanguages: ['ar', 'he', 'fa', 'ur'],
    
    /**
     * تهيئة نظام الترجمة
     */
    init: function(locale = 'ar') {
        this.currentLocale = locale;
        this.loadTranslations(locale);
        this.updatePageDirection();
        this.updateDateTimeFormats();
    },
    
    /**
     * تحميل ترجمات اللغة
     */
    loadTranslations: function(locale) {
        const self = this;
        
        // تحميل الترجمات من الخادم
        $.ajax({
            url: `/language/api/translations/messages`,
            method: 'GET',
            async: false, // تحميل متزامن للتأكد من توفر الترجمات
            success: function(response) {
                if (response.translations) {
                    self.translations[locale] = response.translations;
                }
            },
            error: function() {
                console.warn(`Failed to load translations for locale: ${locale}`);
                // استخدام ترجمات افتراضية
                self.translations[locale] = self.getDefaultTranslations(locale);
            }
        });
    },
    
    /**
     * الحصول على ترجمات افتراضية
     */
    getDefaultTranslations: function(locale) {
        const translations = {
            'ar': {
                'Loading...': 'جاري التحميل...',
                'Please wait...': 'يرجى الانتظار...',
                'Error': 'خطأ',
                'Success': 'نجح',
                'Warning': 'تحذير',
                'Info': 'معلومات',
                'Save': 'حفظ',
                'Cancel': 'إلغاء',
                'Delete': 'حذف',
                'Edit': 'تعديل',
                'View': 'عرض',
                'Add': 'إضافة',
                'Search': 'بحث',
                'Filter': 'تصفية',
                'Export': 'تصدير',
                'Print': 'طباعة',
                'Yes': 'نعم',
                'No': 'لا',
                'OK': 'موافق',
                'Are you sure?': 'هل أنت متأكد؟',
                'This action cannot be undone': 'لا يمكن التراجع عن هذا الإجراء',
                'Confirm Delete': 'تأكيد الحذف',
                'Language changed successfully': 'تم تغيير اللغة بنجاح'
            },
            'en': {
                'Loading...': 'Loading...',
                'Please wait...': 'Please wait...',
                'Error': 'Error',
                'Success': 'Success',
                'Warning': 'Warning',
                'Info': 'Info',
                'Save': 'Save',
                'Cancel': 'Cancel',
                'Delete': 'Delete',
                'Edit': 'Edit',
                'View': 'View',
                'Add': 'Add',
                'Search': 'Search',
                'Filter': 'Filter',
                'Export': 'Export',
                'Print': 'Print',
                'Yes': 'Yes',
                'No': 'No',
                'OK': 'OK',
                'Are you sure?': 'Are you sure?',
                'This action cannot be undone': 'This action cannot be undone',
                'Confirm Delete': 'Confirm Delete',
                'Language changed successfully': 'Language changed successfully'
            }
        };
        
        return translations[locale] || translations['ar'];
    },
    
    /**
     * ترجمة نص
     */
    t: function(key, params = {}) {
        const locale = this.currentLocale;
        let translation = key; // القيمة الافتراضية
        
        // البحث عن الترجمة
        if (this.translations[locale] && this.translations[locale][key]) {
            translation = this.translations[locale][key];
        }
        
        // استبدال المعاملات
        Object.keys(params).forEach(param => {
            const placeholder = `{${param}}`;
            translation = translation.replace(new RegExp(placeholder, 'g'), params[param]);
        });
        
        return translation;
    },
    
    /**
     * تحديث اتجاه الصفحة
     */
    updatePageDirection: function() {
        const isRTL = this.rtlLanguages.includes(this.currentLocale);
        const direction = isRTL ? 'rtl' : 'ltr';
        
        $('html').attr('dir', direction);
        $('html').attr('lang', this.currentLocale);
        
        // تحديث فئات Bootstrap
        if (isRTL) {
            $('body').addClass('rtl').removeClass('ltr');
            // تحديث روابط Bootstrap RTL
            this.updateBootstrapRTL(true);
        } else {
            $('body').addClass('ltr').removeClass('rtl');
            this.updateBootstrapRTL(false);
        }
    },
    
    /**
     * تحديث Bootstrap RTL/LTR
     */
    updateBootstrapRTL: function(isRTL) {
        const bootstrapLink = $('link[href*="bootstrap"]');
        
        if (bootstrapLink.length) {
            const currentHref = bootstrapLink.attr('href');
            let newHref;
            
            if (isRTL && !currentHref.includes('.rtl.')) {
                newHref = currentHref.replace('.min.css', '.rtl.min.css');
            } else if (!isRTL && currentHref.includes('.rtl.')) {
                newHref = currentHref.replace('.rtl.min.css', '.min.css');
            }
            
            if (newHref && newHref !== currentHref) {
                bootstrapLink.attr('href', newHref);
            }
        }
    },
    
    /**
     * تحديث تنسيقات التاريخ والوقت
     */
    updateDateTimeFormats: function() {
        const locale = this.currentLocale;
        
        // تحديث تنسيق التاريخ في جميع عناصر التاريخ
        $('.date-display').each(function() {
            const dateValue = $(this).data('date');
            if (dateValue) {
                const formattedDate = I18N.formatDate(new Date(dateValue), locale);
                $(this).text(formattedDate);
            }
        });
        
        // تحديث تنسيق الوقت
        $('.time-display').each(function() {
            const timeValue = $(this).data('time');
            if (timeValue) {
                const formattedTime = I18N.formatTime(new Date(timeValue), locale);
                $(this).text(formattedTime);
            }
        });
    },
    
    /**
     * تنسيق التاريخ حسب اللغة
     */
    formatDate: function(date, locale = null) {
        locale = locale || this.currentLocale;
        
        const options = {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        };
        
        try {
            return date.toLocaleDateString(locale === 'ar' ? 'ar-SA' : 'en-US', options);
        } catch (e) {
            return date.toLocaleDateString('en-US', options);
        }
    },
    
    /**
     * تنسيق الوقت حسب اللغة
     */
    formatTime: function(date, locale = null) {
        locale = locale || this.currentLocale;
        
        const options = {
            hour: '2-digit',
            minute: '2-digit',
            hour12: locale === 'en'
        };
        
        try {
            return date.toLocaleTimeString(locale === 'ar' ? 'ar-SA' : 'en-US', options);
        } catch (e) {
            return date.toLocaleTimeString('en-US', options);
        }
    },
    
    /**
     * تنسيق الأرقام حسب اللغة
     */
    formatNumber: function(number, locale = null) {
        locale = locale || this.currentLocale;
        
        try {
            return number.toLocaleString(locale === 'ar' ? 'ar-SA' : 'en-US');
        } catch (e) {
            return number.toLocaleString('en-US');
        }
    },
    
    /**
     * تنسيق العملة حسب اللغة
     */
    formatCurrency: function(amount, currency = 'SAR', locale = null) {
        locale = locale || this.currentLocale;
        
        const options = {
            style: 'currency',
            currency: currency,
            minimumFractionDigits: 2
        };
        
        try {
            return amount.toLocaleString(locale === 'ar' ? 'ar-SA' : 'en-US', options);
        } catch (e) {
            return `${amount.toFixed(2)} ${currency}`;
        }
    },
    
    /**
     * تغيير اللغة
     */
    changeLanguage: function(newLocale) {
        if (!this.supportedLocales.includes(newLocale)) {
            console.error(`Unsupported locale: ${newLocale}`);
            return false;
        }
        
        this.currentLocale = newLocale;
        this.loadTranslations(newLocale);
        this.updatePageDirection();
        this.updateDateTimeFormats();
        this.translatePage();
        
        return true;
    },
    
    /**
     * ترجمة الصفحة الحالية
     */
    translatePage: function() {
        const self = this;
        
        // ترجمة العناصر المحددة بـ data-i18n
        $('[data-i18n]').each(function() {
            const key = $(this).data('i18n');
            const translation = self.t(key);
            
            if ($(this).is('input, textarea')) {
                $(this).attr('placeholder', translation);
            } else {
                $(this).text(translation);
            }
        });
        
        // ترجمة العناصر المحددة بـ data-i18n-title
        $('[data-i18n-title]').each(function() {
            const key = $(this).data('i18n-title');
            const translation = self.t(key);
            $(this).attr('title', translation);
        });
    }
};

// ========================================
// وظائف مساعدة عامة
// ========================================

/**
 * ترجمة نص (اختصار)
 */
function _(key, params = {}) {
    return I18N.t(key, params);
}

/**
 * تنسيق تاريخ
 */
function formatDate(date, locale = null) {
    return I18N.formatDate(date, locale);
}

/**
 * تنسيق وقت
 */
function formatTime(date, locale = null) {
    return I18N.formatTime(date, locale);
}

/**
 * تنسيق رقم
 */
function formatNumber(number, locale = null) {
    return I18N.formatNumber(number, locale);
}

/**
 * تنسيق عملة
 */
function formatCurrency(amount, currency = 'SAR', locale = null) {
    return I18N.formatCurrency(amount, currency, locale);
}

// ========================================
// تهيئة النظام عند تحميل الصفحة
// ========================================

$(document).ready(function() {
    // الحصول على اللغة الحالية من HTML
    const currentLang = $('html').attr('lang') || 'ar';
    
    // تهيئة نظام الترجمة
    I18N.init(currentLang);
    
    // ترجمة الصفحة
    I18N.translatePage();
    
    // تحديث الترجمات كل 30 ثانية (للمحتوى الديناميكي)
    setInterval(function() {
        I18N.translatePage();
    }, 30000);
});

// تصدير للاستخدام العام
window.I18N = I18N;
window._ = _;
