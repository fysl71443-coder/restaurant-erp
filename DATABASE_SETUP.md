# 🗄️ دليل إعداد قاعدة البيانات
## Database Setup Guide

---

## 📊 **خيارات قاعدة البيانات المتاحة**

### **الخيار 1: SQLite (افتراضي) - مجاني ✅**

**الاستخدام:**
- مناسب للتطوير والاختبار
- مناسب للمشاريع الصغيرة (أقل من 100 مستخدم)
- لا يحتاج إعداد إضافي

**الإعداد:**
```bash
# لا يحتاج إعداد - يعمل تلقائياً
python accounting_system_pro.py
```

---

### **الخيار 2: PostgreSQL (موصى به للإنتاج) - مجاني ✅**

**المميزات:**
- ✅ قاعدة بيانات احترافية
- ✅ البيانات محفوظة بشكل دائم
- ✅ يدعم آلاف المستخدمين المتزامنين
- ✅ نسخ احتياطي تلقائي
- ✅ مجاني على Render (500MB)

---

## 🚀 **إعداد PostgreSQL على Render**

### **الطريقة الأولى: استخدام render.yaml (تلقائي)**

1. **رفع المشروع على GitHub** مع ملف `render.yaml`
2. **في Render Dashboard:**
   - اختر "New Blueprint"
   - اربط مستودع GitHub
   - سيتم إنشاء قاعدة البيانات تلقائياً

### **الطريقة الثانية: إعداد يدوي**

1. **إنشاء قاعدة البيانات:**
   - في Render Dashboard
   - اختر "New PostgreSQL"
   - اسم قاعدة البيانات: `accounting-system`
   - خطة: Free

2. **إنشاء Web Service:**
   - اختر "New Web Service"
   - اربط مستودع GitHub
   - في Environment Variables أضف:
   ```
   DATABASE_URL=<رابط قاعدة البيانات من Render>
   SECRET_KEY=<مفتاح سري قوي>
   ```

---

## 🔧 **إعداد محلي مع PostgreSQL**

### **1. تثبيت PostgreSQL:**

**Windows:**
```bash
# تحميل من: https://www.postgresql.org/download/windows/
```

**macOS:**
```bash
brew install postgresql
brew services start postgresql
```

**Ubuntu/Linux:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
```

### **2. إنشاء قاعدة البيانات:**
```bash
# الدخول إلى PostgreSQL
sudo -u postgres psql

# إنشاء قاعدة البيانات والمستخدم
CREATE DATABASE accounting_system;
CREATE USER accounting_user WITH PASSWORD 'strong_password';
GRANT ALL PRIVILEGES ON DATABASE accounting_system TO accounting_user;
\q
```

### **3. تحديث متغيرات البيئة:**
```bash
# إنشاء ملف .env
echo "DATABASE_URL=postgresql://accounting_user:strong_password@localhost/accounting_system" > .env
echo "SECRET_KEY=your-secret-key-here" >> .env
```

### **4. تثبيت المتطلبات وتشغيل النظام:**
```bash
pip install -r requirements.txt
python accounting_system_pro.py
```

---

## 🔄 **التبديل بين قواعد البيانات**

### **للتبديل إلى SQLite:**
```bash
# حذف متغير DATABASE_URL أو تعيينه إلى:
export DATABASE_URL="sqlite:///accounting_pro.db"
```

### **للتبديل إلى PostgreSQL:**
```bash
# تعيين رابط PostgreSQL:
export DATABASE_URL="postgresql://username:password@host:port/database"
```

---

## 📋 **مقارنة سريعة**

| الميزة | SQLite | PostgreSQL |
|--------|--------|------------|
| **السعر** | مجاني | مجاني (500MB على Render) |
| **الإعداد** | بسيط جداً | يحتاج إعداد |
| **الأداء** | جيد للمشاريع الصغيرة | ممتاز للمشاريع الكبيرة |
| **المستخدمين المتزامنين** | محدود | غير محدود |
| **النسخ الاحتياطي** | يدوي | تلقائي |
| **الاستمرارية** | قد تُفقد البيانات | البيانات محفوظة |

---

## 🎯 **التوصية**

### **للتطوير والاختبار:**
- استخدم **SQLite** (الإعداد الافتراضي)

### **للإنتاج:**
- استخدم **PostgreSQL** على Render
- مجاني حتى 500MB
- أداء أفضل واستقرار أكبر

---

## 🆘 **حل المشاكل الشائعة**

### **مشكلة: خطأ في الاتصال بـ PostgreSQL**
```bash
# تحقق من رابط قاعدة البيانات
echo $DATABASE_URL

# تحقق من تثبيت psycopg2
pip install psycopg2-binary
```

### **مشكلة: البيانات لا تظهر**
```bash
# تأكد من تهيئة قاعدة البيانات
python -c "from accounting_system_pro import init_database; init_database()"
```

### **مشكلة: خطأ في الصلاحيات**
```sql
-- في PostgreSQL
GRANT ALL PRIVILEGES ON DATABASE accounting_system TO accounting_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO accounting_user;
```

---

**الخلاصة:** النظام يدعم كلا من SQLite و PostgreSQL، ويمكن التبديل بينهما بسهولة حسب احتياجاتك!
