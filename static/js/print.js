// وظائف الطباعة للنظام المحاسبي

// وظيفة الطباعة العامة
function printPage(title = 'تقرير') {
    // إضافة رأس الطباعة
    addPrintHeader(title);
    
    // إضافة تاريخ الطباعة
    addPrintDate();
    
    // إضافة تذييل الطباعة
    addPrintFooter();
    
    // تطبيق أنماط الطباعة
    applyPrintStyles();
    
    // طباعة الصفحة
    window.print();
    
    // إزالة عناصر الطباعة بعد الانتهاء
    setTimeout(removePrintElements, 1000);
}

// إضافة رأس الطباعة
function addPrintHeader(title) {
    const header = document.createElement('div');
    header.className = 'print-header print-only';
    header.innerHTML = `
        <h1>نظام المحاسبة المتكامل</h1>
        <div class="company-info">
            <div>شركة المثال للتجارة</div>
            <div>ص.ب: 12345 - الرياض 11564 - المملكة العربية السعودية</div>
            <div>هاتف: 011-1234567 | فاكس: 011-1234568 | البريد: info@example.com</div>
        </div>
        <h2 style="margin-top: 20px; color: #333;">${title}</h2>
    `;
    
    document.body.insertBefore(header, document.body.firstChild);
}

// إضافة تاريخ الطباعة
function addPrintDate() {
    const dateDiv = document.createElement('div');
    dateDiv.className = 'print-date print-only';
    const now = new Date();
    const dateStr = now.toLocaleDateString('ar-SA', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
    dateDiv.innerHTML = `تاريخ الطباعة: ${dateStr}`;
    
    const content = document.querySelector('.content') || document.body;
    content.insertBefore(dateDiv, content.firstChild);
}

// إضافة تذييل الطباعة
function addPrintFooter() {
    const footer = document.createElement('div');
    footer.className = 'print-footer print-only';
    footer.innerHTML = `
        <div>نظام المحاسبة المتكامل - تم الإنشاء بواسطة النظام</div>
        <div>هذا التقرير تم إنشاؤه تلقائياً ولا يحتاج إلى توقيع</div>
    `;
    
    document.body.appendChild(footer);
}

// تطبيق أنماط الطباعة
function applyPrintStyles() {
    // إضافة فئات CSS للطباعة
    document.body.classList.add('printing');
    
    // إخفاء العناصر غير المرغوب فيها
    const elementsToHide = [
        '.sidebar',
        '.navbar-top', 
        '.btn:not(.print-btn)',
        '.dropdown',
        '.btn-group',
        '.search-filters',
        '.pagination'
    ];
    
    elementsToHide.forEach(selector => {
        const elements = document.querySelectorAll(selector);
        elements.forEach(el => el.classList.add('no-print'));
    });
}

// إزالة عناصر الطباعة
function removePrintElements() {
    const printElements = document.querySelectorAll('.print-only');
    printElements.forEach(el => el.remove());
    
    document.body.classList.remove('printing');
    
    const noPrintElements = document.querySelectorAll('.no-print');
    noPrintElements.forEach(el => el.classList.remove('no-print'));
}

// طباعة جدول محدد
function printTable(tableId, title = 'تقرير الجدول') {
    const table = document.getElementById(tableId);
    if (!table) {
        alert('لم يتم العثور على الجدول المطلوب');
        return;
    }
    
    // إنشاء نافذة جديدة للطباعة
    const printWindow = window.open('', '_blank');
    
    const printContent = `
        <!DOCTYPE html>
        <html lang="ar" dir="rtl">
        <head>
            <meta charset="UTF-8">
            <title>${title}</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
            <link rel="stylesheet" href="/static/css/print.css">
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .table { width: 100%; border-collapse: collapse; }
                .table th, .table td { border: 1px solid #000; padding: 8px; text-align: right; }
                .table th { background-color: #f0f0f0; font-weight: bold; }
                .print-header { text-align: center; margin-bottom: 30px; border-bottom: 2px solid #000; padding-bottom: 15px; }
                .print-date { text-align: left; margin-bottom: 20px; font-size: 12px; }
            </style>
        </head>
        <body>
            <div class="print-header">
                <h1>نظام المحاسبة المتكامل</h1>
                <h2>${title}</h2>
            </div>
            <div class="print-date">تاريخ الطباعة: ${new Date().toLocaleDateString('ar-SA')}</div>
            ${table.outerHTML}
            <div style="margin-top: 30px; text-align: center; font-size: 12px; border-top: 1px solid #000; padding-top: 10px;">
                نظام المحاسبة المتكامل - تم الإنشاء تلقائياً
            </div>
        </body>
        </html>
    `;
    
    printWindow.document.write(printContent);
    printWindow.document.close();
    
    setTimeout(() => {
        printWindow.print();
        printWindow.close();
    }, 500);
}

// طباعة فاتورة
function printInvoice(invoiceId) {
    const invoiceData = getInvoiceData(invoiceId);
    
    const printWindow = window.open('', '_blank');
    
    const invoiceHTML = `
        <!DOCTYPE html>
        <html lang="ar" dir="rtl">
        <head>
            <meta charset="UTF-8">
            <title>فاتورة رقم ${invoiceId}</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
            <link rel="stylesheet" href="/static/css/print.css">
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .invoice-header { display: flex; justify-content: space-between; margin-bottom: 30px; border-bottom: 2px solid #000; padding-bottom: 15px; }
                .company-info { text-align: right; }
                .invoice-info { text-align: left; }
                .customer-info { margin: 20px 0; padding: 15px; border: 1px solid #000; }
                .items-table { width: 100%; border-collapse: collapse; margin: 20px 0; }
                .items-table th, .items-table td { border: 1px solid #000; padding: 10px; text-align: right; }
                .items-table th { background-color: #f0f0f0; }
                .totals { width: 300px; margin-left: auto; margin-top: 20px; }
                .total-row { display: flex; justify-content: space-between; padding: 5px 0; border-bottom: 1px solid #ccc; }
                .grand-total { font-weight: bold; font-size: 16px; border-top: 2px solid #000; border-bottom: 2px solid #000; }
            </style>
        </head>
        <body>
            <div class="invoice-header">
                <div class="company-info">
                    <h2>شركة المثال للتجارة</h2>
                    <div>ص.ب: 12345 - الرياض 11564</div>
                    <div>هاتف: 011-1234567</div>
                    <div>الرقم الضريبي: 123456789</div>
                </div>
                <div class="invoice-info">
                    <h3>فاتورة ضريبية</h3>
                    <div>رقم الفاتورة: #INV-${invoiceId}</div>
                    <div>التاريخ: ${new Date().toLocaleDateString('ar-SA')}</div>
                </div>
            </div>
            
            <div class="customer-info">
                <strong>بيانات العميل:</strong><br>
                ${invoiceData.customerName}<br>
                ${invoiceData.customerAddress || 'العنوان غير محدد'}<br>
                ${invoiceData.customerPhone || 'الهاتف غير محدد'}
            </div>
            
            <table class="items-table">
                <thead>
                    <tr>
                        <th>الوصف</th>
                        <th>الكمية</th>
                        <th>السعر</th>
                        <th>المجموع</th>
                    </tr>
                </thead>
                <tbody>
                    ${invoiceData.items.map(item => `
                        <tr>
                            <td>${item.description}</td>
                            <td>${item.quantity}</td>
                            <td>${item.price.toFixed(2)} ر.س</td>
                            <td>${(item.quantity * item.price).toFixed(2)} ر.س</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
            
            <div class="totals">
                <div class="total-row">
                    <span>المجموع الفرعي:</span>
                    <span>${invoiceData.subtotal.toFixed(2)} ر.س</span>
                </div>
                <div class="total-row">
                    <span>ضريبة القيمة المضافة (15%):</span>
                    <span>${invoiceData.vat.toFixed(2)} ر.س</span>
                </div>
                <div class="total-row grand-total">
                    <span>المجموع الإجمالي:</span>
                    <span>${invoiceData.total.toFixed(2)} ر.س</span>
                </div>
            </div>
            
            <div style="margin-top: 50px; text-align: center; font-size: 12px;">
                <p>شكراً لتعاملكم معنا</p>
                <p>هذه فاتورة ضريبية صادرة إلكترونياً ولا تحتاج إلى توقيع</p>
            </div>
        </body>
        </html>
    `;
    
    printWindow.document.write(invoiceHTML);
    printWindow.document.close();
    
    setTimeout(() => {
        printWindow.print();
        printWindow.close();
    }, 500);
}

// الحصول على بيانات الفاتورة (مؤقت - يجب ربطه بقاعدة البيانات)
function getInvoiceData(invoiceId) {
    return {
        customerName: 'عميل تجريبي',
        customerAddress: 'الرياض، المملكة العربية السعودية',
        customerPhone: '0501234567',
        items: [
            { description: 'منتج تجريبي 1', quantity: 2, price: 100 },
            { description: 'منتج تجريبي 2', quantity: 1, price: 200 }
        ],
        subtotal: 400,
        vat: 60,
        total: 460
    };
}

// طباعة تقرير مخصص
function printCustomReport(data, title) {
    const printWindow = window.open('', '_blank');
    
    const reportHTML = `
        <!DOCTYPE html>
        <html lang="ar" dir="rtl">
        <head>
            <meta charset="UTF-8">
            <title>${title}</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
            <link rel="stylesheet" href="/static/css/print.css">
        </head>
        <body>
            <div class="print-header">
                <h1>نظام المحاسبة المتكامل</h1>
                <h2>${title}</h2>
                <div class="print-date">تاريخ الطباعة: ${new Date().toLocaleDateString('ar-SA')}</div>
            </div>
            
            <div class="report-content">
                ${data}
            </div>
            
            <div class="print-footer">
                <div>نظام المحاسبة المتكامل - تم الإنشاء تلقائياً</div>
            </div>
        </body>
        </html>
    `;
    
    printWindow.document.write(reportHTML);
    printWindow.document.close();
    
    setTimeout(() => {
        printWindow.print();
        printWindow.close();
    }, 500);
}

// طباعة قائمة العملاء
function printCustomersList() {
    printTable('customersTable', 'تقرير العملاء');
}

// طباعة قائمة الفواتير
function printInvoicesList() {
    printTable('invoicesTable', 'تقرير الفواتير');
}

// طباعة قائمة المنتجات
function printProductsList() {
    printTable('productsTable', 'تقرير المخزون');
}

// طباعة قائمة المصروفات
function printExpensesList() {
    printTable('expensesTable', 'تقرير المصروفات');
}

// طباعة قائمة الموردين
function printSuppliersList() {
    printTable('suppliersTable', 'تقرير الموردين');
}

// إعداد أزرار الطباعة
document.addEventListener('DOMContentLoaded', function() {
    // إضافة مستمعي الأحداث لأزرار الطباعة
    const printButtons = document.querySelectorAll('[data-print]');
    printButtons.forEach(button => {
        button.addEventListener('click', function() {
            const printType = this.getAttribute('data-print');
            const printTitle = this.getAttribute('data-print-title') || 'تقرير';
            
            switch(printType) {
                case 'page':
                    printPage(printTitle);
                    break;
                case 'table':
                    const tableId = this.getAttribute('data-table-id');
                    printTable(tableId, printTitle);
                    break;
                case 'invoice':
                    const invoiceId = this.getAttribute('data-invoice-id');
                    printInvoice(invoiceId);
                    break;
                case 'customers':
                    printCustomersList();
                    break;
                case 'invoices':
                    printInvoicesList();
                    break;
                case 'products':
                    printProductsList();
                    break;
                case 'expenses':
                    printExpensesList();
                    break;
                case 'suppliers':
                    printSuppliersList();
                    break;
                default:
                    printPage(printTitle);
            }
        });
    });
});
