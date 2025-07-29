# استخدام Python 3.11 كصورة أساسية
FROM python:3.11-slim

# تعيين متغيرات البيئة
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=run.py \
    FLASK_ENV=production

# تعيين مجلد العمل
WORKDIR /app

# تثبيت متطلبات النظام
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    libffi-dev \
    libssl-dev \
    libxml2-dev \
    libxslt1-dev \
    libjpeg-dev \
    libpng-dev \
    zlib1g-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# إنشاء مستخدم غير جذر
RUN useradd --create-home --shell /bin/bash app

# نسخ ملف المتطلبات وتثبيتها
COPY requirements_pro.txt .
RUN pip install --no-cache-dir -r requirements_pro.txt

# نسخ ملفات التطبيق
COPY . .

# إنشاء المجلدات المطلوبة
RUN mkdir -p logs backups uploads instance static/uploads

# تعيين الصلاحيات
RUN chown -R app:app /app
USER app

# إنشاء قاعدة البيانات
RUN python run.py init-db

# تعريض المنفذ
EXPOSE 5000

# فحص الصحة
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# تشغيل التطبيق
CMD ["python", "run.py", "serve", "--host", "0.0.0.0", "--port", "5000"]
