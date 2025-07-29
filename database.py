from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
from sqlalchemy import Index, event
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

# Initialize SQLAlchemy with optimized configuration
db = SQLAlchemy()

# Database optimization configurations
def configure_db_optimizations(app):
    """تكوين تحسينات قاعدة البيانات"""
    # SQLite optimizations - يتم تطبيقها داخل سياق التطبيق
    if 'sqlite' in app.config.get('SQLALCHEMY_DATABASE_URI', ''):
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            try:
                # تحسينات SQLite للأداء
                cursor.execute("PRAGMA journal_mode=WAL")  # Write-Ahead Logging
                cursor.execute("PRAGMA synchronous=NORMAL")  # تحسين الكتابة
                cursor.execute("PRAGMA cache_size=10000")  # زيادة cache
                cursor.execute("PRAGMA temp_store=MEMORY")  # استخدام الذاكرة للملفات المؤقتة
                cursor.execute("PRAGMA mmap_size=268435456")  # 256MB memory mapping
            except Exception as e:
                print(f"تحذير: لا يمكن تطبيق تحسينات SQLite: {e}")
            finally:
                cursor.close()

        # تسجيل الحدث داخل سياق التطبيق
        with app.app_context():
            try:
                event.listens_for(db.engine, "connect")(set_sqlite_pragma)
                print("✅ تم تطبيق تحسينات قاعدة البيانات")
            except Exception as e:
                print(f"تحذير: لا يمكن تسجيل أحداث قاعدة البيانات: {e}")

# Define models

