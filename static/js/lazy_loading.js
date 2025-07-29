/**
 * نظام التحميل التدريجي للبيانات
 * Lazy Loading System for Data
 */

class LazyLoader {
    constructor(options = {}) {
        this.options = {
            threshold: 0.1,
            rootMargin: '50px',
            pageSize: 20,
            loadingText: 'جاري التحميل...',
            noMoreText: 'لا توجد بيانات أخرى',
            errorText: 'حدث خطأ في التحميل',
            retryText: 'إعادة المحاولة',
            ...options
        };
        
        this.currentPage = 1;
        this.isLoading = false;
        this.hasMore = true;
        this.totalLoaded = 0;
        
        this.setupIntersectionObserver();
    }

    // إعداد مراقب التقاطع
    setupIntersectionObserver() {
        this.observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting && !this.isLoading && this.hasMore) {
                    this.loadMore();
                }
            });
        }, {
            threshold: this.options.threshold,
            rootMargin: this.options.rootMargin
        });
    }

    // تهيئة التحميل التدريجي لجدول
    initTable(tableId, endpoint, columns) {
        this.tableId = tableId;
        this.endpoint = endpoint;
        this.columns = columns;
        this.table = document.getElementById(tableId);
        
        if (!this.table) {
            console.error(`Table with ID ${tableId} not found`);
            return;
        }

        this.tbody = this.table.querySelector('tbody');
        if (!this.tbody) {
            this.tbody = document.createElement('tbody');
            this.table.appendChild(this.tbody);
        }

        // إنشاء عنصر التحميل
        this.createLoadingElement();
        
        // تحميل البيانات الأولى
        this.loadMore();
    }

    // إنشاء عنصر التحميل
    createLoadingElement() {
        this.loadingElement = document.createElement('tr');
        this.loadingElement.className = 'lazy-loading-row';
        this.loadingElement.innerHTML = `
            <td colspan="${this.columns.length}" class="text-center p-3">
                <div class="d-flex align-items-center justify-content-center">
                    <div class="spinner-border spinner-border-sm me-2" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    <span class="loading-text">${this.options.loadingText}</span>
                </div>
            </td>
        `;
        
        this.tbody.appendChild(this.loadingElement);
        this.observer.observe(this.loadingElement);
    }

    // تحميل المزيد من البيانات
    async loadMore() {
        if (this.isLoading || !this.hasMore) return;
        
        this.isLoading = true;
        this.showLoading();

        try {
            const response = await fetch(`${this.endpoint}?page=${this.currentPage}&size=${this.options.pageSize}`, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            
            if (data.success) {
                this.renderData(data.data);
                this.currentPage++;
                this.totalLoaded += data.data.length;
                
                // التحقق من وجود المزيد
                this.hasMore = data.has_more || data.data.length === this.options.pageSize;
                
                if (!this.hasMore) {
                    this.showNoMore();
                }
            } else {
                throw new Error(data.message || 'فشل في تحميل البيانات');
            }

        } catch (error) {
            console.error('Lazy loading error:', error);
            this.showError(error.message);
        } finally {
            this.isLoading = false;
        }
    }

    // عرض البيانات
    renderData(data) {
        const fragment = document.createDocumentFragment();
        
        data.forEach(item => {
            const row = this.createRow(item);
            fragment.appendChild(row);
        });

        // إدراج البيانات قبل عنصر التحميل
        this.tbody.insertBefore(fragment, this.loadingElement);
    }

    // إنشاء صف جدول
    createRow(item) {
        const row = document.createElement('tr');
        row.className = 'lazy-loaded-row';
        
        this.columns.forEach(column => {
            const cell = document.createElement('td');
            
            if (typeof column.render === 'function') {
                cell.innerHTML = column.render(item[column.key], item);
            } else {
                cell.textContent = item[column.key] || '';
            }
            
            if (column.className) {
                cell.className = column.className;
            }
            
            row.appendChild(cell);
        });

        return row;
    }

    // عرض حالة التحميل
    showLoading() {
        const loadingText = this.loadingElement.querySelector('.loading-text');
        const spinner = this.loadingElement.querySelector('.spinner-border');
        
        loadingText.textContent = this.options.loadingText;
        spinner.style.display = 'inline-block';
        this.loadingElement.style.display = 'table-row';
    }

    // عرض رسالة عدم وجود المزيد
    showNoMore() {
        const loadingText = this.loadingElement.querySelector('.loading-text');
        const spinner = this.loadingElement.querySelector('.spinner-border');
        
        loadingText.textContent = this.options.noMoreText;
        spinner.style.display = 'none';
        
        // إخفاء العنصر بعد ثانيتين
        setTimeout(() => {
            this.loadingElement.style.display = 'none';
            this.observer.unobserve(this.loadingElement);
        }, 2000);
    }

    // عرض رسالة الخطأ
    showError(message) {
        const loadingText = this.loadingElement.querySelector('.loading-text');
        const spinner = this.loadingElement.querySelector('.spinner-border');
        
        loadingText.innerHTML = `
            <span class="text-danger">${this.options.errorText}: ${message}</span>
            <button class="btn btn-sm btn-outline-primary ms-2" onclick="this.closest('.lazy-loader').retry()">
                ${this.options.retryText}
            </button>
        `;
        spinner.style.display = 'none';
    }

    // إعادة المحاولة
    retry() {
        this.isLoading = false;
        this.loadMore();
    }

    // إعادة تعيين التحميل
    reset() {
        this.currentPage = 1;
        this.isLoading = false;
        this.hasMore = true;
        this.totalLoaded = 0;
        
        // مسح البيانات الموجودة
        const loadedRows = this.tbody.querySelectorAll('.lazy-loaded-row');
        loadedRows.forEach(row => row.remove());
        
        // إعادة إظهار عنصر التحميل
        this.loadingElement.style.display = 'table-row';
        this.observer.observe(this.loadingElement);
        
        // تحميل البيانات الأولى
        this.loadMore();
    }

    // تدمير المثيل
    destroy() {
        if (this.observer) {
            this.observer.disconnect();
        }
        
        if (this.loadingElement) {
            this.loadingElement.remove();
        }
    }
}

