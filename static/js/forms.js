// وظائف إدارة النماذج والحفظ والتراجع

// متغيرات عامة
let formData = {};
let isFormDirty = false;
let originalFormData = {};

// تهيئة النموذج
function initializeForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return;

    // حفظ البيانات الأصلية
    originalFormData = getFormData(form);
    
    // إضافة مستمعي الأحداث للتغييرات
    addFormChangeListeners(form);
    
    // إضافة مستمع لمنع الخروج بدون حفظ
    addBeforeUnloadListener();
    
    // تفعيل الحفظ التلقائي
    enableAutoSave(form);
}

// الحصول على بيانات النموذج
function getFormData(form) {
    const data = {};
    const formData = new FormData(form);
    
    for (let [key, value] of formData.entries()) {
        data[key] = value;
    }
    
    return data;
}

// إضافة مستمعي التغييرات
function addFormChangeListeners(form) {
    const inputs = form.querySelectorAll('input, select, textarea');
    
    inputs.forEach(input => {
        input.addEventListener('input', function() {
            markFormAsDirty();
            updateUndoButton();
            showSaveIndicator();
        });
        
        input.addEventListener('change', function() {
            markFormAsDirty();
            updateUndoButton();
        });
    });
}

// تمييز النموذج كمُعدّل
function markFormAsDirty() {
    isFormDirty = true;
    updateSaveButton();
    updatePageTitle();
}

// تحديث زر الحفظ
function updateSaveButton() {
    const saveButtons = document.querySelectorAll('.save-btn');
    saveButtons.forEach(btn => {
        if (isFormDirty) {
            btn.classList.remove('btn-outline-primary');
            btn.classList.add('btn-primary');
            btn.innerHTML = '<i class="fas fa-save"></i> حفظ التغييرات';
        } else {
            btn.classList.remove('btn-primary');
            btn.classList.add('btn-outline-primary');
            btn.innerHTML = '<i class="fas fa-check"></i> محفوظ';
        }
    });
}

// تحديث زر التراجع
function updateUndoButton() {
    const undoButtons = document.querySelectorAll('.undo-btn');
    undoButtons.forEach(btn => {
        btn.disabled = !isFormDirty;
        if (isFormDirty) {
            btn.classList.remove('btn-outline-secondary');
            btn.classList.add('btn-warning');
        } else {
            btn.classList.remove('btn-warning');
            btn.classList.add('btn-outline-secondary');
        }
    });
}

// تحديث عنوان الصفحة
function updatePageTitle() {
    const title = document.title;
    if (isFormDirty && !title.includes('*')) {
        document.title = '* ' + title;
    } else if (!isFormDirty && title.includes('*')) {
        document.title = title.replace('* ', '');
    }
}

// إظهار مؤشر الحفظ
function showSaveIndicator() {
    let indicator = document.getElementById('saveIndicator');
    if (!indicator) {
        indicator = document.createElement('div');
        indicator.id = 'saveIndicator';
        indicator.className = 'save-indicator';
        indicator.innerHTML = '<i class="fas fa-circle text-warning"></i> غير محفوظ';
        document.body.appendChild(indicator);
    }
    
    indicator.style.display = 'block';
    indicator.className = 'save-indicator show';
}

// إخفاء مؤشر الحفظ
function hideSaveIndicator() {
    const indicator = document.getElementById('saveIndicator');
    if (indicator) {
        indicator.innerHTML = '<i class="fas fa-check-circle text-success"></i> تم الحفظ';
        setTimeout(() => {
            indicator.style.display = 'none';
        }, 2000);
    }
}

// الحفظ التلقائي
function enableAutoSave(form) {
    setInterval(() => {
        if (isFormDirty) {
            autoSaveForm(form);
        }
    }, 30000); // كل 30 ثانية
}

// حفظ تلقائي
function autoSaveForm(form) {
    const currentData = getFormData(form);
    localStorage.setItem('autoSave_' + form.id, JSON.stringify({
        data: currentData,
        timestamp: new Date().toISOString()
    }));
    
    showAutoSaveNotification();
}

