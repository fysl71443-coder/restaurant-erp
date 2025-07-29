/**
 * نظام الحذف السريع - FastDeleteProcessor
 * يوفر حذف فائق السرعة بدون نوافذ تأكيد مزعجة
 */

class FastDeleteProcessor {
    constructor() {
        this.deletingItems = new Set();
        this.init();
    }

    init() {
        this.setupDeleteHandlers();
        this.optimizeDeleteButtons();
        console.log('✅ نظام الحذف السريع تم تهيئته بنجاح');
    }

    // إعداد معالجات الحذف التلقائية
    setupDeleteHandlers() {
        document.addEventListener('click', (e) => {
            const deleteBtn = e.target.closest('.delete-btn, [onclick*="delete"], [onclick*="confirmDelete"], [href*="delete"]');
            if (deleteBtn) {
                e.preventDefault();
                this.handleDeleteClick(deleteBtn);
            }
        });
    }

    // معالجة النقر على زر الحذف
    handleDeleteClick(button) {
        // منع الحذف المتكرر
        if (this.deletingItems.has(button)) {
            return;
        }

        // استخراج معلومات الحذف
        const deleteInfo = this.extractDeleteInfo(button);
        
        // تنفيذ الحذف السريع
        this.executeQuickDelete(button, deleteInfo);
    }

