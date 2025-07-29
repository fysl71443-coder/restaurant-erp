from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from database import db, init_db, Customer, Invoice, Supplier, Product, Expense, Employee, Attendance, Payroll, Leave, PurchaseInvoice, Payment, User, SystemSettings, configure_db_optimizations
from datetime import datetime, timezone
import logging
from functools import wraps
from performance_optimizations import (
    cache_result, measure_performance, optimize_db_query,
    get_cached_analytics_data, invalidate_analytics_cache,
    optimize_pagination, get_optimized_monthly_data, app_cache
)
from background_tasks import (
    submit_task, get_task_status, get_task_result,
    generate_comprehensive_financial_report, calculate_employee_statistics,
    cleanup_old_data, initialize_background_tasks, shutdown_background_tasks
)

app = Flask(__name__)

# Configure database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///accounting_system.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key-here-change-in-production'  # للرسائل المؤقتة وFlask-Login

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'يرجى تسجيل الدخول للوصول لهذه الصفحة.'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Initialize database
init_db(app)

# إضافة datetime إلى سياق القوالب
@app.context_processor
def inject_datetime():
    return {'datetime': datetime}

# دالة للتحقق من الصلاحيات
def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('login'))
            if not current_user.has_permission(permission):
                flash('ليس لديك صلاحية للوصول لهذه الصفحة.', 'error')
                return redirect(url_for('home'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# دالة للتحقق من دور المستخدم
def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('login'))
            if current_user.role != role and current_user.role != 'admin':
                flash('ليس لديك صلاحية للوصول لهذه الصفحة.', 'error')
                return redirect(url_for('home'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Routes لتسجيل الدخول والخروج
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = bool(request.form.get('remember'))

        if not username or not password:
            flash('يرجى إدخال اسم المستخدم وكلمة المرور.', 'error')
            return render_template('login.html')

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            if not user.is_active:
                flash('حسابك غير مفعل. يرجى الاتصال بالمدير.', 'error')
                return render_template('login.html')

            login_user(user, remember=remember)
            user.last_login = datetime.now(timezone.utc)
            db.session.commit()

            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)

            flash(f'مرحباً {user.full_name}!', 'success')
            return redirect(url_for('home'))
        else:
            flash('اسم المستخدم أو كلمة المرور غير صحيحة.', 'error')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('تم تسجيل الخروج بنجاح.', 'info')
    return redirect(url_for('login'))

@app.route('/')
@login_required
def home():
    try:
        # إحصائيات شاملة للصفحة الرئيسية
        total_customers = Customer.query.count()
        total_invoices = Invoice.query.count()
        total_sales = db.session.query(db.func.sum(Invoice.total_amount)).scalar() or 0
        total_purchases = db.session.query(db.func.sum(PurchaseInvoice.total_amount)).scalar() or 0
        net_profit = total_sales - total_purchases

        return render_template('index.html',
                             total_customers=total_customers,
                             total_invoices=total_invoices,
                             total_sales=total_sales,
                             total_purchases=total_purchases,
                             net_profit=net_profit)
    except Exception as e:
        # معالجة الخطأ وعرض رسالة مناسبة
        logger.error(f"خطأ في تحميل البيانات الرئيسية: {str(e)}")
        flash('حدث خطأ أثناء تحميل البيانات. يرجى المحاولة لاحقًا.', 'error')
        return render_template('index.html',
                         total_customers=0,
                         total_invoices=0,
                         total_sales=0,
                         total_purchases=0,
                         net_profit=0)

@app.route('/dashboard')
def dashboard():
    """لوحة التحكم - إعادة توجيه للصفحة الرئيسية"""
    try:
        return redirect(url_for('index'))
    except Exception:
        return redirect('/')

@app.route('/sales')
def sales():
    try:
        # جلب إحصائيات المبيعات
        from datetime import datetime

        # فواتير المبيعات - مع معالجة الأخطاء
        try:
            sales_invoices = Invoice.query.filter_by(invoice_type='sales').all()
        except:
            # إذا فشل، اجلب جميع الفواتير
            sales_invoices = Invoice.query.all()

        if not sales_invoices:
            # إذا لم توجد فواتير، اعرض جميع الفواتير
            sales_invoices = Invoice.query.all()

        # حساب الإحصائيات
        today = datetime.now().date()
        month_start = today.replace(day=1)

        # مبيعات اليوم
        today_sales = 0
        month_sales = 0

        for invoice in sales_invoices:
            if invoice.date and invoice.total_amount:
                if invoice.date.date() == today:
                    today_sales += invoice.total_amount
                if invoice.date.date() >= month_start:
                    month_sales += invoice.total_amount

        # عدد الفواتير
        total_invoices = len(sales_invoices)

        # إجمالي المبيعات
        total_sales = sum(invoice.total_amount for invoice in sales_invoices if invoice.total_amount)

        # متوسط الفاتورة
        avg_invoice = total_sales / total_invoices if total_invoices > 0 else 0

        # آخر الفواتير
        recent_invoices = Invoice.query.order_by(Invoice.date.desc()).limit(10).all()

        return render_template('sales.html',
                             invoices=recent_invoices,
                             total_sales=total_sales,
                             month_sales=month_sales,
                             total_invoices=total_invoices,
                             avg_invoice=avg_invoice)
    except Exception as e:
        # في حالة حدوث خطأ، اعرض صفحة فارغة
        logger.error(f"خطأ في تحميل بيانات المبيعات: {str(e)}")
        return render_template('sales.html',
                             invoices=[],
                             total_sales=0,
                             month_sales=0,
                             total_invoices=0,
                             avg_invoice=0)

@app.route('/purchases')
@login_required
def purchases():
    try:
        # جلب إحصائيات المشتريات
        from datetime import datetime

        # جلب جميع فواتير المشتريات
        purchase_invoices = PurchaseInvoice.query.all()

        # حساب إجمالي المشتريات
        total_purchases = db.session.query(db.func.sum(PurchaseInvoice.total_amount)).scalar() or 0

        # عدد الموردين
        total_suppliers = Supplier.query.count()

        # عدد فواتير المشتريات
        total_purchase_invoices = PurchaseInvoice.query.count()

        # متوسط الشراء
        avg_purchase = total_purchases / total_purchase_invoices if total_purchase_invoices > 0 else 0

        # جلب الموردين مع حساب إجمالي مشترياتهم
        suppliers = []
        for supplier in Supplier.query.all():
            supplier_purchases = db.session.query(db.func.sum(PurchaseInvoice.total_amount)).filter_by(supplier_id=supplier.id).scalar() or 0
            last_purchase = PurchaseInvoice.query.filter_by(supplier_id=supplier.id).order_by(PurchaseInvoice.date.desc()).first()

            supplier.total_purchases = supplier_purchases
            supplier.last_purchase_date = last_purchase.date.strftime('%Y-%m-%d') if last_purchase and last_purchase.date else 'لا توجد'
            suppliers.append(supplier)

        # ترتيب الموردين حسب إجمالي المشتريات
        suppliers.sort(key=lambda x: x.total_purchases, reverse=True)

        # آخر فواتير المشتريات
        recent_purchase_invoices = PurchaseInvoice.query.order_by(PurchaseInvoice.date.desc()).limit(10).all()

        return render_template('purchases.html',
                             total_purchases=total_purchases,
                             total_suppliers=total_suppliers,
                             total_purchase_invoices=total_purchase_invoices,
                             avg_purchase=avg_purchase,
                             suppliers=suppliers,
                             recent_purchase_invoices=recent_purchase_invoices)
    except Exception as e:
        # في حالة حدوث خطأ، اعرض صفحة بقيم افتراضية
        logger.error(f"خطأ في تحميل بيانات المشتريات: {str(e)}")
        return render_template('purchases.html',
                             total_purchases=0,
                             total_suppliers=0,
                             total_purchase_invoices=0,
                             avg_purchase=0,
                             suppliers=[],
                             recent_purchase_invoices=[])

@app.route('/expenses')
def expenses():
    try:
        all_expenses = Expense.query.order_by(Expense.date.desc()).all()
        return render_template('expenses.html', expenses=all_expenses)
    except Exception as e:
        logger.error(f"خطأ في تحميل المصروفات: {str(e)}")
        return render_template('expenses.html', expenses=[])

@app.route('/inventory')
def inventory():
    try:
        all_products = Product.query.all()
        return render_template('inventory.html', products=all_products)
    except Exception as e:
        logger.error(f"خطأ في تحميل المخزون: {str(e)}")
        return render_template('inventory.html', products=[])

@app.route('/analytics')
@login_required
@measure_performance
def analytics():
    try:
        from datetime import datetime, timedelta
        import calendar

        # الحصول على التاريخ الحالي
        now = datetime.now()
        current_year = now.year
        current_month = now.month

        # محاولة الحصول على البيانات من الـ cache
        cache_key = f"analytics_data:{current_year}:{current_month}"
        cached_data = app_cache.get(cache_key)

        if cached_data:
            return render_template('analytics.html', **cached_data)

        # إحصائيات المبيعات (محسنة)
        sales_query = db.session.query(
            db.func.sum(Invoice.total_amount).label('total'),
            db.func.count(Invoice.id).label('count')
        ).first()

        total_sales = float(sales_query.total or 0)
        sales_count = sales_query.count or 0

        # إحصائيات المشتريات (محسنة)
        purchases_query = db.session.query(
            db.func.sum(PurchaseInvoice.total_amount).label('total'),
            db.func.count(PurchaseInvoice.id).label('count')
        ).first()

        total_purchases = float(purchases_query.total or 0)
        purchases_count = purchases_query.count or 0

        # صافي الربح
        net_profit = total_sales - total_purchases
        profit_margin = (net_profit / total_sales * 100) if total_sales > 0 else 0

        # إحصائيات العملاء والموردين (محسنة)
        counts_query = db.session.query(
            db.func.count(Customer.id.distinct()).label('customers'),
            db.func.count(Supplier.id.distinct()).label('suppliers')
        ).first()

        customers_count = counts_query.customers or 0
        suppliers_count = counts_query.suppliers or 0

        # بيانات المبيعات الشهرية للعام الحالي (محسنة)
        monthly_data = get_optimized_monthly_data(current_year)
        monthly_sales = monthly_data['sales']
        monthly_purchases = monthly_data['purchases']
        months_labels = [calendar.month_name[i] for i in range(1, 13)]

        # أفضل العملاء (محسن)
        top_customers_query = db.session.query(
            Customer.name,
            db.func.sum(Invoice.total_amount).label('total'),
            db.func.count(Invoice.id).label('invoices_count')
        ).join(Invoice).group_by(Customer.id, Customer.name).order_by(
            db.func.sum(Invoice.total_amount).desc()
        ).limit(5).all()

        top_customers = [
            {
                'name': row.name,
                'total': float(row.total or 0),
                'invoices_count': row.invoices_count or 0
            }
            for row in top_customers_query
        ]

        # أفضل الموردين (محسن)
        top_suppliers_query = db.session.query(
            Supplier.name,
            db.func.sum(PurchaseInvoice.total_amount).label('total'),
            db.func.count(PurchaseInvoice.id).label('invoices_count')
        ).join(PurchaseInvoice).group_by(Supplier.id, Supplier.name).order_by(
            db.func.sum(PurchaseInvoice.total_amount).desc()
        ).limit(5).all()

        top_suppliers = [
            {
                'name': row.name,
                'total': float(row.total or 0),
                'invoices_count': row.invoices_count or 0
            }
            for row in top_suppliers_query
        ]

        # إحصائيات الأسبوع الماضي مقابل هذا الأسبوع
        week_ago = now - timedelta(days=7)
        two_weeks_ago = now - timedelta(days=14)

        this_week_sales = db.session.query(db.func.sum(Invoice.total_amount)).filter(
            Invoice.date >= week_ago
        ).scalar() or 0

        last_week_sales = db.session.query(db.func.sum(Invoice.total_amount)).filter(
            Invoice.date >= two_weeks_ago,
            Invoice.date < week_ago
        ).scalar() or 0

        # نسبة التغيير الأسبوعية
        weekly_change = ((this_week_sales - last_week_sales) / last_week_sales * 100) if last_week_sales > 0 else 0

        # إعداد البيانات للـ template
        template_data = {
            'total_sales': total_sales,
            'total_purchases': total_purchases,
            'net_profit': net_profit,
            'profit_margin': profit_margin,
            'sales_count': sales_count,
            'purchases_count': purchases_count,
            'customers_count': customers_count,
            'suppliers_count': suppliers_count,
            'monthly_sales': monthly_sales,
            'monthly_purchases': monthly_purchases,
            'months_labels': months_labels,
            'top_customers': top_customers,
            'top_suppliers': top_suppliers,
            'this_week_sales': this_week_sales,
            'weekly_change': weekly_change
        }

        # حفظ البيانات في الـ cache لمدة 10 دقائق
        app_cache.set(cache_key, template_data, 600)

        return render_template('analytics.html', **template_data)
    except Exception as e:
        logger.error(f"خطأ في تحميل بيانات التحليلات: {str(e)}")
        return render_template('analytics.html',
                             total_sales=0,
                             total_purchases=0,
                             net_profit=0,
                             profit_margin=0,
                             sales_count=0,
                             purchases_count=0,
                             customers_count=0,
                             suppliers_count=0,
                             monthly_sales=[0]*12,
                             monthly_purchases=[0]*12,
                             months_labels=list(calendar.month_name)[1:],
                             top_customers=[],
                             top_suppliers=[],
                             this_week_sales=0,
                             weekly_change=0)

@app.route('/vat')
@login_required
def vat():
    try:
        # حساب ضريبة القيمة المضافة للمبيعات والمشتريات
        vat_rate = 0.15  # 15% ضريبة القيمة المضافة في السعودية

        # إجمالي المبيعات وضريبة المبيعات
        total_sales = db.session.query(db.func.sum(Invoice.total_amount)).scalar() or 0
        sales_vat = total_sales * vat_rate

        # إجمالي المشتريات وضريبة المشتريات
        total_purchases = db.session.query(db.func.sum(PurchaseInvoice.total_amount)).scalar() or 0
        purchases_vat = total_purchases * vat_rate

        # صافي ضريبة القيمة المضافة (المستحقة - المدفوعة)
        net_vat = sales_vat - purchases_vat

        # بيانات شهرية لضريبة القيمة المضافة
        from datetime import datetime
        import calendar

        current_year = datetime.now().year
        monthly_vat_data = []

        for month in range(1, 13):
            # مبيعات الشهر
            month_sales = db.session.query(db.func.sum(Invoice.total_amount)).filter(
                db.extract('year', Invoice.date) == current_year,
                db.extract('month', Invoice.date) == month
            ).scalar() or 0

            # مشتريات الشهر
            month_purchases = db.session.query(db.func.sum(PurchaseInvoice.total_amount)).filter(
                db.extract('year', PurchaseInvoice.date) == current_year,
                db.extract('month', PurchaseInvoice.date) == month
            ).scalar() or 0

            month_sales_vat = month_sales * vat_rate
            month_purchases_vat = month_purchases * vat_rate
            month_net_vat = month_sales_vat - month_purchases_vat

            monthly_vat_data.append({
                'month': calendar.month_name[month],
                'month_num': month,
                'sales': float(month_sales),
                'purchases': float(month_purchases),
                'sales_vat': float(month_sales_vat),
                'purchases_vat': float(month_purchases_vat),
                'net_vat': float(month_net_vat)
            })

        # إحصائيات إضافية
        invoices_count = Invoice.query.count()
        purchase_invoices_count = PurchaseInvoice.query.count()

        return render_template('vat.html',
                             total_sales=total_sales,
                             total_purchases=total_purchases,
                             sales_vat=sales_vat,
                             purchases_vat=purchases_vat,
                             net_vat=net_vat,
                             vat_rate=vat_rate,
                             monthly_vat_data=monthly_vat_data,
                             invoices_count=invoices_count,
                             purchase_invoices_count=purchase_invoices_count)
    except Exception as e:
        logger.error(f"خطأ في تحميل بيانات ضريبة القيمة المضافة: {str(e)}")
        return render_template('vat.html',
                             total_sales=0,
                             total_purchases=0,
                             sales_vat=0,
                             purchases_vat=0,
                             net_vat=0,
                             vat_rate=0.15,
                             monthly_vat_data=[],
                             invoices_count=0,
                             purchase_invoices_count=0)

@app.route('/employees')
def employees():
    try:
        all_employees = Employee.query.order_by(Employee.created_at.desc()).all()
        return render_template('employees.html', employees=all_employees)
    except Exception as e:
        logger.error(f"خطأ في تحميل الموظفين: {str(e)}")
        return render_template('employees.html', employees=[])

@app.route('/suppliers')
def suppliers():
    try:
        all_suppliers = Supplier.query.all()
        return render_template('suppliers.html', suppliers=all_suppliers)
    except Exception as e:
        logger.error(f"خطأ في تحميل الموردين: {str(e)}")
        return render_template('suppliers.html', suppliers=[])

@app.route('/reports')
@login_required
@measure_performance
def reports():
    try:
        from datetime import datetime

        # محاولة الحصول على البيانات من الـ cache
        current_month = datetime.now().month
        current_year = datetime.now().year
        cache_key = f"reports_data:{current_year}:{current_month}"
        cached_data = app_cache.get(cache_key)

        if cached_data:
            return render_template('reports.html', **cached_data)

        # إحصائيات عامة (محسنة)
        financial_stats = db.session.query(
            db.func.sum(Invoice.total_amount).label('total_sales'),
            db.func.count(Invoice.id).label('sales_count'),
            db.func.sum(PurchaseInvoice.total_amount).label('total_purchases'),
            db.func.count(PurchaseInvoice.id).label('purchases_count')
        ).outerjoin(PurchaseInvoice, False).first()  # Cross join للحصول على كلا الإحصائيات

        total_sales = float(financial_stats.total_sales or 0)
        total_purchases = float(financial_stats.total_purchases or 0)
        net_profit = total_sales - total_purchases
        profit_margin = (net_profit / total_sales * 100) if total_sales > 0 else 0
        sales_count = financial_stats.sales_count or 0
        purchases_count = financial_stats.purchases_count or 0

        # عدد العملاء والموردين (محسن)
        entity_counts = db.session.query(
            db.func.count(Customer.id.distinct()).label('customers'),
            db.func.count(Supplier.id.distinct()).label('suppliers')
        ).first()

        customers_count = entity_counts.customers or 0
        suppliers_count = entity_counts.suppliers or 0

        # إحصائيات الشهر الحالي (محسنة)
        current_month_stats = db.session.query(
            db.func.sum(Invoice.total_amount).label('sales'),
            db.func.sum(PurchaseInvoice.total_amount).label('purchases')
        ).filter(
            db.or_(
                db.and_(
                    db.extract('year', Invoice.date) == current_year,
                    db.extract('month', Invoice.date) == current_month
                ),
                db.and_(
                    db.extract('year', PurchaseInvoice.date) == current_year,
                    db.extract('month', PurchaseInvoice.date) == current_month
                )
            )
        ).first()

        current_month_sales = float(current_month_stats.sales or 0)
        current_month_purchases = float(current_month_stats.purchases or 0)

        # أفضل العملاء (حسب إجمالي المشتريات)
        top_customers = db.session.query(
            Customer.name,
            db.func.sum(Invoice.total_amount).label('total'),
            db.func.count(Invoice.id).label('invoices_count')
        ).join(Invoice).group_by(Customer.id).order_by(db.desc('total')).limit(5).all()

        # أفضل الموردين (حسب إجمالي المشتريات منهم)
        top_suppliers = db.session.query(
            Supplier.name,
            db.func.sum(PurchaseInvoice.total_amount).label('total'),
            db.func.count(PurchaseInvoice.id).label('invoices_count')
        ).join(PurchaseInvoice).group_by(Supplier.id).order_by(db.desc('total')).limit(5).all()

        # بيانات شهرية للرسوم البيانية (محسنة)
        monthly_optimized = get_optimized_monthly_data(current_year)
        monthly_data = []
        for month in range(1, 13):
            sales = monthly_optimized['sales'][month - 1]
            purchases = monthly_optimized['purchases'][month - 1]
            monthly_data.append({
                'month': month,
                'sales': sales,
                'purchases': purchases,
                'profit': sales - purchases
            })

        # إعداد البيانات للـ template
        template_data = {
            'total_sales': total_sales,
            'total_purchases': total_purchases,
            'net_profit': net_profit,
            'sales_count': sales_count,
            'purchases_count': purchases_count,
            'customers_count': customers_count,
            'suppliers_count': suppliers_count,
            'current_month_sales': current_month_sales,
            'current_month_purchases': current_month_purchases,
            'top_customers': top_customers,
            'top_suppliers': top_suppliers,
            'monthly_data': monthly_data,
            'profit_margin': profit_margin
        }

        # حفظ البيانات في الـ cache لمدة 15 دقيقة
        app_cache.set(cache_key, template_data, 900)

        return render_template('reports.html', **template_data)
    except Exception as e:
        logger.error(f"خطأ في تحميل بيانات التقارير: {str(e)}")
        return render_template('reports.html',
                             total_sales=0,
                             total_purchases=0,
                             net_profit=0,
                             sales_count=0,
                             purchases_count=0,
                             customers_count=0,
                             suppliers_count=0,
                             current_month_sales=0,
                             current_month_purchases=0,
                             top_customers=[],
                             top_suppliers=[],
                             monthly_data=[],
                             profit_margin=0)



@app.route('/settings')
@login_required
@permission_required('manage_settings')
def settings():
    # الحصول على جميع الإعدادات مقسمة حسب الفئة
    settings_by_category = {}
    all_settings = SystemSettings.query.order_by(SystemSettings.category, SystemSettings.setting_key).all()

    for setting in all_settings:
        if setting.category not in settings_by_category:
            settings_by_category[setting.category] = []
        settings_by_category[setting.category].append(setting)

    # الحصول على جميع المستخدمين
    users = User.query.order_by(User.created_at.desc()).all()

    return render_template('settings.html',
                         settings_by_category=settings_by_category,
                         users=users)

# إدارة المستخدمين
@app.route('/add_user', methods=['GET', 'POST'])
@login_required
@permission_required('manage_users')
def add_user():
    if request.method == 'POST':
        try:
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
            full_name = request.form.get('full_name')
            role = request.form.get('role', 'user')
            department = request.form.get('department')
            phone = request.form.get('phone')

            # التحقق من البيانات المطلوبة
            if not all([username, email, password, full_name]):
                flash('جميع الحقول المطلوبة يجب ملؤها.', 'error')
                return render_template('add_user.html')

            # التحقق من عدم وجود المستخدم
            if User.query.filter_by(username=username).first():
                flash('اسم المستخدم موجود بالفعل.', 'error')
                return render_template('add_user.html')

            if User.query.filter_by(email=email).first():
                flash('البريد الإلكتروني موجود بالفعل.', 'error')
                return render_template('add_user.html')

            # إنشاء المستخدم الجديد
            new_user = User(
                username=username,
                email=email,
                full_name=full_name,
                role=role,
                department=department,
                phone=phone
            )
            new_user.set_password(password)

            # تعيين الصلاحيات حسب الدور
            if role == 'admin':
                new_user.can_manage_users = True
                new_user.can_manage_settings = True
                new_user.can_manage_employees = True
                new_user.can_manage_payroll = True
            elif role == 'manager':
                new_user.can_manage_employees = True
                new_user.can_manage_payroll = True
            elif role == 'accountant':
                new_user.can_view_reports = True
                new_user.can_manage_invoices = True
                new_user.can_manage_customers = True
                new_user.can_manage_products = True

            db.session.add(new_user)
            db.session.commit()

            flash(f'تم إضافة المستخدم "{full_name}" بنجاح!', 'success')
            return redirect(url_for('settings'))

        except Exception as e:
            logger.error(f"خطأ في إضافة المستخدم: {str(e)}")
            db.session.rollback()
            flash('حدث خطأ أثناء إضافة المستخدم.', 'error')

    return render_template('add_user.html')

@app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
@permission_required('manage_users')
def edit_user(user_id):
    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        try:
            user.full_name = request.form.get('full_name', user.full_name)
            user.email = request.form.get('email', user.email)
            user.role = request.form.get('role', user.role)
            user.department = request.form.get('department', user.department)
            user.phone = request.form.get('phone', user.phone)
            user.is_active = bool(request.form.get('is_active'))

            # تحديث كلمة المرور إذا تم إدخالها
            new_password = request.form.get('password')
            if new_password:
                user.set_password(new_password)

            # تحديث الصلاحيات
            user.can_view_reports = bool(request.form.get('can_view_reports'))
            user.can_manage_invoices = bool(request.form.get('can_manage_invoices'))
            user.can_manage_customers = bool(request.form.get('can_manage_customers'))
            user.can_manage_products = bool(request.form.get('can_manage_products'))
            user.can_manage_employees = bool(request.form.get('can_manage_employees'))
            user.can_manage_payroll = bool(request.form.get('can_manage_payroll'))
            user.can_manage_settings = bool(request.form.get('can_manage_settings'))
            user.can_manage_users = bool(request.form.get('can_manage_users'))

            user.updated_at = datetime.now(timezone.utc)
            db.session.commit()

            flash(f'تم تحديث بيانات المستخدم "{user.full_name}" بنجاح!', 'success')
            return redirect(url_for('settings'))

        except Exception as e:
            logger.error(f"خطأ في تحديث المستخدم: {str(e)}")
            db.session.rollback()
            flash('حدث خطأ أثناء تحديث المستخدم.', 'error')

    return render_template('edit_user.html', user=user)

@app.route('/delete_user/<int:user_id>', methods=['POST'])
@login_required
@permission_required('manage_users')
def delete_user(user_id):
    try:
        user = User.query.get_or_404(user_id)

        # منع حذف المستخدم الحالي
        if user.id == current_user.id:
            flash('لا يمكنك حذف حسابك الخاص.', 'error')
            return redirect(url_for('settings'))

        # منع حذف آخر مدير
        if user.role == 'admin':
            admin_count = User.query.filter_by(role='admin').count()
            if admin_count <= 1:
                flash('لا يمكن حذف آخر مدير في النظام.', 'error')
                return redirect(url_for('settings'))

        username = user.username
        db.session.delete(user)
        db.session.commit()

        flash(f'تم حذف المستخدم "{username}" بنجاح!', 'success')

    except Exception as e:
        logger.error(f"خطأ في حذف المستخدم: {str(e)}")
        db.session.rollback()
        flash('حدث خطأ أثناء حذف المستخدم.', 'error')

    return redirect(url_for('settings'))

# إدارة إعدادات النظام
@app.route('/update_settings', methods=['POST'])
@login_required
@permission_required('manage_settings')
def update_settings():
    try:
        # جمع جميع الإعدادات الموجودة
        all_settings = SystemSettings.query.all()
        settings_dict = {s.setting_key: s for s in all_settings}

        # تحديث الإعدادات من النموذج
        for key, value in request.form.items():
            if key.startswith('setting_') and not key.endswith('_exists'):
                setting_key = key.replace('setting_', '')
                setting = settings_dict.get(setting_key)

                if setting:
                    setting.set_value(value)
                    setting.updated_at = datetime.now(timezone.utc)

        # معالجة checkbox values (boolean settings)
        for setting_key, setting in settings_dict.items():
            if setting.setting_type == 'boolean':
                exists_key = f'setting_{setting_key}_exists'
                checkbox_key = f'setting_{setting_key}'

                if exists_key in request.form:
                    # إذا كان checkbox موجود في النموذج
                    if checkbox_key in request.form:
                        # checkbox محدد
                        setting.set_value('true')
                    else:
                        # checkbox غير محدد
                        setting.set_value('false')
                    setting.updated_at = datetime.now(timezone.utc)

        db.session.commit()
        flash('تم تحديث الإعدادات بنجاح!', 'success')

    except Exception as e:
        logger.error(f"خطأ في تحديث الإعدادات: {str(e)}")
        db.session.rollback()
        flash('حدث خطأ أثناء تحديث الإعدادات.', 'error')

    return redirect(url_for('settings'))

@app.route('/add_setting', methods=['POST'])
@login_required
@permission_required('manage_settings')
def add_setting():
    try:
        setting_key = request.form.get('setting_key')
        setting_value = request.form.get('setting_value')
        setting_type = request.form.get('setting_type', 'string')
        description = request.form.get('description')
        category = request.form.get('category', 'general')
        is_public = bool(request.form.get('is_public'))

        if not setting_key:
            flash('مفتاح الإعداد مطلوب.', 'error')
            return redirect(url_for('settings'))

        # التحقق من عدم وجود الإعداد
        if SystemSettings.query.filter_by(setting_key=setting_key).first():
            flash('مفتاح الإعداد موجود بالفعل.', 'error')
            return redirect(url_for('settings'))

        new_setting = SystemSettings(
            setting_key=setting_key,
            setting_type=setting_type,
            description=description,
            category=category,
            is_public=is_public
        )
        new_setting.set_value(setting_value)

        db.session.add(new_setting)
        db.session.commit()

        flash(f'تم إضافة الإعداد "{setting_key}" بنجاح!', 'success')

    except Exception as e:
        logger.error(f"خطأ في إضافة الإعداد: {str(e)}")
        db.session.rollback()
        flash('حدث خطأ أثناء إضافة الإعداد.', 'error')

    return redirect(url_for('settings'))

@app.route('/delete_setting/<int:setting_id>', methods=['POST'])
@login_required
@permission_required('manage_settings')
def delete_setting(setting_id):
    try:
        setting = SystemSettings.query.get_or_404(setting_id)
        setting_key = setting.setting_key

        db.session.delete(setting)
        db.session.commit()

        flash(f'تم حذف الإعداد "{setting_key}" بنجاح!', 'success')

    except Exception as e:
        logger.error(f"خطأ في حذف الإعداد: {str(e)}")
        db.session.rollback()
        flash('حدث خطأ أثناء حذف الإعداد.', 'error')

    return redirect(url_for('settings'))

# إعداد الإعدادات الافتراضية
def setup_default_settings():
    """إعداد الإعدادات الافتراضية للنظام"""
    default_settings = [
        # إعدادات عامة
        ('company_name', 'شركة المحاسبة', 'string', 'اسم الشركة', 'general'),
        ('company_address', 'العنوان', 'string', 'عنوان الشركة', 'general'),
        ('company_phone', '+966xxxxxxxxx', 'string', 'هاتف الشركة', 'general'),
        ('company_email', 'info@company.com', 'string', 'بريد الشركة الإلكتروني', 'general'),
        ('tax_number', '123456789', 'string', 'الرقم الضريبي', 'general'),

        # إعدادات المظهر
        ('theme', 'light', 'string', 'سمة النظام (light/dark)', 'appearance'),
        ('language', 'ar', 'string', 'لغة النظام', 'appearance'),
        ('date_format', 'dd/mm/yyyy', 'string', 'تنسيق التاريخ', 'appearance'),
        ('currency', 'SAR', 'string', 'العملة الافتراضية', 'appearance'),
        ('items_per_page', '20', 'integer', 'عدد العناصر في الصفحة', 'appearance'),

        # إعدادات الأمان
        ('session_timeout', '30', 'integer', 'انتهاء الجلسة (بالدقائق)', 'security'),
        ('password_min_length', '8', 'integer', 'الحد الأدنى لطول كلمة المرور', 'security'),
        ('max_login_attempts', '5', 'integer', 'عدد محاولات تسجيل الدخول', 'security'),
        ('require_password_change', 'false', 'boolean', 'إجبار تغيير كلمة المرور', 'security'),

        # إعدادات الطباعة
        ('print_logo', 'true', 'boolean', 'طباعة شعار الشركة', 'printing'),
        ('print_header', 'true', 'boolean', 'طباعة رأس الصفحة', 'printing'),
        ('print_footer', 'true', 'boolean', 'طباعة تذييل الصفحة', 'printing'),
        ('paper_size', 'A4', 'string', 'حجم الورق', 'printing'),
        ('print_margins', '20', 'integer', 'هوامش الطباعة (مم)', 'printing'),

        # إعدادات التوطين
        ('timezone', 'Asia/Riyadh', 'string', 'المنطقة الزمنية', 'localization'),
        ('first_day_of_week', '6', 'integer', 'أول يوم في الأسبوع (0=أحد)', 'localization'),
        ('number_format', '1,234.56', 'string', 'تنسيق الأرقام', 'localization'),
        ('rtl_support', 'true', 'boolean', 'دعم الكتابة من اليمين لليسار', 'localization'),
    ]

    with app.app_context():
        for key, value, setting_type, description, category in default_settings:
            if not SystemSettings.query.filter_by(setting_key=key).first():
                setting = SystemSettings(
                    setting_key=key,
                    setting_type=setting_type,
                    description=description,
                    category=category,
                    is_public=True
                )
                setting.set_value(value)
                db.session.add(setting)

        db.session.commit()

# إنشاء مستخدم افتراضي
def create_default_admin():
    """إنشاء مستخدم مدير افتراضي"""
    with app.app_context():
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                email='admin@company.com',
                full_name='مدير النظام',
                role='admin',
                department='إدارة',
                can_view_reports=True,
                can_manage_invoices=True,
                can_manage_customers=True,
                can_manage_products=True,
                can_manage_employees=True,
                can_manage_payroll=True,
                can_manage_settings=True,
                can_manage_users=True
            )
            admin.set_password('admin123')  # يجب تغييرها في الإنتاج
            db.session.add(admin)
            db.session.commit()
            print("✅ تم إنشاء المستخدم الافتراضي: admin / admin123")

@app.route('/print_test')
def print_test():
    return render_template('print_test.html')

@app.route('/forms_test')
def forms_test():
    return render_template('forms_test.html')

# مسارات عرض الكيانات
@app.route('/view_product/<int:product_id>')
def view_product(product_id):
    try:
        product = Product.query.get_or_404(product_id)
        return render_template('view_product.html', product=product)
    except Exception as e:
        logger.error(f"خطأ في عرض المنتج {product_id}: {str(e)}")
        flash('حدث خطأ أثناء عرض المنتج.', 'error')
        return redirect(url_for('inventory'))

@app.route('/view_supplier/<int:supplier_id>')
def view_supplier(supplier_id):
    try:
        supplier = Supplier.query.get_or_404(supplier_id)
        return render_template('view_supplier.html', supplier=supplier)
    except Exception as e:
        logger.error(f"خطأ في عرض المورد {supplier_id}: {str(e)}")
        flash('حدث خطأ أثناء عرض المورد.', 'error')
        return redirect(url_for('suppliers'))

# مسارات حذف الكيانات
@app.route('/delete_product/<int:product_id>')
def delete_product(product_id):
    try:
        product = Product.query.get_or_404(product_id)
        product_name = product.name
        db.session.delete(product)
        db.session.commit()
        flash(f'تم حذف المنتج "{product_name}" بنجاح.', 'success')
    except Exception as e:
        logger.error(f"خطأ في حذف المنتج {product_id}: {str(e)}")
        db.session.rollback()
        flash('حدث خطأ أثناء حذف المنتج.', 'error')
    return redirect(url_for('inventory'))

@app.route('/delete_supplier/<int:supplier_id>')
def delete_supplier(supplier_id):
    try:
        supplier = Supplier.query.get_or_404(supplier_id)
        supplier_name = supplier.name
        db.session.delete(supplier)
        db.session.commit()
        flash(f'تم حذف المورد "{supplier_name}" بنجاح.', 'success')
    except Exception as e:
        logger.error(f"خطأ في حذف المورد {supplier_id}: {str(e)}")
        db.session.rollback()
        flash('حدث خطأ أثناء حذف المورد.', 'error')
    return redirect(url_for('suppliers'))

# مسارات تعديل الكيانات
@app.route('/edit_product/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    try:
        product = Product.query.get_or_404(product_id)

        if request.method == 'POST':
            # تحديث بيانات المنتج
            product.name = request.form.get('name')
            product.code = request.form.get('code')
            product.category = request.form.get('category')
            product.description = request.form.get('description')
            product.purchase_price = float(request.form.get('purchase_price', 0))
            product.selling_price = float(request.form.get('selling_price', 0))
            product.quantity = int(request.form.get('quantity', 0))
            product.min_quantity = int(request.form.get('min_quantity', 0))

            db.session.commit()
            flash(f'تم تحديث المنتج "{product.name}" بنجاح.', 'success')
            return redirect(url_for('view_product', product_id=product.id))

        return render_template('edit_product.html', product=product)
    except Exception as e:
        logger.error(f"خطأ في تعديل المنتج {product_id}: {str(e)}")
        db.session.rollback()
        flash('حدث خطأ أثناء تعديل المنتج.', 'error')
        return redirect(url_for('inventory'))

@app.route('/edit_supplier/<int:supplier_id>', methods=['GET', 'POST'])
def edit_supplier(supplier_id):
    try:
        supplier = Supplier.query.get_or_404(supplier_id)

        if request.method == 'POST':
            # تحديث بيانات المورد
            supplier.name = request.form.get('name')
            supplier.supplier_id = request.form.get('supplier_id')
            supplier.business_type = request.form.get('business_type')
            supplier.status = request.form.get('status')
            supplier.email = request.form.get('email')
            supplier.phone = request.form.get('phone')
            supplier.contact_info = request.form.get('contact_info')
            supplier.address = request.form.get('address')

            db.session.commit()
            flash(f'تم تحديث المورد "{supplier.name}" بنجاح.', 'success')
            return redirect(url_for('view_supplier', supplier_id=supplier.id))

        return render_template('edit_supplier.html', supplier=supplier)
    except Exception as e:
        logger.error(f"خطأ في تعديل المورد {supplier_id}: {str(e)}")
        db.session.rollback()
        flash('حدث خطأ أثناء تعديل المورد.', 'error')
        return redirect(url_for('suppliers'))

@app.route('/view_attendance/<int:attendance_id>')
def view_attendance(attendance_id):
    try:
        attendance = Attendance.query.get_or_404(attendance_id)
        return render_template('view_attendance.html', attendance=attendance)
    except Exception as e:
        logger.error(f"خطأ في عرض الحضور {attendance_id}: {str(e)}")
        flash('حدث خطأ أثناء عرض سجل الحضور.', 'error')
        return redirect(url_for('attendance'))

@app.route('/delete_attendance/<int:attendance_id>')
def delete_attendance(attendance_id):
    try:
        attendance = Attendance.query.get_or_404(attendance_id)
        employee_name = attendance.employee.name
        attendance_date = attendance.date.strftime('%Y-%m-%d')
        db.session.delete(attendance)
        db.session.commit()
        flash(f'تم حذف سجل حضور الموظف "{employee_name}" بتاريخ {attendance_date} بنجاح.', 'success')
    except Exception as e:
        logger.error(f"خطأ في حذف الحضور {attendance_id}: {str(e)}")
        db.session.rollback()
        flash('حدث خطأ أثناء حذف سجل الحضور.', 'error')
    return redirect(url_for('attendance'))

@app.route('/view_payment/<int:payment_id>')
def view_payment(payment_id):
    try:
        payment = Payment.query.get_or_404(payment_id)
        return render_template('view_payment.html', payment=payment)
    except Exception as e:
        logger.error(f"خطأ في عرض الدفعة {payment_id}: {str(e)}")
        flash('حدث خطأ أثناء عرض الدفعة.', 'error')
        return redirect(url_for('payments'))

@app.route('/print_payment/<int:payment_id>')
def print_payment(payment_id):
    try:
        payment = Payment.query.get_or_404(payment_id)
        return render_template('print_payment.html', payment=payment)
    except Exception as e:
        logger.error(f"خطأ في طباعة الدفعة {payment_id}: {str(e)}")
        flash('حدث خطأ أثناء طباعة الدفعة.', 'error')
        return redirect(url_for('payments'))

@app.route('/delete_payment/<int:payment_id>')
def delete_payment(payment_id):
    try:
        payment = Payment.query.get_or_404(payment_id)
        payment_ref = payment.reference_number or f"#{payment.id}"
        db.session.delete(payment)
        db.session.commit()
        flash(f'تم حذف الدفعة "{payment_ref}" بنجاح.', 'success')
    except Exception as e:
        logger.error(f"خطأ في حذف الدفعة {payment_id}: {str(e)}")
        db.session.rollback()
        flash('حدث خطأ أثناء حذف الدفعة.', 'error')
    return redirect(url_for('payments'))

@app.route('/view_expense/<int:expense_id>')
def view_expense(expense_id):
    try:
        expense = Expense.query.get_or_404(expense_id)
        return render_template('view_expense.html', expense=expense)
    except Exception as e:
        logger.error(f"خطأ في عرض المصروف {expense_id}: {str(e)}")
        flash('حدث خطأ أثناء عرض المصروف.', 'error')
        return redirect(url_for('expenses'))

@app.route('/delete_expense/<int:expense_id>')
def delete_expense(expense_id):
    try:
        expense = Expense.query.get_or_404(expense_id)
        expense_description = expense.description[:30]
        db.session.delete(expense)
        db.session.commit()
        flash(f'تم حذف المصروف "{expense_description}..." بنجاح.', 'success')
    except Exception as e:
        logger.error(f"خطأ في حذف المصروف {expense_id}: {str(e)}")
        db.session.rollback()
        flash('حدث خطأ أثناء حذف المصروف.', 'error')
    return redirect(url_for('expenses'))

@app.route('/view_purchase_invoice/<int:purchase_invoice_id>')
def view_purchase_invoice(purchase_invoice_id):
    try:
        purchase_invoice = PurchaseInvoice.query.get_or_404(purchase_invoice_id)
        return render_template('view_purchase_invoice.html', purchase_invoice=purchase_invoice)
    except Exception as e:
        logger.error(f"خطأ في عرض فاتورة المشتريات {purchase_invoice_id}: {str(e)}")
        flash('حدث خطأ أثناء عرض فاتورة المشتريات.', 'error')
        return redirect(url_for('purchase_invoices'))

@app.route('/delete_purchase_invoice/<int:purchase_invoice_id>')
def delete_purchase_invoice(purchase_invoice_id):
    try:
        purchase_invoice = PurchaseInvoice.query.get_or_404(purchase_invoice_id)
        invoice_number = purchase_invoice.invoice_number
        db.session.delete(purchase_invoice)
        db.session.commit()
        flash(f'تم حذف فاتورة المشتريات "{invoice_number}" بنجاح.', 'success')
    except Exception as e:
        logger.error(f"خطأ في حذف فاتورة المشتريات {purchase_invoice_id}: {str(e)}")
        db.session.rollback()
        flash('حدث خطأ أثناء حذف فاتورة المشتريات.', 'error')
    return redirect(url_for('purchase_invoices'))

@app.route('/view_payroll/<int:payroll_id>')
def view_payroll(payroll_id):
    try:
        payroll = Payroll.query.get_or_404(payroll_id)
        return render_template('view_payroll.html', payroll=payroll)
    except Exception as e:
        logger.error(f"خطأ في عرض الراتب {payroll_id}: {str(e)}")
        flash('حدث خطأ أثناء عرض الراتب.', 'error')
        return redirect(url_for('payroll'))

@app.route('/delete_payroll/<int:payroll_id>')
def delete_payroll(payroll_id):
    try:
        payroll = Payroll.query.get_or_404(payroll_id)
        employee_name = payroll.employee.name
        period = f"{payroll.month}/{payroll.year}"
        db.session.delete(payroll)
        db.session.commit()
        flash(f'تم حذف راتب الموظف "{employee_name}" لفترة {period} بنجاح.', 'success')
    except Exception as e:
        logger.error(f"خطأ في حذف الراتب {payroll_id}: {str(e)}")
        db.session.rollback()
        flash('حدث خطأ أثناء حذف الراتب.', 'error')
    return redirect(url_for('payroll'))

@app.route('/mark_payroll_paid/<int:payroll_id>')
def mark_payroll_paid(payroll_id):
    try:
        payroll = Payroll.query.get_or_404(payroll_id)
        payroll.status = 'paid'
        payroll.payment_date = datetime.now(timezone.utc).date()
        db.session.commit()
        flash(f'تم تأكيد دفع راتب الموظف "{payroll.employee.name}" بنجاح.', 'success')
    except Exception as e:
        logger.error(f"خطأ في تأكيد دفع الراتب {payroll_id}: {str(e)}")
        db.session.rollback()
        flash('حدث خطأ أثناء تأكيد دفع الراتب.', 'error')
    return redirect(url_for('view_payroll', payroll_id=payroll_id))

@app.route('/view_leave/<int:leave_id>')
def view_leave(leave_id):
    try:
        leave = Leave.query.get_or_404(leave_id)
        return render_template('view_leave.html', leave=leave)
    except Exception as e:
        logger.error(f"خطأ في عرض الإجازة {leave_id}: {str(e)}")
        flash('حدث خطأ أثناء عرض الإجازة.', 'error')
        return redirect(url_for('leaves'))

@app.route('/delete_leave/<int:leave_id>')
def delete_leave(leave_id):
    try:
        leave = Leave.query.get_or_404(leave_id)
        employee_name = leave.employee.name
        start_date = leave.start_date.strftime('%Y-%m-%d')
        db.session.delete(leave)
        db.session.commit()
        flash(f'تم حذف إجازة الموظف "{employee_name}" التي تبدأ في {start_date} بنجاح.', 'success')
    except Exception as e:
        logger.error(f"خطأ في حذف الإجازة {leave_id}: {str(e)}")
        db.session.rollback()
        flash('حدث خطأ أثناء حذف الإجازة.', 'error')
    return redirect(url_for('leaves'))

@app.route('/approve_leave/<int:leave_id>')
def approve_leave(leave_id):
    try:
        leave = Leave.query.get_or_404(leave_id)
        leave.status = 'approved'
        leave.approved_at = datetime.now(timezone.utc)
        leave.approved_by = 'المدير'  # يمكن تحسين هذا لاحقاً بنظام المستخدمين
        db.session.commit()
        flash(f'تم الموافقة على إجازة الموظف "{leave.employee.name}" بنجاح.', 'success')
    except Exception as e:
        logger.error(f"خطأ في الموافقة على الإجازة {leave_id}: {str(e)}")
        db.session.rollback()
        flash('حدث خطأ أثناء الموافقة على الإجازة.', 'error')
    return redirect(url_for('view_leave', leave_id=leave_id))

@app.route('/reject_leave/<int:leave_id>')
def reject_leave(leave_id):
    try:
        leave = Leave.query.get_or_404(leave_id)
        leave.status = 'rejected'
        reason = request.args.get('reason', '')
        if reason:
            leave.notes = f"سبب الرفض: {reason}"
        db.session.commit()
        flash(f'تم رفض إجازة الموظف "{leave.employee.name}".', 'warning')
    except Exception as e:
        logger.error(f"خطأ في رفض الإجازة {leave_id}: {str(e)}")
        db.session.rollback()
        flash('حدث خطأ أثناء رفض الإجازة.', 'error')
    return redirect(url_for('view_leave', leave_id=leave_id))

@app.route('/cancel_leave/<int:leave_id>')
def cancel_leave(leave_id):
    try:
        leave = Leave.query.get_or_404(leave_id)
        leave.status = 'cancelled'
        db.session.commit()
        flash(f'تم إلغاء إجازة الموظف "{leave.employee.name}" بنجاح.', 'info')
    except Exception as e:
        logger.error(f"خطأ في إلغاء الإجازة {leave_id}: {str(e)}")
        db.session.rollback()
        flash('حدث خطأ أثناء إلغاء الإجازة.', 'error')
    return redirect(url_for('view_leave', leave_id=leave_id))

# مسارات الموظفين
@app.route('/add_employee', methods=['GET', 'POST'])
def add_employee():
    if request.method == 'POST':
        try:
            # إنشاء رقم موظف تلقائي
            last_employee = Employee.query.order_by(Employee.id.desc()).first()
            if last_employee:
                last_id = int(last_employee.employee_id.replace('EMP', ''))
                employee_id = f'EMP{last_id + 1:04d}'
            else:
                employee_id = 'EMP0001'

            name = request.form['name']
            email = request.form.get('email')
            phone = request.form.get('phone')
            national_id = request.form.get('national_id')
            position = request.form.get('position')
            department = request.form.get('department')
            hire_date = request.form.get('hire_date')
            birth_date = request.form.get('birth_date')
            salary = request.form.get('salary')
            address = request.form.get('address')
            emergency_contact = request.form.get('emergency_contact')
            emergency_phone = request.form.get('emergency_phone')
            contract_type = request.form.get('contract_type', 'full_time')
            bank_account = request.form.get('bank_account')
            iban = request.form.get('iban')
            notes = request.form.get('notes')

            new_employee = Employee(
                employee_id=employee_id,
                name=name,
                email=email if email else None,
                phone=phone if phone else None,
                national_id=national_id if national_id else None,
                position=position if position else None,
                department=department if department else None,
                hire_date=datetime.strptime(hire_date, '%Y-%m-%d').date() if hire_date else None,
                birth_date=datetime.strptime(birth_date, '%Y-%m-%d').date() if birth_date else None,
                salary=float(salary) if salary else None,
                address=address if address else None,
                emergency_contact=emergency_contact if emergency_contact else None,
                emergency_phone=emergency_phone if emergency_phone else None,
                contract_type=contract_type,
                bank_account=bank_account if bank_account else None,
                iban=iban if iban else None,
                notes=notes if notes else None
            )

            db.session.add(new_employee)
            db.session.commit()

            # إذا كان طلب AJAX
            if request.headers.get('Content-Type') == 'application/json' or request.is_json:
                return jsonify({
                    'success': True,
                    'message': 'تم إضافة الموظف بنجاح!',
                    'employee_id': new_employee.id
                })

            flash('تم إضافة الموظف بنجاح!', 'success')
            return redirect(url_for('employees'))
        except Exception as e:
            logger.error(f"خطأ في إضافة الموظف: {str(e)}")
            db.session.rollback()

            # إذا كان طلب AJAX
            if request.headers.get('Content-Type') == 'application/json' or request.is_json:
                return jsonify({
                    'success': False,
                    'message': 'حدث خطأ أثناء إضافة الموظف. يرجى المحاولة مرة أخرى.'
                }), 400

            flash('حدث خطأ أثناء إضافة الموظف. يرجى المحاولة مرة أخرى.', 'error')

    return render_template('add_employee.html')

@app.route('/attendance')
def attendance():
    try:
        all_attendance = Attendance.query.join(Employee).order_by(Attendance.date.desc()).all()
        return render_template('attendance.html', attendance_records=all_attendance)
    except Exception as e:
        logger.error(f"خطأ في تحميل سجلات الحضور: {str(e)}")
        return render_template('attendance.html', attendance_records=[])

@app.route('/add_attendance', methods=['GET', 'POST'])
def add_attendance():
    if request.method == 'POST':
        try:
            employee_id = request.form['employee_id']
            date_str = request.form['date']
            check_in = request.form.get('check_in')
            check_out = request.form.get('check_out')
            break_start = request.form.get('break_start')
            break_end = request.form.get('break_end')
            status = request.form.get('status', 'present')
            notes = request.form.get('notes')

            # حساب إجمالي الساعات
            total_hours = 0
            overtime_hours = 0

            if check_in and check_out:
                check_in_time = datetime.strptime(check_in, '%H:%M').time()
                check_out_time = datetime.strptime(check_out, '%H:%M').time()

                # حساب الساعات
                check_in_datetime = datetime.combine(datetime.today(), check_in_time)
                check_out_datetime = datetime.combine(datetime.today(), check_out_time)

                if check_out_datetime > check_in_datetime:
                    work_duration = check_out_datetime - check_in_datetime
                    total_hours = work_duration.total_seconds() / 3600

                    # خصم وقت الاستراحة
                    if break_start and break_end:
                        break_start_time = datetime.strptime(break_start, '%H:%M').time()
                        break_end_time = datetime.strptime(break_end, '%H:%M').time()
                        break_start_datetime = datetime.combine(datetime.today(), break_start_time)
                        break_end_datetime = datetime.combine(datetime.today(), break_end_time)

                        if break_end_datetime > break_start_datetime:
                            break_duration = break_end_datetime - break_start_datetime
                            total_hours -= break_duration.total_seconds() / 3600

                    # حساب الساعات الإضافية (أكثر من 8 ساعات)
                    if total_hours > 8:
                        overtime_hours = total_hours - 8

            new_attendance = Attendance(
                employee_id=int(employee_id),
                date=datetime.strptime(date_str, '%Y-%m-%d').date(),
                check_in=datetime.strptime(check_in, '%H:%M').time() if check_in else None,
                check_out=datetime.strptime(check_out, '%H:%M').time() if check_out else None,
                break_start=datetime.strptime(break_start, '%H:%M').time() if break_start else None,
                break_end=datetime.strptime(break_end, '%H:%M').time() if break_end else None,
                total_hours=total_hours,
                overtime_hours=overtime_hours,
                status=status,
                notes=notes if notes else None
            )

            db.session.add(new_attendance)
            db.session.commit()
            flash('تم تسجيل الحضور بنجاح!', 'success')
            return redirect(url_for('attendance'))
        except Exception as e:
            logger.error(f"خطأ: {str(e)}")
            flash('حدث خطأ أثناء تسجيل الحضور. يرجى المحاولة مرة أخرى.', 'error')
            db.session.rollback()

    try:
        employees = Employee.query.filter_by(status='active').all()
    except Exception:
        employees = []
    return render_template('add_attendance.html', employees=employees)

@app.route('/payroll')
@login_required
def payroll():
    try:
        # جلب جميع سجلات الرواتب مع بيانات الموظفين
        all_payroll = Payroll.query.join(Employee).order_by(Payroll.year.desc(), Payroll.month.desc()).all()

        # حساب الإحصائيات العامة
        total_payroll = db.session.query(db.func.sum(Payroll.net_salary)).scalar() or 0
        total_employees = Employee.query.filter_by(status='active').count()
        avg_salary = total_payroll / total_employees if total_employees > 0 else 0

        # إحصائيات الشهر الحالي
        from datetime import datetime
        current_month = datetime.now().month
        current_year = datetime.now().year

        current_month_payroll = db.session.query(db.func.sum(Payroll.net_salary)).filter(
            Payroll.month == current_month,
            Payroll.year == current_year
        ).scalar() or 0

        current_month_count = Payroll.query.filter(
            Payroll.month == current_month,
            Payroll.year == current_year
        ).count()

        # أعلى الرواتب
        top_salaries = db.session.query(
            Employee.name,
            Payroll.net_salary,
            Payroll.month,
            Payroll.year
        ).join(Employee).order_by(Payroll.net_salary.desc()).limit(5).all()

        # إحصائيات شهرية للرسم البياني
        monthly_stats = []
        for month in range(1, 13):
            month_total = db.session.query(db.func.sum(Payroll.net_salary)).filter(
                Payroll.month == month,
                Payroll.year == current_year
            ).scalar() or 0

            month_count = Payroll.query.filter(
                Payroll.month == month,
                Payroll.year == current_year
            ).count()

            monthly_stats.append({
                'month': month,
                'total': float(month_total),
                'count': month_count,
                'average': float(month_total / month_count) if month_count > 0 else 0
            })

        return render_template('payroll.html',
                             payroll_records=all_payroll,
                             total_payroll=total_payroll,
                             total_employees=total_employees,
                             avg_salary=avg_salary,
                             current_month_payroll=current_month_payroll,
                             current_month_count=current_month_count,
                             top_salaries=top_salaries,
                             monthly_stats=monthly_stats)
    except Exception as e:
        logger.error(f"خطأ في تحميل بيانات الرواتب: {str(e)}")
        return render_template('payroll.html',
                             payroll_records=[],
                             total_payroll=0,
                             total_employees=0,
                             avg_salary=0,
                             current_month_payroll=0,
                             current_month_count=0,
                             top_salaries=[],
                             monthly_stats=[])

@app.route('/generate_payroll', methods=['GET', 'POST'])
def generate_payroll():
    if request.method == 'POST':
        try:
            month = int(request.form['month'])
            year = int(request.form['year'])
            employee_id = int(request.form['employee_id'])

            # الحصول على القيم من النموذج
            basic_salary = float(request.form['basic_salary'])
            allowances = float(request.form.get('allowances', 0))
            overtime_pay = float(request.form.get('overtime_pay', 0))
            bonus = float(request.form.get('bonus', 0))
            deductions = float(request.form.get('deductions', 0))
            insurance = float(request.form.get('insurance', 0))
            tax = float(request.form.get('tax', 0))
            other_deductions = float(request.form.get('other_deductions', 0))
            notes = request.form.get('notes', '')

            # حساب صافي الراتب
            gross_total = basic_salary + allowances + overtime_pay + bonus
            total_deductions = deductions + insurance + tax + other_deductions
            net_salary = gross_total - total_deductions

            # التحقق من وجود راتب للشهر
            existing_payroll = Payroll.query.filter_by(
                employee_id=employee_id,
                month=month,
                year=year
            ).first()

            if existing_payroll:
                flash('يوجد راتب مسجل لهذا الموظف في هذا الشهر!', 'warning')
                employees = Employee.query.filter_by(status='active').all()
                return render_template('generate_payroll.html', employees=employees)

            # إنشاء سجل راتب جديد
            new_payroll = Payroll(
                employee_id=employee_id,
                month=month,
                year=year,
                basic_salary=basic_salary,
                allowances=allowances + bonus,  # دمج البدلات والمكافآت
                overtime_pay=overtime_pay,
                deductions=deductions + other_deductions,  # دمج جميع الاستقطاعات
                tax=tax,
                insurance=insurance,
                net_salary=net_salary,
                notes=notes,
                status='pending'
            )

            db.session.add(new_payroll)
            db.session.commit()
            flash('تم إنشاء الراتب بنجاح!', 'success')
            return redirect(url_for('payroll'))

        except Exception as e:
            logger.error(f"خطأ: {str(e)}")
            flash('حدث خطأ أثناء إنشاء الرواتب. يرجى المحاولة مرة أخرى.', 'error')
            db.session.rollback()

    try:
        employees = Employee.query.filter_by(status='active').all()
    except Exception:
        employees = []
    return render_template('generate_payroll.html', employees=employees)

@app.route('/add_customer', methods=['GET', 'POST'])
def add_customer():
    if request.method == 'POST':
        try:
            name = request.form['name']
            email = request.form.get('email')
            phone = request.form.get('phone')

            new_customer = Customer(
                name=name,
                email=email if email else None,
                phone=phone if phone else None
            )
            db.session.add(new_customer)
            db.session.commit()

            # إذا كان طلب AJAX
            if request.headers.get('Content-Type') == 'application/json' or request.is_json:
                return jsonify({
                    'success': True,
                    'message': 'تم إضافة العميل بنجاح!',
                    'customer_id': new_customer.id
                })

            flash('تم إضافة العميل بنجاح!', 'success')
            return redirect(url_for('customers'))
        except Exception as e:
            logger.error(f"خطأ في إضافة العميل: {str(e)}")
            db.session.rollback()

            # إذا كان طلب AJAX
            if request.headers.get('Content-Type') == 'application/json' or request.is_json:
                return jsonify({
                    'success': False,
                    'message': 'حدث خطأ أثناء إضافة العميل. يرجى المحاولة مرة أخرى.'
                }), 400

            flash('حدث خطأ أثناء إضافة العميل. يرجى المحاولة مرة أخرى.', 'error')

    return render_template('add_customer.html')

@app.route('/customers')
def customers():
    try:
        all_customers = Customer.query.order_by(Customer.id.desc()).all()
        return render_template('customers.html', customers=all_customers)
    except Exception as e:
        logger.error(f"خطأ في تحميل العملاء: {str(e)}")
        return render_template('customers.html', customers=[])

@app.route('/add_invoice', methods=['GET', 'POST'])
def add_invoice():
    if request.method == 'POST':
        try:
            customer_name = request.form['customer_name']
            total_amount = float(request.form['total_amount'])
            invoice_date = request.form.get('invoice_date')
            notes = request.form.get('notes', '')

            # إنشاء الفاتورة بالحقول الموجودة فقط
            new_invoice = Invoice(
                customer_name=customer_name,
                total_amount=total_amount,
                date=datetime.strptime(invoice_date, '%Y-%m-%d') if invoice_date else datetime.now(),
                notes=notes
            )

            db.session.add(new_invoice)
            db.session.commit()
            flash('تم إنشاء الفاتورة بنجاح!', 'success')
            return redirect(url_for('invoices'))
        except Exception as e:
            logger.error(f"خطأ في إنشاء الفاتورة: {str(e)}")
            flash('حدث خطأ أثناء إنشاء الفاتورة. يرجى المحاولة مرة أخرى.', 'error')
            db.session.rollback()

    # جلب قائمة العملاء للاختيار منها
    try:
        customers = Customer.query.all()
    except:
        customers = []
    return render_template('add_invoice.html', customers=customers)

@app.route('/invoices')
def invoices():
    try:
        all_invoices = Invoice.query.order_by(Invoice.date.desc()).all()
        return render_template('invoices.html', invoices=all_invoices)
    except Exception:
        # في حالة حدوث خطأ، اعرض قائمة فارغة
        return render_template('invoices.html', invoices=[])

@app.route('/add_supplier', methods=['GET', 'POST'])
def add_supplier():
    if request.method == 'POST':
        try:
            name = request.form['name']
            contact_info = request.form.get('contact_info')
            new_supplier = Supplier(name=name, contact_info=contact_info)
            db.session.add(new_supplier)
            db.session.commit()
            flash('تم إضافة المورد بنجاح!', 'success')
            return redirect(url_for('suppliers'))
        except Exception as e:
            logger.error(f"خطأ: {str(e)}")
            flash('حدث خطأ أثناء إضافة المورد. يرجى المحاولة مرة أخرى.', 'error')
            db.session.rollback()

    return render_template('add_supplier.html')

# مسارات إضافية للمنتجات والمصروفات
@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        try:
            name = request.form['name']
            quantity = int(request.form['quantity'])
            price = float(request.form['price'])

            new_product = Product(name=name, quantity=quantity, price=price)
            db.session.add(new_product)
            db.session.commit()
            flash('تم إضافة المنتج بنجاح!', 'success')
            return redirect(url_for('inventory'))
        except Exception as e:
            logger.error(f"خطأ: {str(e)}")
            flash('حدث خطأ أثناء إضافة المنتج. يرجى المحاولة مرة أخرى.', 'error')
            db.session.rollback()

    return render_template('add_product.html')

@app.route('/add_expense', methods=['GET', 'POST'])
def add_expense():
    if request.method == 'POST':
        try:
            description = request.form['description']
            amount = float(request.form['amount'])
            expense_date = request.form.get('expense_date')

            new_expense = Expense(
                description=description,
                amount=amount,
                date=datetime.strptime(expense_date, '%Y-%m-%d') if expense_date else datetime.now()
            )
            db.session.add(new_expense)
            db.session.commit()
            flash('تم إضافة المصروف بنجاح!', 'success')
            return redirect(url_for('expenses'))
        except Exception as e:
            logger.error(f"خطأ: {str(e)}")
            flash('حدث خطأ أثناء إضافة المصروف. يرجى المحاولة مرة أخرى.', 'error')
            db.session.rollback()

    return render_template('add_expense.html')

# مسار لحذف العملاء
@app.route('/delete_customer/<int:customer_id>', methods=['POST'])
def delete_customer(customer_id):
    try:
        customer = Customer.query.get_or_404(customer_id)
        db.session.delete(customer)
        db.session.commit()
        flash('تم حذف العميل بنجاح!', 'success')
    except Exception as e:
        logger.error(f"خطأ: {str(e)}")
        flash('حدث خطأ أثناء حذف العميل.', 'error')
        db.session.rollback()
    return redirect(url_for('customers'))

# مسار لحذف الفواتير
@app.route('/delete_invoice/<int:invoice_id>', methods=['POST'])
def delete_invoice(invoice_id):
    try:
        invoice = Invoice.query.get_or_404(invoice_id)
        db.session.delete(invoice)
        db.session.commit()
        flash('تم حذف الفاتورة بنجاح!', 'success')
    except Exception as e:
        logger.error(f"خطأ: {str(e)}")
        flash('حدث خطأ أثناء حذف الفاتورة.', 'error')
        db.session.rollback()
    return redirect(url_for('invoices'))



# مسارات العرض والتعديل والحذف للموظفين
@app.route('/view_employee/<int:employee_id>')
def view_employee(employee_id):
    employee = Employee.query.get_or_404(employee_id)
    return render_template('view_employee.html', employee=employee)

@app.route('/edit_employee/<int:employee_id>', methods=['GET', 'POST'])
def edit_employee(employee_id):
    employee = Employee.query.get_or_404(employee_id)

    if request.method == 'POST':
        try:
            employee.name = request.form['name']
            employee.email = request.form.get('email')
            employee.phone = request.form.get('phone')
            employee.national_id = request.form.get('national_id')
            employee.position = request.form.get('position')
            employee.department = request.form.get('department')
            employee.salary = float(request.form.get('salary', 0))
            employee.address = request.form.get('address')
            employee.emergency_contact = request.form.get('emergency_contact')
            employee.emergency_phone = request.form.get('emergency_phone')
            employee.contract_type = request.form.get('contract_type')
            employee.bank_account = request.form.get('bank_account')
            employee.iban = request.form.get('iban')
            employee.notes = request.form.get('notes')

            db.session.commit()
            flash('تم تحديث بيانات الموظف بنجاح!', 'success')
            return redirect(url_for('employees'))
        except Exception as e:
            logger.error(f"خطأ: {str(e)}")
            flash('حدث خطأ أثناء تحديث بيانات الموظف.', 'error')
            db.session.rollback()

    return render_template('edit_employee.html', employee=employee)

@app.route('/delete_employee/<int:employee_id>', methods=['POST'])
def delete_employee(employee_id):
    try:
        employee = Employee.query.get_or_404(employee_id)
        db.session.delete(employee)
        db.session.commit()
        flash('تم حذف الموظف بنجاح!', 'success')
    except Exception as e:
        logger.error(f"خطأ: {str(e)}")
        flash('حدث خطأ أثناء حذف الموظف.', 'error')
        db.session.rollback()
    return redirect(url_for('employees'))

# مسارات العرض والتعديل والحذف للعملاء
@app.route('/view_customer/<int:customer_id>')
def view_customer(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    customer_invoices = Invoice.query.filter_by(customer_name=customer.name).all()
    return render_template('view_customer.html', customer=customer, invoices=customer_invoices)

@app.route('/edit_customer/<int:customer_id>', methods=['GET', 'POST'])
def edit_customer(customer_id):
    customer = Customer.query.get_or_404(customer_id)

    if request.method == 'POST':
        try:
            customer.name = request.form['name']
            customer.email = request.form.get('email')
            customer.phone = request.form.get('phone')

            db.session.commit()
            flash('تم تحديث بيانات العميل بنجاح!', 'success')
            return redirect(url_for('customers'))
        except Exception as e:
            logger.error(f"خطأ: {str(e)}")
            flash('حدث خطأ أثناء تحديث بيانات العميل.', 'error')
            db.session.rollback()

    return render_template('edit_customer.html', customer=customer)

# مسارات العرض والتعديل للفواتير
@app.route('/view_invoice/<int:invoice_id>')
def view_invoice(invoice_id):
    invoice = Invoice.query.get_or_404(invoice_id)
    return render_template('view_invoice.html', invoice=invoice)

@app.route('/edit_invoice/<int:invoice_id>', methods=['GET', 'POST'])
def edit_invoice(invoice_id):
    invoice = Invoice.query.get_or_404(invoice_id)

    if request.method == 'POST':
        try:
            invoice.customer_name = request.form['customer_name']
            invoice.total_amount = float(request.form['total_amount'])

            db.session.commit()
            flash('تم تحديث الفاتورة بنجاح!', 'success')
            return redirect(url_for('invoices'))
        except Exception as e:
            logger.error(f"خطأ: {str(e)}")
            flash('حدث خطأ أثناء تحديث الفاتورة.', 'error')
            db.session.rollback()

    customers = Customer.query.all()
    return render_template('edit_invoice.html', invoice=invoice, customers=customers)







# مسارات فواتير المشتريات
@app.route('/purchase_invoices')
@login_required
def purchase_invoices():
    try:
        # جلب جميع فواتير المشتريات مع الموردين
        all_purchase_invoices = PurchaseInvoice.query.order_by(PurchaseInvoice.date.desc()).all()

        # حساب الإحصائيات
        total_invoices = len(all_purchase_invoices)
        total_amount = sum(invoice.total_amount or 0 for invoice in all_purchase_invoices)

        # فواتير هذا الشهر
        from datetime import datetime
        current_month = datetime.now().month
        current_year = datetime.now().year

        monthly_invoices = [
            invoice for invoice in all_purchase_invoices
            if invoice.date and invoice.date.month == current_month and invoice.date.year == current_year
        ]
        monthly_total = sum(invoice.total_amount or 0 for invoice in monthly_invoices)

        # متوسط الفاتورة
        avg_invoice = total_amount / total_invoices if total_invoices > 0 else 0

        return render_template('purchase_invoices.html',
                             purchase_invoices=all_purchase_invoices,
                             total_invoices=total_invoices,
                             total_amount=total_amount,
                             monthly_total=monthly_total,
                             avg_invoice=avg_invoice)
    except Exception as e:
        logger.error(f"خطأ في تحميل فواتير المشتريات: {str(e)}")
        return render_template('purchase_invoices.html',
                             purchase_invoices=[],
                             total_invoices=0,
                             total_amount=0,
                             monthly_total=0,
                             avg_invoice=0)

@app.route('/add_purchase_invoice', methods=['GET', 'POST'])
def add_purchase_invoice():
    if request.method == 'POST':
        try:
            supplier_name = request.form['supplier_name']
            subtotal = float(request.form.get('subtotal', 0))
            tax_amount = float(request.form.get('tax_amount', 0))
            discount = float(request.form.get('discount', 0))
            total_amount = subtotal + tax_amount - discount
            notes = request.form.get('notes', '')

            new_purchase_invoice = PurchaseInvoice(
                supplier_name=supplier_name,
                subtotal=subtotal,
                tax_amount=tax_amount,
                discount=discount,
                total_amount=total_amount,
                notes=notes
            )

            db.session.add(new_purchase_invoice)
            db.session.commit()
            flash('تم إنشاء فاتورة المشتريات بنجاح!', 'success')
            return redirect(url_for('purchase_invoices'))
        except Exception as e:
            logger.error(f"خطأ: {str(e)}")
            flash('حدث خطأ أثناء إنشاء فاتورة المشتريات.', 'error')
            db.session.rollback()

    try:
        suppliers = Supplier.query.all()
    except Exception:
        suppliers = []
    return render_template('add_purchase_invoice.html', suppliers=suppliers)

# مسارات المدفوعات
@app.route('/payments')
def payments():
    try:
        # جلب جميع المدفوعات مع ترتيب حسب التاريخ
        all_payments = Payment.query.order_by(Payment.date.desc()).all()

        # حساب الإحصائيات
        total_received = sum(p.amount for p in all_payments if p.payment_type == 'received')
        total_paid = sum(p.amount for p in all_payments if p.payment_type == 'paid')
        net_flow = total_received - total_paid
        total_transactions = len(all_payments)

        # إحصائيات إضافية
        today_payments = [p for p in all_payments if p.date.date() == datetime.now().date()]
        this_month_payments = [p for p in all_payments if p.date.month == datetime.now().month and p.date.year == datetime.now().year]

        # تجميع حسب طريقة الدفع
        payment_methods_stats = {}
        for payment in all_payments:
            method = payment.payment_method
            if method not in payment_methods_stats:
                payment_methods_stats[method] = {'count': 0, 'total': 0}
            payment_methods_stats[method]['count'] += 1
            payment_methods_stats[method]['total'] += payment.amount

        # إرسال البيانات للقالب
        return render_template('payments.html',
                             payments=all_payments,
                             total_received=total_received,
                             total_paid=total_paid,
                             net_flow=net_flow,
                             total_transactions=total_transactions,
                             today_payments=len(today_payments),
                             this_month_payments=len(this_month_payments),
                             payment_methods_stats=payment_methods_stats)
    except Exception as e:
        logger.error(f"خطأ في جلب المدفوعات: {str(e)}")
        flash('حدث خطأ أثناء جلب المدفوعات.', 'error')
        return render_template('payments.html', payments=[])

@app.route('/add_payment', methods=['GET', 'POST'])
def add_payment():
    try:
        if request.method == 'POST':
            try:
                amount = float(request.form['amount'])
                payment_method = request.form['payment_method']
                payment_type = request.form['payment_type']
                reference_number = request.form.get('reference_number', '')
                notes = request.form.get('notes', '')

                # ربط بالفاتورة إذا تم تحديدها
                invoice_id = request.form.get('invoice_id')
                customer_name = request.form.get('customer_name', '')
                supplier_name = request.form.get('supplier_name', '')

                # إنشاء رقم مرجع تلقائي إذا لم يتم تحديده
                if not reference_number:
                    try:
                        last_payment = Payment.query.order_by(Payment.id.desc()).first()
                        reference_number = f"PAY-{(last_payment.id + 1) if last_payment else 1:06d}"
                    except:
                        reference_number = "PAY-000001"

                new_payment = Payment(
                    amount=amount,
                    payment_method=payment_method,
                    payment_type=payment_type,
                    reference_number=reference_number,
                    invoice_id=int(invoice_id) if invoice_id else None,
                    customer_name=customer_name,
                    supplier_name=supplier_name,
                    notes=notes
                )

                db.session.add(new_payment)

                # تحديث حالة الفاتورة إذا تم الدفع كاملاً
                if invoice_id:
                    try:
                        invoice = Invoice.query.get(invoice_id)
                        if invoice:
                            total_payments = sum(p.amount for p in invoice.payments) + amount
                            if total_payments >= invoice.total_amount:
                                invoice.status = 'paid'
                    except:
                        pass

                db.session.commit()
                flash('تم تسجيل الدفع بنجاح!', 'success')
                return redirect(url_for('payments'))
            except Exception:
                flash('حدث خطأ أثناء تسجيل الدفع.', 'error')
                db.session.rollback()

        # جلب الفواتير المعلقة
        try:
            pending_invoices = Invoice.query.filter_by(status='pending').all()
        except:
            pending_invoices = []

        return render_template('add_payment.html',
                             pending_invoices=pending_invoices)
    except Exception:
        # في حالة حدوث خطأ، اعرض صفحة فارغة
        return render_template('add_payment.html', pending_invoices=[])

@app.route('/sales_invoices')
def sales_invoices():
    try:
        # تحديث مسار فواتير المبيعات ليكون منفصل
        try:
            sales_invoices = Invoice.query.filter_by(invoice_type='sales').order_by(Invoice.date.desc()).all()
        except:
            # إذا فشل، اجلب جميع الفواتير
            sales_invoices = Invoice.query.order_by(Invoice.date.desc()).all()

        if not sales_invoices:
            # إذا لم توجد فواتير مبيعات، اعرض جميع الفواتير كفواتير مبيعات
            sales_invoices = Invoice.query.order_by(Invoice.date.desc()).all()

        return render_template('sales_invoices.html', sales_invoices=sales_invoices)
    except Exception:
        # في حالة حدوث خطأ، اعرض قائمة فارغة
        return render_template('sales_invoices.html', sales_invoices=[])

@app.route('/add_sales_invoice', methods=['GET', 'POST'])
def add_sales_invoice():
    if request.method == 'POST':
        try:
            customer_id = int(request.form.get('customer_id', 0))
            customer_name = request.form['customer_name']
            subtotal = float(request.form.get('subtotal', 0))
            tax_amount = float(request.form.get('tax_amount', 0))
            discount = float(request.form.get('discount', 0))
            total_amount = subtotal + tax_amount - discount
            notes = request.form.get('notes', '')

            # إنشاء رقم فاتورة تلقائي
            last_invoice = Invoice.query.order_by(Invoice.id.desc()).first()
            invoice_number = f"INV-{(last_invoice.id + 1) if last_invoice else 1:06d}"

            # إذا لم يتم تحديد عميل موجود، إنشاء عميل جديد
            if customer_id == 0 and customer_name:
                existing_customer = Customer.query.filter_by(name=customer_name).first()
                if existing_customer:
                    customer_id = existing_customer.id
                else:
                    new_customer = Customer(name=customer_name)
                    db.session.add(new_customer)
                    db.session.flush()  # للحصول على ID
                    customer_id = new_customer.id

            new_invoice = Invoice(
                customer_id=customer_id,
                customer_name=customer_name,
                invoice_number=invoice_number,
                subtotal=subtotal,
                tax_amount=tax_amount,
                discount=discount,
                total_amount=total_amount,
                invoice_type='sales',
                notes=notes
            )

            db.session.add(new_invoice)
            db.session.commit()
            flash('تم إنشاء فاتورة المبيعات بنجاح!', 'success')
            return redirect(url_for('sales_invoices'))
        except Exception as e:
            logger.error(f"خطأ: {str(e)}")
            flash('حدث خطأ أثناء إنشاء فاتورة المبيعات.', 'error')
            db.session.rollback()

    customers = Customer.query.all()
    return render_template('add_sales_invoice.html', customers=customers)

# مسارات إدارة الإجازات
@app.route('/leaves')
def leaves():
    try:
        all_leaves = Leave.query.order_by(Leave.created_at.desc()).all()
        return render_template('leaves.html', leaves=all_leaves)
    except Exception as e:
        logger.error(f"خطأ في تحميل الإجازات: {str(e)}")
        return render_template('leaves.html', leaves=[])

@app.route('/add_leave', methods=['GET', 'POST'])
def add_leave():
    if request.method == 'POST':
        try:
            employee_id = int(request.form['employee_id'])
            leave_type = request.form['leave_type']
            start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d').date()
            end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d').date()
            reason = request.form.get('reason', '')

            new_leave = Leave(
                employee_id=employee_id,
                leave_type=leave_type,
                start_date=start_date,
                end_date=end_date,
                reason=reason,
                status='pending'
            )

            db.session.add(new_leave)
            db.session.commit()
            flash('تم تقديم طلب الإجازة بنجاح!', 'success')
            return redirect(url_for('leaves'))
        except Exception as e:
            logger.error(f"خطأ: {str(e)}")
            flash('حدث خطأ أثناء تقديم طلب الإجازة.', 'error')
            db.session.rollback()

    try:
        employees = Employee.query.filter_by(status='active').all()
    except Exception:
        employees = []
    return render_template('add_leave.html', employees=employees)

# ==================== AJAX Routes ====================

@app.route('/ajax/quick_save_customer', methods=['POST'])
@login_required
@measure_performance
def ajax_quick_save_customer():
    """حفظ سريع للعملاء بـ AJAX"""
    try:
        if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
            return jsonify({'success': False, 'message': 'طلب غير صحيح'})

        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()

        if not name:
            return jsonify({'success': False, 'message': 'اسم العميل مطلوب'})

        # التحقق من عدم وجود عميل بنفس الاسم
        existing = Customer.query.filter_by(name=name).first()
        if existing:
            return jsonify({'success': False, 'message': 'يوجد عميل بهذا الاسم بالفعل'})

        customer = Customer(name=name, email=email, phone=phone)
        db.session.add(customer)
        db.session.commit()

        # إلغاء cache العملاء
        app_cache.delete('customers_list')
        invalidate_analytics_cache()

        return jsonify({
            'success': True,
            'message': 'تم إضافة العميل بنجاح',
            'customer': {
                'id': customer.id,
                'name': customer.name,
                'email': customer.email,
                'phone': customer.phone
            }
        })

    except Exception as e:
        db.session.rollback()
        logger.error(f"خطأ في حفظ العميل: {str(e)}")
        return jsonify({'success': False, 'message': 'حدث خطأ أثناء الحفظ'})

@app.route('/ajax/search_customers')
@login_required
@cache_result(timeout=60)
def ajax_search_customers():
    """البحث في العملاء بـ AJAX"""
    try:
        query = request.args.get('q', '').strip()
        if len(query) < 2:
            return jsonify({'success': True, 'html': '<div class="text-muted p-2">اكتب حرفين على الأقل للبحث</div>'})

        customers = Customer.query.filter(
            Customer.name.contains(query)
        ).limit(10).all()

        if not customers:
            return jsonify({'success': True, 'html': '<div class="text-muted p-2">لا توجد نتائج</div>'})

        html = '<div class="list-group">'
        for customer in customers:
            html += f'''
                <div class="list-group-item list-group-item-action" onclick="selectCustomer({customer.id}, '{customer.name}')">
                    <div class="d-flex w-100 justify-content-between">
                        <h6 class="mb-1">{customer.name}</h6>
                        <small>{customer.phone or ''}</small>
                    </div>
                    <small class="text-muted">{customer.email or ''}</small>
                </div>
            '''
        html += '</div>'

        return jsonify({'success': True, 'html': html})

    except Exception as e:
        logger.error(f"خطأ في البحث عن العملاء: {str(e)}")
        return jsonify({'success': False, 'message': 'حدث خطأ في البحث'})

# ==================== Background Tasks Routes ====================

@app.route('/ajax/generate_financial_report', methods=['POST'])
@login_required
def ajax_generate_financial_report():
    """إنشاء تقرير مالي في الخلفية"""
    try:
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')

        # تحويل التواريخ
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d') if start_date else None
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d') if end_date else None

        # إرسال المهمة للخلفية
        task_id = generate_comprehensive_financial_report(start_date_obj, end_date_obj)

        return jsonify({
            'success': True,
            'message': 'تم بدء إنشاء التقرير في الخلفية',
            'task_id': task_id
        })

    except Exception as e:
        logger.error(f"خطأ في إنشاء التقرير: {str(e)}")
        return jsonify({'success': False, 'message': 'حدث خطأ أثناء إنشاء التقرير'})

@app.route('/ajax/calculate_employee_stats', methods=['POST'])
@login_required
def ajax_calculate_employee_stats():
    """حساب إحصائيات الموظفين في الخلفية"""
    try:
        task_id = calculate_employee_statistics()

        return jsonify({
            'success': True,
            'message': 'تم بدء حساب الإحصائيات في الخلفية',
            'task_id': task_id
        })

    except Exception as e:
        logger.error(f"خطأ في حساب الإحصائيات: {str(e)}")
        return jsonify({'success': False, 'message': 'حدث خطأ أثناء حساب الإحصائيات'})

@app.route('/ajax/task_status/<task_id>')
@login_required
def ajax_task_status(task_id):
    """الحصول على حالة المهمة"""
    try:
        task = get_task_status(task_id)

        if not task:
            return jsonify({'success': False, 'message': 'المهمة غير موجودة'})

        return jsonify({
            'success': True,
            'task': {
                'id': task.task_id,
                'name': task.name,
                'status': task.status,
                'progress': task.progress,
                'created_at': task.created_at.isoformat() if task.created_at else None,
                'started_at': task.started_at.isoformat() if task.started_at else None,
                'completed_at': task.completed_at.isoformat() if task.completed_at else None,
                'error': task.error
            }
        })

    except Exception as e:
        logger.error(f"خطأ في الحصول على حالة المهمة: {str(e)}")
        return jsonify({'success': False, 'message': 'حدث خطأ في الحصول على حالة المهمة'})

@app.route('/ajax/task_result/<task_id>')
@login_required
def ajax_task_result(task_id):
    """الحصول على نتيجة المهمة"""
    try:
        result = get_task_result(task_id)

        if result is None:
            return jsonify({'success': False, 'message': 'النتيجة غير متوفرة'})

        return jsonify({
            'success': True,
            'result': result
        })

    except Exception as e:
        logger.error(f"خطأ في الحصول على نتيجة المهمة: {str(e)}")
        return jsonify({'success': False, 'message': 'حدث خطأ في الحصول على النتيجة'})

@app.route('/ajax/cleanup_data', methods=['POST'])
@login_required
def ajax_cleanup_data():
    """تنظيف البيانات القديمة"""
    try:
        task_id = cleanup_old_data()

        return jsonify({
            'success': True,
            'message': 'تم بدء تنظيف البيانات في الخلفية',
            'task_id': task_id
        })

    except Exception as e:
        logger.error(f"خطأ في تنظيف البيانات: {str(e)}")
        return jsonify({'success': False, 'message': 'حدث خطأ أثناء تنظيف البيانات'})

# ==================== Lazy Loading Routes ====================

@app.route('/ajax/lazy_invoices')
@login_required
@cache_result(timeout=60)
def ajax_lazy_invoices():
    """تحميل تدريجي للفواتير"""
    try:
        page = int(request.args.get('page', 1))
        size = int(request.args.get('size', 20))
        search = request.args.get('search', '').strip()

        # بناء الاستعلام
        query = Invoice.query

        if search:
            query = query.join(Customer).filter(
                db.or_(
                    Invoice.invoice_number.contains(search),
                    Customer.name.contains(search)
                )
            )

        # ترتيب وتقسيم الصفحات
        query = query.order_by(Invoice.date.desc())
        total = query.count()

        offset = (page - 1) * size
        invoices = query.offset(offset).limit(size).all()

        # تحويل البيانات
        data = []
        for invoice in invoices:
            data.append({
                'id': invoice.id,
                'invoice_number': invoice.invoice_number,
                'customer_name': invoice.customer.name if invoice.customer else '',
                'date': invoice.date.strftime('%Y-%m-%d'),
                'total_amount': float(invoice.total_amount),
                'status': invoice.status,
                'actions': f'''
                    <button class="btn btn-sm btn-primary" onclick="viewInvoice({invoice.id})">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="btn btn-sm btn-warning" onclick="editInvoice({invoice.id})">
                        <i class="fas fa-edit"></i>
                    </button>
                '''
            })

        has_more = (offset + size) < total

        return jsonify({
            'success': True,
            'data': data,
            'has_more': has_more,
            'total': total,
            'page': page
        })

    except Exception as e:
        logger.error(f"خطأ في التحميل التدريجي للفواتير: {str(e)}")
        return jsonify({'success': False, 'message': 'حدث خطأ في تحميل البيانات'})

@app.route('/ajax/lazy_customers')
@login_required
@cache_result(timeout=60)
def ajax_lazy_customers():
    """تحميل تدريجي للعملاء"""
    try:
        page = int(request.args.get('page', 1))
        size = int(request.args.get('size', 20))
        search = request.args.get('search', '').strip()

        query = Customer.query

        if search:
            query = query.filter(
                db.or_(
                    Customer.name.contains(search),
                    Customer.email.contains(search),
                    Customer.phone.contains(search)
                )
            )

        query = query.order_by(Customer.name)
        total = query.count()

        offset = (page - 1) * size
        customers = query.offset(offset).limit(size).all()

        data = []
        for customer in customers:
            # حساب إجمالي المبيعات
            total_sales = db.session.query(
                db.func.sum(Invoice.total_amount)
            ).filter_by(customer_id=customer.id).scalar() or 0

            data.append({
                'id': customer.id,
                'name': customer.name,
                'email': customer.email or '',
                'phone': customer.phone or '',
                'total_sales': float(total_sales),
                'actions': f'''
                    <button class="btn btn-sm btn-primary" onclick="viewCustomer({customer.id})">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="btn btn-sm btn-warning" onclick="editCustomer({customer.id})">
                        <i class="fas fa-edit"></i>
                    </button>
                '''
            })

        has_more = (offset + size) < total

        return jsonify({
            'success': True,
            'data': data,
            'has_more': has_more,
            'total': total,
            'page': page
        })

    except Exception as e:
        logger.error(f"خطأ في التحميل التدريجي للعملاء: {str(e)}")
        return jsonify({'success': False, 'message': 'حدث خطأ في تحميل البيانات'})

@app.route('/ajax/lazy_employees')
@login_required
@cache_result(timeout=60)
def ajax_lazy_employees():
    """تحميل تدريجي للموظفين"""
    try:
        page = int(request.args.get('page', 1))
        size = int(request.args.get('size', 20))
        search = request.args.get('search', '').strip()

        query = Employee.query

        if search:
            query = query.filter(
                db.or_(
                    Employee.name.contains(search),
                    Employee.email.contains(search),
                    Employee.phone.contains(search),
                    Employee.position.contains(search)
                )
            )

        query = query.order_by(Employee.name)
        total = query.count()

        offset = (page - 1) * size
        employees = query.offset(offset).limit(size).all()

        data = []
        for employee in employees:
            data.append({
                'id': employee.id,
                'name': employee.name,
                'email': employee.email or '',
                'phone': employee.phone or '',
                'position': employee.position or '',
                'salary': float(employee.salary),
                'status': employee.status,
                'hire_date': employee.hire_date.strftime('%Y-%m-%d') if employee.hire_date else '',
                'actions': f'''
                    <button class="btn btn-sm btn-primary" onclick="viewEmployee({employee.id})">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="btn btn-sm btn-warning" onclick="editEmployee({employee.id})">
                        <i class="fas fa-edit"></i>
                    </button>
                '''
            })

        has_more = (offset + size) < total

        return jsonify({
            'success': True,
            'data': data,
            'has_more': has_more,
            'total': total,
            'page': page
        })

    except Exception as e:
        logger.error(f"خطأ في التحميل التدريجي للموظفين: {str(e)}")
        return jsonify({'success': False, 'message': 'حدث خطأ في تحميل البيانات'})

if __name__ == '__main__':
    # تكوين تحسينات قاعدة البيانات
    configure_db_optimizations(app)

    # تهيئة نظام المهام الخلفية
    initialize_background_tasks()

    try:
        app.run(debug=True)
    finally:
        # إغلاق نظام المهام الخلفية عند الإغلاق
        shutdown_background_tasks()