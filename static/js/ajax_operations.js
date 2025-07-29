/**
 * نظام AJAX للعمليات السريعة
 * AJAX System for Fast Operations
 */

// إعدادات عامة للـ AJAX
const ajaxConfig = {
    timeout: 30000, // 30 ثانية
    retryAttempts: 3,
    retryDelay: 1000 // ثانية واحدة
};

// عرض loading indicator
function showLoading(element, message = 'جاري التحميل...') {
    if (element) {
        element.innerHTML = `
            <div class="d-flex align-items-center">
                <div class="spinner-border spinner-border-sm me-2" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                ${message}
            </div>
        `;
        element.disabled = true;
    }
}

// إخفاء loading indicator
function hideLoading(element, originalText = '') {
    if (element) {
        element.innerHTML = originalText;
        element.disabled = false;
    }
}

// عرض رسائل النجاح والخطأ
function showMessage(message, type = 'success', duration = 5000) {
    const alertClass = type === 'success' ? 'alert-success' : 'alert-danger';
    const icon = type === 'success' ? 'fas fa-check-circle' : 'fas fa-exclamation-triangle';
    
    const alertHtml = `
        <div class="alert ${alertClass} alert-dismissible fade show" role="alert">
            <i class="${icon} me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    // إضافة الرسالة إلى أعلى الصفحة
    const container = document.querySelector('.container-fluid') || document.body;
    const alertDiv = document.createElement('div');
    alertDiv.innerHTML = alertHtml;
    container.insertBefore(alertDiv.firstElementChild, container.firstElementChild);
    
    // إزالة الرسالة تلقائياً
    setTimeout(() => {
        const alert = container.querySelector('.alert');
        if (alert) {
            alert.remove();
        }
    }, duration);
}

// دالة AJAX عامة مع إعادة المحاولة
async function makeAjaxRequest(url, options = {}, retryCount = 0) {
    const defaultOptions = {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        },
        timeout: ajaxConfig.timeout
    };
    
    const finalOptions = { ...defaultOptions, ...options };
    
    try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), finalOptions.timeout);
        
        const response = await fetch(url, {
            ...finalOptions,
            signal: controller.signal
        });
        
        clearTimeout(timeoutId);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
            return await response.json();
        } else {
            return await response.text();
        }
        
    } catch (error) {
        if (retryCount < ajaxConfig.retryAttempts) {
            console.log(`محاولة ${retryCount + 1} فشلت، إعادة المحاولة...`);
            await new Promise(resolve => setTimeout(resolve, ajaxConfig.retryDelay));
            return makeAjaxRequest(url, options, retryCount + 1);
        }
        throw error;
    }
}

// حفظ النماذج بـ AJAX
async function submitFormAjax(form, successCallback = null, errorCallback = null) {
    const submitButton = form.querySelector('button[type="submit"]');
    const originalText = submitButton ? submitButton.innerHTML : '';
    
    try {
        if (submitButton) {
            showLoading(submitButton, 'جاري الحفظ...');
        }
        
        const formData = new FormData(form);
        const response = await makeAjaxRequest(form.action, {
            method: form.method || 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        });
        
        if (response.success) {
            showMessage(response.message || 'تم الحفظ بنجاح!', 'success');
            if (successCallback) {
                successCallback(response);
            }
        } else {
            throw new Error(response.message || 'حدث خطأ أثناء الحفظ');
        }
        
    } catch (error) {
        console.error('خطأ في إرسال النموذج:', error);
        showMessage(error.message || 'حدث خطأ أثناء الحفظ', 'error');
        if (errorCallback) {
            errorCallback(error);
        }
    } finally {
        if (submitButton) {
            hideLoading(submitButton, originalText);
        }
    }
}

// تحديث البيانات بـ AJAX
async function updateDataAjax(url, data, successMessage = 'تم التحديث بنجاح!') {
    try {
        const response = await makeAjaxRequest(url, {
            method: 'POST',
            body: JSON.stringify(data),
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            }
        });
        
        if (response.success) {
            showMessage(successMessage, 'success');
            return response;
        } else {
            throw new Error(response.message || 'حدث خطأ أثناء التحديث');
        }
        
    } catch (error) {
        console.error('خطأ في تحديث البيانات:', error);
        showMessage(error.message || 'حدث خطأ أثناء التحديث', 'error');
        throw error;
    }
}

// حذف العناصر بـ AJAX - نسخة سريعة
async function deleteItemAjax(url, itemName = 'العنصر') {
    // حذف سريع بدون تأكيد
    FastDeleteProcessor.showQuickMessage(`جاري حذف ${itemName}...`, 'warning', 1000);

    try {
        const response = await makeAjaxRequest(url, {
            method: 'DELETE',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        });

        if (response.success) {
            FastDeleteProcessor.showQuickMessage(response.message || `تم حذف ${itemName} بنجاح!`, 'success');
            return true;
        } else {
            throw new Error(response.message || 'حدث خطأ أثناء الحذف');
        }

    } catch (error) {
        console.error('خطأ في الحذف:', error);
        FastDeleteProcessor.showQuickMessage(error.message || `خطأ في حذف ${itemName}`, 'danger');
        return false;
    }
}

// تحميل البيانات بـ AJAX مع pagination
async function loadDataWithPagination(url, container, page = 1, append = false) {
    try {
        const loadingHtml = `
            <div class="text-center p-4">
                <div class="spinner-border" role="status">
                    <span class="visually-hidden">جاري التحميل...</span>
                </div>
                <p class="mt-2">جاري تحميل البيانات...</p>
            </div>
        `;
        
        if (!append) {
            container.innerHTML = loadingHtml;
        }
        
        const response = await makeAjaxRequest(`${url}?page=${page}&ajax=1`);
        
        if (response.success) {
            if (append) {
                container.insertAdjacentHTML('beforeend', response.html);
            } else {
                container.innerHTML = response.html;
            }
            
            // إضافة أزرار pagination إذا كانت متوفرة
            if (response.pagination) {
                addPaginationControls(container, response.pagination, url);
            }
            
            return response;
        } else {
            throw new Error(response.message || 'حدث خطأ في تحميل البيانات');
        }
        
    } catch (error) {
        console.error('خطأ في تحميل البيانات:', error);
        container.innerHTML = `
            <div class="alert alert-danger text-center">
                <i class="fas fa-exclamation-triangle me-2"></i>
                ${error.message || 'حدث خطأ في تحميل البيانات'}
                <button class="btn btn-sm btn-outline-danger ms-2" onclick="loadDataWithPagination('${url}', this.closest('.alert').parentElement)">
                    إعادة المحاولة
                </button>
            </div>
        `;
    }
}

// إضافة أزرار pagination
function addPaginationControls(container, pagination, baseUrl) {
    const paginationHtml = `
        <nav aria-label="Page navigation" class="mt-3">
            <ul class="pagination justify-content-center">
                ${pagination.has_prev ? `
                    <li class="page-item">
                        <a class="page-link" href="#" onclick="loadDataWithPagination('${baseUrl}', document.querySelector('[data-container]'), ${pagination.prev_num}); return false;">
                            السابق
                        </a>
                    </li>
                ` : ''}
                
                ${Array.from({length: pagination.pages}, (_, i) => i + 1).map(page => `
                    <li class="page-item ${page === pagination.page ? 'active' : ''}">
                        <a class="page-link" href="#" onclick="loadDataWithPagination('${baseUrl}', document.querySelector('[data-container]'), ${page}); return false;">
                            ${page}
                        </a>
                    </li>
                `).join('')}
                
                ${pagination.has_next ? `
                    <li class="page-item">
                        <a class="page-link" href="#" onclick="loadDataWithPagination('${baseUrl}', document.querySelector('[data-container]'), ${pagination.next_num}); return false;">
                            التالي
                        </a>
                    </li>
                ` : ''}
            </ul>
        </nav>
    `;
    
    container.insertAdjacentHTML('afterend', paginationHtml);
}

// البحث المباشر بـ AJAX
let searchTimeout;
function setupLiveSearch(searchInput, resultsContainer, searchUrl) {
    searchInput.addEventListener('input', function() {
        clearTimeout(searchTimeout);
        const query = this.value.trim();
        
        if (query.length < 2) {
            resultsContainer.innerHTML = '';
            return;
        }
        
        searchTimeout = setTimeout(async () => {
            try {
                resultsContainer.innerHTML = '<div class="text-center p-2"><div class="spinner-border spinner-border-sm"></div></div>';
                
                const response = await makeAjaxRequest(`${searchUrl}?q=${encodeURIComponent(query)}&ajax=1`);
                
                if (response.success) {
                    resultsContainer.innerHTML = response.html;
                } else {
                    resultsContainer.innerHTML = '<div class="text-muted p-2">لا توجد نتائج</div>';
                }
                
            } catch (error) {
                console.error('خطأ في البحث:', error);
                resultsContainer.innerHTML = '<div class="text-danger p-2">حدث خطأ في البحث</div>';
            }
        }, 300); // تأخير 300ms
    });
}

// تهيئة النظام عند تحميل الصفحة
document.addEventListener('DOMContentLoaded', function() {
    // تحويل النماذج إلى AJAX تلقائياً
    document.querySelectorAll('form[data-ajax="true"]').forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            submitFormAjax(this);
        });
    });
    
    // تهيئة البحث المباشر
    const searchInputs = document.querySelectorAll('[data-live-search]');
    searchInputs.forEach(input => {
        const resultsContainer = document.querySelector(input.dataset.resultsContainer);
        const searchUrl = input.dataset.searchUrl;
        if (resultsContainer && searchUrl) {
            setupLiveSearch(input, resultsContainer, searchUrl);
        }
    });
    
    console.log('نظام AJAX تم تهيئته بنجاح');
});
