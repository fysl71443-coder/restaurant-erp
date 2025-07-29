/*!
 * نظام المحاسبة الاحترافي - JavaScript الرئيسي
 * Professional Accounting System - Main JavaScript
 */

// ========================================
// المتغيرات العامة
// ========================================
const APP = {
    name: 'نظام المحاسبة الاحترافي',
    version: '2.0.0',
    debug: false,
    
    // إعدادات AJAX
    ajax: {
        timeout: 30000,
        retries: 3
    },
    
    // إعدادات التنبيهات
    notifications: {
        duration: 5000,
        position: 'top-end'
    }
};

// ========================================
// الوظائف المساعدة العامة
// ========================================

/**
 * عرض رسالة تنبيه
 */
function showAlert(message, type = 'info', duration = 5000) {
    const alertTypes = {
        'success': { icon: 'check-circle', class: 'alert-success' },
        'error': { icon: 'exclamation-triangle', class: 'alert-danger' },
        'warning': { icon: 'exclamation-triangle', class: 'alert-warning' },
        'info': { icon: 'info-circle', class: 'alert-info' }
    };
    
    const alertConfig = alertTypes[type] || alertTypes['info'];
    
    const alertHtml = `
        <div class="alert ${alertConfig.class} alert-dismissible fade show animate-fadeIn" role="alert">
            <i class="fas fa-${alertConfig.icon} me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    // إضافة التنبيه إلى الصفحة
    const alertContainer = $('#alertContainer');
    if (alertContainer.length) {
        alertContainer.append(alertHtml);
    } else {
        $('body').prepend(`<div id="alertContainer" class="position-fixed top-0 end-0 p-3" style="z-index: 9999;">${alertHtml}</div>`);
    }
    
    // إخفاء التنبيه تلقائياً
    setTimeout(() => {
        $('.alert').fadeOut('slow', function() {
            $(this).remove();
        });
    }, duration);
}

/**
 * عرض مؤشر التحميل
 */
function showLoading(message = 'جاري التحميل...') {
    const loadingHtml = `
        <div id="loadingOverlay" class="position-fixed top-0 start-0 w-100 h-100 d-flex align-items-center justify-content-center" 
             style="background: rgba(0,0,0,0.5); z-index: 9999;">
            <div class="bg-white p-4 rounded-3 text-center">
                <div class="spinner-border text-primary mb-3" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <div class="fw-bold">${message}</div>
            </div>
        </div>
    `;
    
    $('body').append(loadingHtml);
}

/**
 * إخفاء مؤشر التحميل
 */
function hideLoading() {
    $('#loadingOverlay').fadeOut('fast', function() {
        $(this).remove();
    });
}

/**
 * تأكيد الحذف
 */
function confirmDelete(message = 'هل أنت متأكد من الحذف؟', callback = null) {
    const confirmHtml = `
        <div class="modal fade" id="confirmDeleteModal" tabindex="-1">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-header bg-danger text-white">
                        <h5 class="modal-title">
                            <i class="fas fa-exclamation-triangle me-2"></i>
                            تأكيد الحذف
                        </h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body text-center">
                        <i class="fas fa-trash-alt fa-3x text-danger mb-3"></i>
                        <p class="mb-0">${message}</p>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                            <i class="fas fa-times me-2"></i>إلغاء
                        </button>
                        <button type="button" class="btn btn-danger" id="confirmDeleteBtn">
                            <i class="fas fa-trash me-2"></i>حذف
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // إزالة النافذة السابقة إن وجدت
    $('#confirmDeleteModal').remove();
    
    // إضافة النافذة الجديدة
    $('body').append(confirmHtml);
    
    // عرض النافذة
    const modal = new bootstrap.Modal(document.getElementById('confirmDeleteModal'));
    modal.show();
    
    // معالج زر التأكيد
    $('#confirmDeleteBtn').click(function() {
        modal.hide();
        if (callback && typeof callback === 'function') {
            callback();
        }
    });
    
    // إزالة النافذة عند الإغلاق
    $('#confirmDeleteModal').on('hidden.bs.modal', function() {
        $(this).remove();
    });
}

/**
 * تنسيق الأرقام
 */
function formatNumber(number, decimals = 2) {
    return parseFloat(number).toLocaleString('ar-SA', {
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals
    });
}

/**
 * تنسيق العملة
 */
function formatCurrency(amount, currency = 'ر.س') {
    return `${formatNumber(amount)} ${currency}`;
}

/**
 * تنسيق التاريخ
 */