    // استخراج معلومات الحذف من الزر
    extractDeleteInfo(button) {
        const onclick = button.getAttribute('onclick') || '';
        const href = button.getAttribute('href') || '';
        
        // استخراج ID من onclick
        let itemId = null;
        let itemType = 'item';
        let itemName = 'العنصر';

        // البحث عن ID في onclick
        const onclickMatch = onclick.match(/confirmDelete\(([^,)]+)/);
        if (onclickMatch) {
            itemId = onclickMatch[1].replace(/['"]/g, '');
        }

        // البحث عن ID في href
        const hrefMatch = href.match(/delete_(\w+)\/(\d+)/);
        if (hrefMatch) {
            itemType = hrefMatch[1];
            itemId = hrefMatch[2];
        }

        // استخراج اسم العنصر من onclick
        const nameMatch = onclick.match(/confirmDelete\([^,]+,\s*['"](.*?)['"]/);
        if (nameMatch) {
            itemName = nameMatch[1];
        }

        return {
            id: itemId,
            type: itemType,
            name: itemName,
            url: href || this.buildDeleteUrl(itemType, itemId)
        };
    }

    // بناء رابط الحذف
    buildDeleteUrl(type, id) {
        return `/delete_${type}/${id}`;
    }

    // تنفيذ الحذف السريع
    executeQuickDelete(button, deleteInfo) {
        // إضافة الزر للقائمة المعالجة
        this.deletingItems.add(button);

        // تغيير حالة الزر فوراً
        this.updateButtonState(button, 'deleting');

        // عرض رسالة سريعة
        this.showQuickMessage(`جاري حذف ${deleteInfo.name}...`, 'warning', 1000);

        // تنفيذ الحذف
        setTimeout(() => {
            this.performDelete(button, deleteInfo);
        }, 500); // تأخير قصير للتأثير البصري
    }

    // تنفيذ عملية الحذف
    performDelete(button, deleteInfo) {
        if (deleteInfo.url) {
            // إذا كان هناك رابط مباشر
            window.location.href = deleteInfo.url;
        } else {
            // البحث عن نموذج الحذف
            const deleteForm = document.querySelector('#deleteForm, [id*="delete"]');
            if (deleteForm) {
                deleteForm.action = deleteInfo.url;
                deleteForm.submit();
            } else {
                // حذف مباشر عبر AJAX
                this.deleteViaAjax(button, deleteInfo);
            }
        }
    }

    // حذف عبر AJAX
    async deleteViaAjax(button, deleteInfo) {
        try {
            const response = await fetch(deleteInfo.url, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            if (response.ok) {
                this.updateButtonState(button, 'deleted');
                this.showQuickMessage(`تم حذف ${deleteInfo.name} بنجاح!`, 'success');
                
                // إزالة العنصر من الجدول
                const row = button.closest('tr, .card, .list-item');
                if (row) {
                    row.style.transition = 'all 0.3s ease';
                    row.style.opacity = '0';
                    setTimeout(() => row.remove(), 300);
                }
            } else {
                throw new Error('فشل في الحذف');
            }
        } catch (error) {
            this.updateButtonState(button, 'error');
            this.showQuickMessage(`خطأ في حذف ${deleteInfo.name}`, 'danger');
        } finally {
            this.deletingItems.delete(button);
        }
    }

    // تحديث حالة الزر
    updateButtonState(button, state) {
        const states = {
            deleting: {
                icon: 'fas fa-spinner fa-spin',
                text: 'جاري الحذف...',
                class: 'btn-warning'
            },
            deleted: {
                icon: 'fas fa-check',
                text: 'تم الحذف',
                class: 'btn-success'
            },
            error: {
                icon: 'fas fa-exclamation-triangle',
                text: 'خطأ',
                class: 'btn-danger'
            }
        };

        const stateConfig = states[state];
        if (stateConfig) {
            // تحديث الأيقونة والنص
            const icon = button.querySelector('i');
            if (icon) {
                icon.className = stateConfig.icon;
            }

            const textNode = button.childNodes[button.childNodes.length - 1];
            if (textNode && textNode.nodeType === Node.TEXT_NODE) {
                textNode.textContent = ` ${stateConfig.text}`;
            }

            // تحديث الفئة
            button.className = button.className.replace(/btn-\w+/, stateConfig.class);
            button.disabled = true;
        }
    }

    // عرض رسالة سريعة
    showQuickMessage(message, type = 'info', duration = 3000) {
        // إنشاء عنصر الرسالة
        const messageEl = document.createElement('div');
        messageEl.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        messageEl.style.cssText = `
            top: 20px;
            right: 20px;
            z-index: 9999;
            min-width: 300px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            border: none;
            border-radius: 8px;
        `;
        
        messageEl.innerHTML = `
            <i class="fas fa-${this.getIconForType(type)} me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        // إضافة الرسالة للصفحة
        document.body.appendChild(messageEl);

        // إزالة الرسالة تلقائياً
        setTimeout(() => {
            if (messageEl.parentNode) {
                messageEl.remove();
            }
        }, duration);
    }

    // الحصول على أيقونة حسب نوع الرسالة
    getIconForType(type) {
        const icons = {
            success: 'check-circle',
            danger: 'exclamation-triangle',
            warning: 'exclamation-circle',
            info: 'info-circle'
        };
        return icons[type] || 'info-circle';
    }

    // تحسين أزرار الحذف
    optimizeDeleteButtons() {
        const deleteButtons = document.querySelectorAll('.delete-btn, [onclick*="delete"], [href*="delete"]');
        deleteButtons.forEach(button => {
            // إزالة أي تأخيرات في CSS
            button.style.transition = 'all 0.2s ease';
            
            // تحسين الاستجابة
            button.addEventListener('mousedown', () => {
                button.style.transform = 'scale(0.95)';
            });
            
            button.addEventListener('mouseup', () => {
                button.style.transform = 'scale(1)';
            });

            // إضافة تأثير hover
            button.addEventListener('mouseenter', () => {
                if (!button.disabled) {
                    button.style.boxShadow = '0 2px 8px rgba(220, 53, 69, 0.3)';
                }
            });

            button.addEventListener('mouseleave', () => {
                button.style.boxShadow = 'none';
            });
        });
    }

    // إزالة نوافذ التأكيد القديمة
    static removeOldConfirmations() {
        // إزالة جميع استدعاءات confirm()
        const scripts = document.querySelectorAll('script');
        scripts.forEach(script => {
            if (script.innerHTML.includes('confirm(')) {
                // استبدال confirm بـ true لتجاوز التأكيد
                script.innerHTML = script.innerHTML.replace(/if\s*\(\s*confirm\([^)]+\)\s*\)/g, 'if (true)');
            }
        });

        // إزالة معالجات التأكيد من base.html
        const deleteConfirmHandlers = document.querySelectorAll('[onclick*="confirm"]');
        deleteConfirmHandlers.forEach(handler => {
            const onclick = handler.getAttribute('onclick');
            if (onclick && onclick.includes('confirm')) {
                // إزالة التأكيد من onclick
                const newOnclick = onclick.replace(/if\s*\(\s*confirm\([^)]+\)\s*\)\s*{?/, '');
                handler.setAttribute('onclick', newOnclick.replace(/}?$/, ''));
            }
        });
    }

    // دالة static للوصول السريع
    static showQuickMessage(message, type = 'info', duration = 3000) {
        if (window.fastDeleteProcessor) {
            window.fastDeleteProcessor.showQuickMessage(message, type, duration);
        } else {
            // إنشاء رسالة مؤقتة إذا لم يكن النظام جاهز
            const messageEl = document.createElement('div');
            messageEl.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
            messageEl.style.cssText = `
                top: 20px;
                right: 20px;
                z-index: 9999;
                min-width: 300px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                border: none;
                border-radius: 8px;
                font-weight: 500;
            `;
            messageEl.innerHTML = `
                <div class="d-flex align-items-center">
                    <i class="fas fa-info-circle me-2"></i>
                    <span>${message}</span>
                </div>
            `;

            document.body.appendChild(messageEl);

            setTimeout(() => {
                messageEl.classList.remove('show');
                setTimeout(() => messageEl.remove(), 150);
            }, duration);
        }
    }
}

// تهيئة النظام
const fastDeleteProcessor = new FastDeleteProcessor();

// تحسينات إضافية
document.addEventListener('DOMContentLoaded', () => {
    FastDeleteProcessor.removeOldConfirmations();
    console.log('🗑️ نظام الحذف السريع جاهز للعمل!');
});

// تصدير للاستخدام العام
window.FastDeleteProcessor = FastDeleteProcessor;
window.fastDeleteProcessor = fastDeleteProcessor;
