FROM python:3.11-slim

WORKDIR /app

# Sistem bağımlılıkları
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Python bağımlılıkları
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Uygulama dosyaları
COPY . .

# Migrations ve static dosyalar
RUN python manage.py collectstatic --noinput --skip-checks

EXPOSE 9000

# Basit ve çalışan Gunicorn komutu
CMD ["gunicorn", "--bind", "0.0.0.0:9000", "--workers", "3", "config.wsgi:application"]