function formatDate(date, format = 'YYYY-MM-DD') {
    if (typeof date === 'string') {
        date = new Date(date);
    }
    
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    
    switch (format) {
        case 'DD/MM/YYYY':
            return `${day}/${month}/${year}`;
        case 'MM/DD/YYYY':
            return `${month}/${day}/${year}`;
        default:
            return `${year}-${month}-${day}`;
    }
}

/**
 * التحقق من صحة البريد الإلكتروني
 */
function validateEmail(email) {
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return regex.test(email);
}

/**
 * التحقق من صحة رقم الهاتف السعودي
 */
function validateSaudiPhone(phone) {
    const regex = /^(05|5)[0-9]{8}$/;
    return regex.test(phone.replace(/\s+/g, ''));
}

/**
 * إرسال طلب AJAX محسن
 */
function ajaxRequest(options) {
    const defaults = {
        method: 'GET',
        timeout: APP.ajax.timeout,
        dataType: 'json',
        beforeSend: function() {
            showLoading();
        },
        complete: function() {
            hideLoading();
        },
        error: function(xhr, status, error) {
            let message = 'حدث خطأ غير متوقع';
            
            if (xhr.responseJSON && xhr.responseJSON.message) {
                message = xhr.responseJSON.message;
            } else if (xhr.status === 404) {
                message = 'الصفحة المطلوبة غير موجودة';
            } else if (xhr.status === 500) {
                message = 'خطأ في الخادم';
            } else if (xhr.status === 403) {
                message = 'ليس لديك صلاحية للوصول';
            }
            
            showAlert(message, 'error');
        }
    };
    
    return $.ajax($.extend({}, defaults, options));
}

// ========================================
// معالجات الأحداث العامة
// ========================================

$(document).ready(function() {
    
    // إعداد CSRF Token للطلبات
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", $('meta[name=csrf-token]').attr('content'));
            }
        }
    });
    
    // تبديل الشريط الجانبي للهواتف
    $('#sidebarToggle').click(function() {
        $('#sidebar').toggleClass('show');
        $('#mainContent').toggleClass('expanded');
    });
    
    // إغلاق الشريط الجانبي عند النقر خارجه
    $(document).click(function(e) {
        if ($(window).width() <= 768) {
            if (!$(e.target).closest('#sidebar, #sidebarToggle').length) {
                $('#sidebar').removeClass('show');
                $('#mainContent').removeClass('expanded');
            }
        }
    });
    
    // إخفاء التنبيهات تلقائياً
    setTimeout(function() {
        $('.alert').fadeOut('slow');
    }, APP.notifications.duration);
    
    // تفعيل tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // تفعيل popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // معالج أزرار الحذف
    $(document).on('click', '.btn-delete', function(e) {
        e.preventDefault();
        const url = $(this).attr('href') || $(this).data('url');
        const message = $(this).data('message') || 'هل أنت متأكد من الحذف؟';
        
        confirmDelete(message, function() {
            if (url) {
                window.location.href = url;
            }
        });
    });
    
    // معالج النماذج مع AJAX
    $(document).on('submit', '.ajax-form', function(e) {
        e.preventDefault();
        
        const form = $(this);
        const url = form.attr('action');
        const method = form.attr('method') || 'POST';
        const data = new FormData(this);
        
        ajaxRequest({
            url: url,
            method: method,
            data: data,
            processData: false,
            contentType: false,
            success: function(response) {
                if (response.success) {
                    showAlert(response.message || 'تم الحفظ بنجاح', 'success');
                    
                    // إعادة تحميل الصفحة أو إعادة توجيه
                    if (response.redirect) {
                        setTimeout(() => {
                            window.location.href = response.redirect;
                        }, 1000);
                    } else if (response.reload) {
                        setTimeout(() => {
                            location.reload();
                        }, 1000);
                    }
                } else {
                    showAlert(response.message || 'حدث خطأ', 'error');
                }
            }
        });
    });
    
    // تنسيق حقول الأرقام
    $(document).on('input', '.number-input', function() {
        let value = $(this).val().replace(/[^\d.-]/g, '');
        $(this).val(value);
    });
    
    // تنسيق حقول العملة
    $(document).on('input', '.currency-input', function() {
        let value = $(this).val().replace(/[^\d.]/g, '');
        if (value) {
            $(this).val(formatNumber(parseFloat(value)));
        }
    });
    
    // تنسيق حقول الهاتف
    $(document).on('input', '.phone-input', function() {
        let value = $(this).val().replace(/\D/g, '');
        if (value.length > 0) {
            if (value.startsWith('966')) {
                value = value.substring(3);
            }
            if (value.startsWith('0')) {
                value = value.substring(1);
            }
            if (value.length === 9) {
                value = `05${value.substring(1)}`;
            }
        }
        $(this).val(value);
    });
    
    // البحث المباشر
    let searchTimeout;
    $(document).on('input', '.live-search', function() {
        const input = $(this);
        const query = input.val();
        const target = input.data('target');
        
        clearTimeout(searchTimeout);
        
        if (query.length >= 2) {
            searchTimeout = setTimeout(function() {
                ajaxRequest({
                    url: '/api/search',
                    data: { q: query, type: target },
                    success: function(response) {
                        // عرض نتائج البحث
                        displaySearchResults(response.results, target);
                    }
                });
            }, 500);
        }
    });
    
    // طباعة الصفحة
    $(document).on('click', '.btn-print', function(e) {
        e.preventDefault();
        window.print();
    });
    
    // تصدير البيانات
    $(document).on('click', '.btn-export', function(e) {
        e.preventDefault();
        const format = $(this).data('format') || 'excel';
        const url = $(this).attr('href') || $(this).data('url');
        
        if (url) {
            showLoading('جاري تصدير البيانات...');
            window.location.href = `${url}?format=${format}`;
            setTimeout(hideLoading, 2000);
        }
    });
    
    // تحديث الوقت كل دقيقة
    setInterval(updateTime, 60000);
    updateTime();
    
    // حفظ تلقائي للنماذج
    let autoSaveTimeout;
    $(document).on('input', '.auto-save', function() {
        clearTimeout(autoSaveTimeout);
        autoSaveTimeout = setTimeout(function() {
            // حفظ تلقائي
            console.log('Auto-saving...');
        }, 5000);
    });
    
});

