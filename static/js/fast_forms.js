/*!
 * نظام النماذج السريع - Fast Forms System
 * معالجة فائقة السرعة لجميع أزرار الحفظ
 */

class FastFormProcessor {
    constructor() {
        this.processingForms = new Set();
        this.init();
    }

    init() {
        // معالجة جميع النماذج عند تحميل الصفحة
        document.addEventListener('DOMContentLoaded', () => {
            this.setupAllForms();
        });

        // معالجة النماذج المضافة ديناميكياً
        this.observeNewForms();
    }

    setupAllForms() {
        // البحث عن جميع النماذج
        const forms = document.querySelectorAll('form');
        forms.forEach(form => this.setupForm(form));
    }

    setupForm(form) {
        // تجنب الإعداد المتكرر
        if (form.dataset.fastFormSetup) return;
        form.dataset.fastFormSetup = 'true';

        // إضافة معالج الإرسال
        form.addEventListener('submit', (e) => {
            this.handleFormSubmit(e, form);
        });

        // إضافة معالج للأزرار
        const submitButtons = form.querySelectorAll('button[type="submit"], .save-btn');
        submitButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                this.handleButtonClick(e, button, form);
            });
        });
    }

    handleFormSubmit(e, form) {
        // منع الإرسال المتكرر
        if (this.processingForms.has(form)) {
            e.preventDefault();
            return;
        }

        // التحقق السريع من صحة النموذج
        if (!form.checkValidity()) {
            return; // السماح للمتصفح بإظهار رسائل التحقق
        }

        // إضافة النموذج للمعالجة
        this.processingForms.add(form);

        // معالجة الزر
        const submitButton = form.querySelector('button[type="submit"], .save-btn');
        if (submitButton) {
            this.processButton(submitButton, 'saving');
        }

        // إزالة النموذج من المعالجة بعد 3 ثوانٍ
        setTimeout(() => {
            this.processingForms.delete(form);
            if (submitButton) {
                this.resetButton(submitButton);
            }
        }, 3000);
    }

    handleButtonClick(e, button, form) {
        // منع النقر المتكرر
        if (button.disabled || this.processingForms.has(form)) {
            e.preventDefault();
            return;
        }

        // معالجة فورية للزر
        this.processButton(button, 'clicked');
    }

    processButton(button, state) {
        const originalText = button.dataset.originalText || button.innerHTML;
        button.dataset.originalText = originalText;

        switch (state) {
            case 'clicked':
                button.innerHTML = '<i class="fas fa-check"></i> تم';
                button.disabled = true;
                break;
            case 'saving':
                button.innerHTML = '<i class="fas fa-check text-success"></i> محفوظ';
                button.disabled = true;
                break;
            case 'success':
                button.innerHTML = '<i class="fas fa-check-circle text-success"></i> نجح';
                button.disabled = false;
                break;
            case 'error':
                button.innerHTML = '<i class="fas fa-times-circle text-danger"></i> خطأ';
                button.disabled = false;
                break;
        }

        // إعادة النص الأصلي بعد فترة قصيرة
        if (state !== 'clicked') {
            setTimeout(() => {
                this.resetButton(button);
            }, state === 'error' ? 2000 : 1500);
        }
    }

    resetButton(button) {
        const originalText = button.dataset.originalText;
        if (originalText) {
            button.innerHTML = originalText;
            button.disabled = false;
        }
    }

    observeNewForms() {
        // مراقبة النماذج الجديدة المضافة للصفحة
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                mutation.addedNodes.forEach((node) => {
                    if (node.nodeType === 1) { // Element node
                        // البحث عن النماذج في العقدة الجديدة
                        if (node.tagName === 'FORM') {
                            this.setupForm(node);
                        } else {
                            const forms = node.querySelectorAll && node.querySelectorAll('form');
                            if (forms) {
                                forms.forEach(form => this.setupForm(form));
                            }
                        }
                    }
                });
            });
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }

    // وظائف مساعدة عامة
    static showQuickMessage(message, type = 'success', duration = 2000) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `alert alert-${type} quick-message`;
        messageDiv.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
            min-width: 250px;
            animation: slideInRight 0.3s ease;
        `;
        messageDiv.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check' : 'times'}"></i>
            ${message}
        `;

        document.body.appendChild(messageDiv);

        setTimeout(() => {
            messageDiv.style.animation = 'slideOutRight 0.3s ease';
            setTimeout(() => {
                if (messageDiv.parentNode) {
                    messageDiv.parentNode.removeChild(messageDiv);
                }
            }, 300);
        }, duration);
    }

    // تحسين الأداء - إزالة التأخيرات غير الضرورية
    static removeDelays() {
        // إزالة جميع setTimeout و setInterval غير الضرورية
        const scripts = document.querySelectorAll('script');
        scripts.forEach(script => {
            if (script.innerHTML.includes('setTimeout') && 
                script.innerHTML.includes('loading') && 
                script.innerHTML.includes('10000')) {
                // تقليل التأخير من 10 ثوانٍ إلى ثانيتين
                script.innerHTML = script.innerHTML.replace(/10000/g, '2000');
            }
        });
    }

    // تحسين استجابة الأزرار
    static optimizeButtons() {
        const buttons = document.querySelectorAll('button[type="submit"], .save-btn');
        buttons.forEach(button => {
            // إزالة أي تأخيرات في CSS
            button.style.transition = 'all 0.1s ease';
            
            // تحسين الاستجابة
            button.addEventListener('mousedown', () => {
                button.style.transform = 'scale(0.98)';
            });
            
            button.addEventListener('mouseup', () => {
                button.style.transform = 'scale(1)';
            });
        });
    }
}

// تهيئة النظام
const fastFormProcessor = new FastFormProcessor();

// تحسينات إضافية
document.addEventListener('DOMContentLoaded', () => {
    FastFormProcessor.removeDelays();
    FastFormProcessor.optimizeButtons();
});

// إضافة أنماط CSS للرسائل السريعة
const quickMessageStyles = document.createElement('style');
quickMessageStyles.textContent = `
    @keyframes slideInRight {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes slideOutRight {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
    
    .quick-message {
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        font-weight: 500;
    }
    
    .quick-message i {
        margin-left: 8px;
    }
`;
document.head.appendChild(quickMessageStyles);

// تصدير للاستخدام العام
window.FastFormProcessor = FastFormProcessor;