// فئة التحميل التدريجي للبطاقات
class LazyCardLoader {
    constructor(containerId, endpoint, cardTemplate, options = {}) {
        this.containerId = containerId;
        this.endpoint = endpoint;
        this.cardTemplate = cardTemplate;
        this.options = {
            pageSize: 12,
            loadingText: 'جاري التحميل...',
            noMoreText: 'لا توجد بيانات أخرى',
            ...options
        };
        
        this.currentPage = 1;
        this.isLoading = false;
        this.hasMore = true;
        
        this.init();
    }

    init() {
        this.container = document.getElementById(this.containerId);
        if (!this.container) {
            console.error(`Container with ID ${this.containerId} not found`);
            return;
        }

        this.createLoadingElement();
        this.setupScrollListener();
        this.loadMore();
    }

    createLoadingElement() {
        this.loadingElement = document.createElement('div');
        this.loadingElement.className = 'text-center p-4 lazy-loading-cards';
        this.loadingElement.innerHTML = `
            <div class="spinner-border" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <div class="mt-2">${this.options.loadingText}</div>
        `;
        
        this.container.appendChild(this.loadingElement);
    }

    setupScrollListener() {
        window.addEventListener('scroll', () => {
            if (this.isNearBottom() && !this.isLoading && this.hasMore) {
                this.loadMore();
            }
        });
    }

    isNearBottom() {
        return window.innerHeight + window.scrollY >= document.body.offsetHeight - 1000;
    }

    async loadMore() {
        if (this.isLoading || !this.hasMore) return;
        
        this.isLoading = true;

        try {
            const response = await fetch(`${this.endpoint}?page=${this.currentPage}&size=${this.options.pageSize}`, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            const data = await response.json();
            
            if (data.success) {
                this.renderCards(data.data);
                this.currentPage++;
                this.hasMore = data.has_more || data.data.length === this.options.pageSize;
                
                if (!this.hasMore) {
                    this.showNoMore();
                }
            }

        } catch (error) {
            console.error('Lazy card loading error:', error);
        } finally {
            this.isLoading = false;
        }
    }

    renderCards(data) {
        const fragment = document.createDocumentFragment();
        
        data.forEach(item => {
            const cardElement = document.createElement('div');
            cardElement.innerHTML = this.cardTemplate(item);
            fragment.appendChild(cardElement.firstElementChild);
        });

        this.container.insertBefore(fragment, this.loadingElement);
    }

    showNoMore() {
        this.loadingElement.innerHTML = `
            <div class="text-muted">${this.options.noMoreText}</div>
        `;
        
        setTimeout(() => {
            this.loadingElement.style.display = 'none';
        }, 2000);
    }
}

// دوال مساعدة للاستخدام السريع
window.LazyLoader = LazyLoader;
window.LazyCardLoader = LazyCardLoader;

// تهيئة التحميل التدريجي للجداول الموجودة
document.addEventListener('DOMContentLoaded', function() {
    // البحث عن الجداول التي تحتاج تحميل تدريجي
    document.querySelectorAll('[data-lazy-table]').forEach(table => {
        const endpoint = table.dataset.lazyEndpoint;
        const columns = JSON.parse(table.dataset.lazyColumns || '[]');
        
        if (endpoint && columns.length > 0) {
            const loader = new LazyLoader();
            loader.initTable(table.id, endpoint, columns);
            
            // حفظ المرجع للاستخدام لاحقاً
            table.lazyLoader = loader;
        }
    });

    console.log('نظام التحميل التدريجي تم تهيئته بنجاح');
});