// ========================================
// وظائف مساعدة إضافية
// ========================================

/**
 * تحديث الوقت
 */
function updateTime() {
    const now = new Date();
    const timeString = now.toLocaleTimeString('ar-SA');
    const dateString = now.toLocaleDateString('ar-SA');
    
    $('.current-time').text(timeString);
    $('.current-date').text(dateString);
}

/**
 * عرض نتائج البحث
 */
function displaySearchResults(results, target) {
    const container = $(`#${target}-results`);
    if (container.length) {
        container.empty();
        
        if (results.length > 0) {
            results.forEach(function(item) {
                const resultHtml = `
                    <div class="search-result-item p-2 border-bottom" data-id="${item.id}">
                        <div class="fw-bold">${item.name}</div>
                        <small class="text-muted">${item.description || ''}</small>
                    </div>
                `;
                container.append(resultHtml);
            });
            container.show();
        } else {
            container.hide();
        }
    }
}

/**
 * تحديث الإحصائيات
 */
function updateStats() {
    ajaxRequest({
        url: '/api/stats',
        success: function(response) {
            // تحديث الإحصائيات في الصفحة
            Object.keys(response).forEach(function(key) {
                $(`.stat-${key}`).text(response[key]);
            });
        }
    });
}

/**
 * تحديث الإشعارات
 */
function updateNotifications() {
    ajaxRequest({
        url: '/api/notifications',
        success: function(response) {
            const count = response.unread_count || 0;
            $('.notification-count').text(count);
            
            if (count > 0) {
                $('.notification-badge').show();
            } else {
                $('.notification-badge').hide();
            }
        }
    });
}

// ========================================
// معالجة الأخطاء العامة
// ========================================

window.onerror = function(msg, url, lineNo, columnNo, error) {
    if (APP.debug) {
        console.error('JavaScript Error:', {
            message: msg,
            source: url,
            line: lineNo,
            column: columnNo,
            error: error
        });
    }
    
    // إرسال الخطأ للخادم (اختياري)
    // ajaxRequest({
    //     url: '/api/log-error',
    //     method: 'POST',
    //     data: {
    //         message: msg,
    //         source: url,
    //         line: lineNo,
    //         column: columnNo
    //     }
    // });
    
    return false;
};

// ========================================
// تصدير الوظائف للاستخدام العام
// ========================================

window.APP = APP;
window.showAlert = showAlert;
window.showLoading = showLoading;
window.hideLoading = hideLoading;
window.confirmDelete = confirmDelete;
window.formatNumber = formatNumber;
window.formatCurrency = formatCurrency;
window.formatDate = formatDate;
window.validateEmail = validateEmail;
window.validateSaudiPhone = validateSaudiPhone;
window.ajaxRequest = ajaxRequest;