// إظهار إشعار الحفظ التلقائي
function showAutoSaveNotification() {
    const notification = document.createElement('div');
    notification.className = 'auto-save-notification';
    notification.innerHTML = '<i class="fas fa-cloud"></i> تم الحفظ التلقائي';
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// استرداد البيانات المحفوظة تلقائياً
function restoreAutoSavedData(formId) {
    const saved = localStorage.getItem('autoSave_' + formId);
    if (saved) {
        const { data, timestamp } = JSON.parse(saved);
        const saveTime = new Date(timestamp);
        const now = new Date();
        const diffMinutes = (now - saveTime) / (1000 * 60);
        
        if (diffMinutes < 60) { // خلال الساعة الماضية
            if (confirm(`تم العثور على بيانات محفوظة تلقائياً من ${saveTime.toLocaleString('ar-SA')}. هل تريد استردادها؟`)) {
                fillFormWithData(formId, data);
                markFormAsDirty();
            }
        }
    }
}

// ملء النموذج بالبيانات
function fillFormWithData(formId, data) {
    const form = document.getElementById(formId);
    if (!form) return;
    
    Object.keys(data).forEach(key => {
        const input = form.querySelector(`[name="${key}"]`);
        if (input) {
            input.value = data[key];
        }
    });
}

// وظيفة التراجع
function undoChanges(formId) {
    if (!isFormDirty) return;
    
    if (confirm('هل أنت متأكد من التراجع عن جميع التغييرات؟')) {
        const form = document.getElementById(formId);
        if (form) {
            fillFormWithData(formId, originalFormData);
            isFormDirty = false;
            updateSaveButton();
            updateUndoButton();
            updatePageTitle();
            hideSaveIndicator();
            
            showUndoNotification();
        }
    }
}

// إظهار إشعار التراجع
function showUndoNotification() {
    const notification = document.createElement('div');
    notification.className = 'undo-notification';
    notification.innerHTML = '<i class="fas fa-undo"></i> تم التراجع عن التغييرات';
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// حفظ النموذج بسرعة فائقة
function saveForm(formId, url, method = 'POST') {
    const form = document.getElementById(formId);
    if (!form) return;

    // التحقق السريع من صحة النموذج
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }

    // تعطيل زر الحفظ فوراً
    const saveButton = form.querySelector('button[type="submit"], .save-btn');
    const originalText = saveButton ? saveButton.innerHTML : '';

    if (saveButton) {
        saveButton.disabled = true;
        saveButton.innerHTML = '<i class="fas fa-check"></i> محفوظ';
    }

    // إرسال البيانات فوراً
    const formData = new FormData(form);

    fetch(url || form.action, {
        method: method,
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => {
        // إعادة تفعيل الزر فوراً
        if (saveButton) {
            saveButton.disabled = false;
            saveButton.innerHTML = '<i class="fas fa-check text-success"></i> تم';
        }

        if (response.ok) {
            return response.json().catch(() => {
                return { success: true, message: 'تم الحفظ بنجاح' };
            });
        }
        throw new Error('فشل في الحفظ');
    })
    .then(data => {
        // نجح الحفظ
        isFormDirty = false;
        originalFormData = getFormData(form);
        updateSaveButton();
        updateUndoButton();
        updatePageTitle();
        hideSaveIndicator();

        // حذف البيانات المحفوظة تلقائياً
        localStorage.removeItem('autoSave_' + formId);

        // إعادة النص الأصلي للزر بعد ثانية واحدة
        setTimeout(() => {
            if (saveButton) {
                saveButton.innerHTML = originalText;
            }
        }, 1000);

        // إعادة التوجيه فوراً إذا لزم الأمر
        if (data.redirect) {
            window.location.href = data.redirect;
        } else if (data.reload) {
            window.location.reload();
        }
    })
    .catch(error => {
        // إظهار خطأ سريع
        if (saveButton) {
            saveButton.disabled = false;
            saveButton.innerHTML = '<i class="fas fa-times text-danger"></i> خطأ';
            setTimeout(() => {
                saveButton.innerHTML = originalText;
            }, 1500);
        }
    });
}

// إظهار مؤشر التحميل
function showLoadingIndicator() {
    let indicator = document.getElementById('loadingIndicator');
    if (!indicator) {
        indicator = document.createElement('div');
        indicator.id = 'loadingIndicator';
        indicator.className = 'loading-indicator';
        indicator.innerHTML = `
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">جاري التحميل...</span>
            </div>
            <div class="mt-2">جاري الحفظ...</div>
        `;
        document.body.appendChild(indicator);
    }
    indicator.style.display = 'flex';
}

// إخفاء مؤشر التحميل
function hideLoadingIndicator() {
    const indicator = document.getElementById('loadingIndicator');
    if (indicator) {
        indicator.style.display = 'none';
    }
}

// إظهار إشعار النجاح
function showSuccessNotification(message) {
    showNotification(message, 'success');
}

// إظهار إشعار الخطأ
function showErrorNotification(message) {
    showNotification(message, 'error');
}

// إظهار الإشعارات
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    
    const icon = type === 'success' ? 'check-circle' : 
                 type === 'error' ? 'exclamation-circle' : 'info-circle';
    
    notification.innerHTML = `
        <i class="fas fa-${icon}"></i>
        <span>${message}</span>
        <button class="notification-close" onclick="this.parentElement.remove()">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    document.body.appendChild(notification);
    
    // إزالة تلقائية بعد 5 ثوان
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, 5000);
}

// منع الخروج بدون حفظ
function addBeforeUnloadListener() {
    window.addEventListener('beforeunload', function(e) {
        if (isFormDirty) {
            e.preventDefault();
            e.returnValue = 'لديك تغييرات غير محفوظة. هل أنت متأكد من الخروج؟';
            return e.returnValue;
        }
    });
}

// تهيئة الصفحة
document.addEventListener('DOMContentLoaded', function() {
    // البحث عن النماذج وتهيئتها
    const forms = document.querySelectorAll('form[id]');
    forms.forEach(form => {
        initializeForm(form.id);
        
        // استرداد البيانات المحفوظة تلقائياً
        restoreAutoSavedData(form.id);
    });
    
    // إضافة مستمعي الأحداث للأزرار
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('save-btn') || e.target.closest('.save-btn')) {
            e.preventDefault();
            const form = e.target.closest('form');
            if (form) {
                saveForm(form.id, form.action, form.method);
            }
        }
        
        if (e.target.classList.contains('undo-btn') || e.target.closest('.undo-btn')) {
            e.preventDefault();
            const form = e.target.closest('form');
            if (form) {
                undoChanges(form.id);
            }
        }
    });
});

// اختصارات لوحة المفاتيح
document.addEventListener('keydown', function(e) {
    // Ctrl+S للحفظ
    if (e.ctrlKey && e.key === 's') {
        e.preventDefault();
        const form = document.querySelector('form[id]');
        if (form && isFormDirty) {
            saveForm(form.id, form.action, form.method);
        }
    }
    
    // Ctrl+Z للتراجع
    if (e.ctrlKey && e.key === 'z') {
        e.preventDefault();
        const form = document.querySelector('form[id]');
        if (form && isFormDirty) {
            undoChanges(form.id);
        }
    }
});