# نموذج المستخدمين
class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')  # admin, manager, user, accountant
    department = db.Column(db.String(50))
    phone = db.Column(db.String(20))
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    last_login = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # الصلاحيات
    can_view_reports = db.Column(db.Boolean, default=True)
    can_manage_invoices = db.Column(db.Boolean, default=True)
    can_manage_customers = db.Column(db.Boolean, default=True)
    can_manage_products = db.Column(db.Boolean, default=True)
    can_manage_employees = db.Column(db.Boolean, default=False)
    can_manage_payroll = db.Column(db.Boolean, default=False)
    can_manage_settings = db.Column(db.Boolean, default=False)
    can_manage_users = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        """تشفير كلمة المرور"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """التحقق من كلمة المرور"""
        return check_password_hash(self.password_hash, password)

    def has_permission(self, permission):
        """التحقق من الصلاحية"""
        if self.role == 'admin':
            return True
        return getattr(self, f'can_{permission}', False)

    def __repr__(self):
        return f'<User {self.username}>'

# نموذج إعدادات النظام
class SystemSettings(db.Model):
    __tablename__ = 'system_settings'

    id = db.Column(db.Integer, primary_key=True)
    setting_key = db.Column(db.String(100), unique=True, nullable=False, index=True)
    setting_value = db.Column(db.Text)
    setting_type = db.Column(db.String(20), default='string')  # string, integer, boolean, json
    description = db.Column(db.Text)
    category = db.Column(db.String(50), default='general')  # general, appearance, security, printing, localization
    is_public = db.Column(db.Boolean, default=False)  # هل يمكن للمستخدمين العاديين رؤيتها
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def get_value(self):
        """الحصول على القيمة بالنوع الصحيح"""
        if self.setting_type == 'boolean':
            return self.setting_value.lower() in ['true', '1', 'yes', 'on']
        elif self.setting_type == 'integer':
            try:
                return int(self.setting_value)
            except (ValueError, TypeError):
                return 0
        elif self.setting_type == 'json':
            try:
                import json
                return json.loads(self.setting_value)
            except (ValueError, TypeError):
                return {}
        return self.setting_value

    def set_value(self, value):
        """تعيين القيمة بالنوع الصحيح"""
        if self.setting_type == 'boolean':
            self.setting_value = str(bool(value)).lower()
        elif self.setting_type == 'integer':
            self.setting_value = str(int(value))
        elif self.setting_type == 'json':
            import json
            self.setting_value = json.dumps(value, ensure_ascii=False)
        else:
            self.setting_value = str(value)

    @staticmethod
    def get_setting(key, default=None):
        """الحصول على إعداد معين"""
        setting = SystemSettings.query.filter_by(setting_key=key).first()
        if setting:
            return setting.get_value()
        return default

    @staticmethod
    def set_setting(key, value, setting_type='string', description=None, category='general'):
        """تعيين إعداد معين"""
        setting = SystemSettings.query.filter_by(setting_key=key).first()
        if not setting:
            setting = SystemSettings(
                setting_key=key,
                setting_type=setting_type,
                description=description,
                category=category
            )
            db.session.add(setting)

        setting.set_value(value)
        setting.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        return setting

    def __repr__(self):
        return f'<SystemSettings {self.setting_key}={self.setting_value}>'

class Invoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    customer_name = db.Column(db.String(100), nullable=False, index=True)
    total_amount = db.Column(db.Float, nullable=False, index=True)
    invoice_type = db.Column(db.String(20), default='sales', index=True)  # 'sales' or 'purchase'
    status = db.Column(db.String(20), default='pending', index=True)  # 'pending', 'paid', 'overdue'
    subtotal = db.Column(db.Float, default=0.0)
    tax_amount = db.Column(db.Float, default=0.0)
    discount = db.Column(db.Float, default=0.0)
    notes = db.Column(db.Text)

class PurchaseInvoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    supplier_name = db.Column(db.String(100), nullable=False, index=True)
    total_amount = db.Column(db.Float, nullable=False, index=True)
    status = db.Column(db.String(20), default='pending', index=True)  # 'pending', 'paid', 'overdue'
    subtotal = db.Column(db.Float, default=0.0)
    tax_amount = db.Column(db.Float, default=0.0)
    discount = db.Column(db.Float, default=0.0)
    notes = db.Column(db.Text)
    invoice_number = db.Column(db.String(50), nullable=False, unique=True, index=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'), index=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    # Enhanced indexes for faster queries
    __table_args__ = (
        Index('idx_purchase_date_status', 'date', 'status'),
        Index('idx_purchase_supplier_date', 'supplier_id', 'date'),
        Index('idx_purchase_amount_date', 'total_amount', 'date'),
        Index('idx_purchase_number', 'invoice_number'),
    )

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)  # 'cash', 'bank_transfer', 'check', 'card'
    payment_type = db.Column(db.String(20), nullable=False)  # 'received', 'paid'
    reference_number = db.Column(db.String(100))
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoice.id'))
    # purchase_invoice_id = db.Column(db.Integer, db.ForeignKey('purchase_invoice.id'))
    customer_name = db.Column(db.String(100))
    supplier_name = db.Column(db.String(100))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # العلاقات
    invoice = db.relationship('Invoice', backref='payments')
    # purchase_invoice = db.relationship('PurchaseInvoice', backref='payments')

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=True)
    phone = db.Column(db.String(15), nullable=True)

class Supplier(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    contact_info = db.Column(db.String(200), nullable=True)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True)
    phone = db.Column(db.String(20))
    national_id = db.Column(db.String(20), unique=True)
    position = db.Column(db.String(100))
    department = db.Column(db.String(100))
    hire_date = db.Column(db.Date)
    birth_date = db.Column(db.Date)
    salary = db.Column(db.Float)
    address = db.Column(db.Text)
    emergency_contact = db.Column(db.String(100))
    emergency_phone = db.Column(db.String(20))
    status = db.Column(db.String(20), default='active')  # active, inactive, terminated
    contract_type = db.Column(db.String(20))  # full_time, part_time, contract
    bank_account = db.Column(db.String(50))
    iban = db.Column(db.String(50))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Enhanced indexes for faster queries
    __table_args__ = (
        Index('idx_employee_dept_status', 'department', 'status'),
        Index('idx_employee_position_dept', 'position', 'department'),
        Index('idx_employee_hire_date', 'hire_date'),
        Index('idx_employee_salary_range', 'salary'),
        Index('idx_employee_name_search', 'name'),
    )

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False, index=True)
    date = db.Column(db.Date, nullable=False, index=True)
    check_in = db.Column(db.Time)
    check_out = db.Column(db.Time)
    break_start = db.Column(db.Time)
    break_end = db.Column(db.Time)
    total_hours = db.Column(db.Float, index=True)
    overtime_hours = db.Column(db.Float, default=0, index=True)
    status = db.Column(db.String(20), default='present', index=True)  # present, absent, late, half_day
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    employee = db.relationship('Employee', backref=db.backref('attendances', lazy=True))

    # Enhanced indexes for faster queries
    __table_args__ = (
        Index('idx_attendance_emp_date', 'employee_id', 'date'),
        Index('idx_attendance_date_status', 'date', 'status'),
        Index('idx_attendance_month_year', 'date'),  # للتقارير الشهرية
    )

class Payroll(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    month = db.Column(db.Integer, nullable=False)  # 1-12
    year = db.Column(db.Integer, nullable=False)
    basic_salary = db.Column(db.Float, nullable=False)
    allowances = db.Column(db.Float, default=0)
    overtime_pay = db.Column(db.Float, default=0)
    deductions = db.Column(db.Float, default=0)
    tax = db.Column(db.Float, default=0)
    insurance = db.Column(db.Float, default=0)
    net_salary = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.Date)
    status = db.Column(db.String(20), default='pending')  # pending, paid, cancelled
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    employee = db.relationship('Employee', backref=db.backref('payrolls', lazy=True))

class Leave(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    leave_type = db.Column(db.String(50), nullable=False)  # annual, sick, emergency, maternity
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    days_count = db.Column(db.Integer, nullable=False)
    reason = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    approved_by = db.Column(db.String(100))
    approved_date = db.Column(db.Date)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    employee = db.relationship('Employee', backref=db.backref('leaves', lazy=True))

# Initialize database function
def init_db(app):
    """تهيئة قاعدة البيانات مع السياق الصحيح"""
    try:
        # تهيئة SQLAlchemy مع التطبيق
        db.init_app(app)
        print('✅ تم تهيئة SQLAlchemy')

        with app.app_context():
            try:
                # إنشاء الجداول
                db.create_all()
                print('✅ تم إنشاء الجداول')

                # تكوين تحسينات قاعدة البيانات بعد إنشاء الجداول
                configure_db_optimizations(app)

                # إنشاء مستخدم مدير افتراضي إذا لم يكن موجود
                admin_user = User.query.filter_by(username='admin').first()
                if not admin_user:
                    admin_user = User(
                        username='admin',
                        email='admin@system.com',
                        full_name='مدير النظام',
                        role='admin',
                        department='إدارة',
                        is_active=True,
                        can_view_reports=True,
                        can_manage_invoices=True,
                        can_manage_customers=True,
                        can_manage_products=True,
                        can_manage_employees=True,
                        can_manage_payroll=True,
                        can_manage_settings=True,
                        can_manage_users=True
                    )
                    admin_user.set_password('admin123')
                    db.session.add(admin_user)
                    db.session.commit()
                    print('✅ تم إنشاء المستخدم المدير: admin / admin123')
                else:
                    print('✅ المستخدم المدير موجود بالفعل')

                print('✅ تم تهيئة قاعدة البيانات بنجاح')
                return True

            except Exception as e:
                print(f'❌ خطأ في تهيئة قاعدة البيانات: {e}')
                try:
                    db.session.rollback()
                except:
                    pass
                return False

    except Exception as e:
        print(f'❌ خطأ في تهيئة SQLAlchemy: {e}')
        return False
