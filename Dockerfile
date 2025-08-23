FROM python:3.11-slim

WORKDIR /app

# Sistem bağımlılıkları
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Static dosyaları topla
RUN python manage.py collectstatic --noinput

EXPOSE 9000

CMD ["gunicorn", "--bind", "0.0.0.0:9000", "config.wsgi:application"]
