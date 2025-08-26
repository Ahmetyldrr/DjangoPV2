# Django Projesi Sunucu Deployment Talimatları

## � Port Konfigürasyonu

**Önemli:** Bu sistem 9000'li portları kullanacak şekilde konfigüre edilmiştir:

- **Web Uygulama**: 9000
- **Redis**: 9379 (host), 6379 (container içi)
- **Nginx HTTP**: 9080
- **Nginx HTTPS**: 9443

### Erişim URL'leri:
- **HTTP**: http://apphane.com.tr:9080
- **HTTPS**: https://apphane.com.tr:9443
- **Direct App**: http://165.227.130.23:9000

## �📋 Proje Bilgileri
- **Domain**: apphane.com.tr
- **Server IP**: 165.227.130.23
- **Private IP**: 10.114.0.2
- **Server Spec**: 4 GB RAM, 2 vCPUs, 50 GB Disk
- **OS**: Ubuntu 24.10 x64
- **Database**: PostgreSQL (fxdb)

## 🔧 Sunucu Konfigürasyonu

### 1. Sunucuya Bağlanma
```bash
ssh root@165.227.130.23
```

### 2. Gerekli Paketlerin Kurulumu
```bash
# Sistem güncellemesi
apt update && apt upgrade -y

# Gerekli paketler
apt install -y python3 python3-pip python3-venv nginx git postgresql postgresql-contrib redis-server

# Docker kurulumu
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
systemctl enable docker
systemctl start docker

# Docker Compose kurulumu
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
```

### 3. PostgreSQL Konfigürasyonu
```bash
# PostgreSQL servisini başlat
systemctl enable postgresql
systemctl start postgresql

# Kullanıcı ve veritabanı oluştur
sudo -u postgres psql
```

```sql
CREATE USER ahmet21 WITH PASSWORD 'diclem2121';
CREATE DATABASE fxdb OWNER ahmet21;
GRANT ALL PRIVILEGES ON DATABASE fxdb TO ahmet21;
ALTER USER ahmet21 CREATEDB;
\q
```

```bash
# PostgreSQL konfigürasyonu düzenle
nano /etc/postgresql/*/main/postgresql.conf
# listen_addresses = '*' satırını açın

nano /etc/postgresql/*/main/pg_hba.conf
# Bu satırı ekleyin: host all all 0.0.0.0/0 md5

systemctl restart postgresql
```

### 4. Uygulama Dizini Oluşturma
```bash
mkdir -p /var/www/apphane
cd /var/www/apphane
git clone https://github.com/KULLANICI_ADI/REPO_ADI.git .
```

### 5. Python Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 🐳 Docker Konfigürasyonu

### 1. Dockerfile
```dockerfile
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

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "config.wsgi:application"]
```

### 2. docker-compose.yml
```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEBUG=False
      - DATABASE_URL=postgresql://ahmet21:diclem2121@165.227.130.23:5432/fxdb
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - redis
    volumes:
      - static_volume:/app/staticfiles
      - media_volume:/app/media

  redis:
    image: redis:alpine
    ports:
      - "6379:6379"

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - static_volume:/var/www/static
      - media_volume:/var/www/media
      - /etc/ssl/certs:/etc/ssl/certs
    depends_on:
      - web

volumes:
  static_volume:
  media_volume:
```

## 🌐 Nginx Konfigürasyonu

### nginx.conf
```nginx
events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    upstream django {
        server web:8000;
    }

    server {
        listen 80;
        server_name apphane.com.tr www.apphane.com.tr;
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name apphane.com.tr www.apphane.com.tr;

        ssl_certificate /etc/ssl/certs/apphane.com.tr.crt;
        ssl_certificate_key /etc/ssl/private/apphane.com.tr.key;

        client_max_body_size 100M;

        location / {
            proxy_pass http://django;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location /static/ {
            alias /var/www/static/;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }

        location /media/ {
            alias /var/www/media/;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }

        location /ws/ {
            proxy_pass http://django;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

## ⚙️ Django Settings Güncellemesi

### Production Settings (settings.py)
```python
import os
from pathlib import Path

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-93e5@eteyt3v2ltol$r4fnznr(3*b9b!sj=sd)&(^trniech05')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = ['apphane.com.tr', 'www.apphane.com.tr', '165.227.130.23', 'localhost']

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'fxdb',
        'USER': 'ahmet21',
        'PASSWORD': 'diclem2121',
        'HOST': '165.227.130.23',
        'PORT': '5432',
        'OPTIONS': {
            'connect_timeout': 10,
        }
    }
}

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = '/app/staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = '/app/media'

# Redis için Channels
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('redis', 6379)],
        },
    },
}

# Security settings
SECURE_SSL_REDIRECT = not DEBUG
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000 if not DEBUG else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Email settings (Production)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
```

## 📦 Requirements.txt Güncellemesi
```txt
Django>=5.0,<6.0
markdown
Pillow
psycopg2-binary
gunicorn
redis
channels
channels-redis
django-allauth
whitenoise
python-decouple
celery
```

## 🚀 CI/CD GitHub Actions

### .github/workflows/deploy.yml
```yaml
name: Deploy to Production

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Run tests
      env:
        DATABASE_URL: postgres://postgres:postgres@localhost/test_db
      run: |
        python manage.py test

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - name: Deploy to server
      uses: appleboy/ssh-action@v0.1.5
      with:
        host: 165.227.130.23
        username: root
        key: ${{ secrets.SSH_PRIVATE_KEY }}
        script: |
          cd /var/www/apphane
          git pull origin main
          docker-compose down
          docker-compose build
          docker-compose up -d
          docker-compose exec -T web python manage.py migrate
          docker-compose exec -T web python manage.py collectstatic --noinput
```

## 🔐 SSL Sertifikası (Let's Encrypt)
```bash
# Certbot kurulumu
apt install certbot python3-certbot-nginx -y

# SSL sertifikası al
certbot --nginx -d apphane.com.tr -d www.apphane.com.tr

# Otomatik yenileme
crontab -e
# Bu satırı ekle: 0 12 * * * /usr/bin/certbot renew --quiet
```

## 🎯 Deployment Adımları

### 1. GitHub Repository Hazırlama
```bash
# Local'de
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/KULLANICI_ADI/REPO_ADI.git
git push -u origin main
```

### 2. Sunucuda Deployment
```bash
# Sunucuya bağlan
ssh root@165.227.130.23

# Proje dizinine git
cd /var/www/apphane

# Docker ile çalıştır
docker-compose up -d

# Veritabanı migration
docker-compose exec web python manage.py migrate

# Static dosyaları topla
docker-compose exec web python manage.py collectstatic --noinput

# Superuser oluştur
docker-compose exec web python manage.py createsuperuser
```

### 3. Domain DNS Ayarları
```
A Record: apphane.com.tr -> 165.227.130.23
A Record: www.apphane.com.tr -> 165.227.130.23
```

### 4. Firewall Ayarları
```bash
ufw allow ssh
ufw allow 9080
ufw allow 9443
ufw enable
```

## 🔍 Monitoring ve Logs
```bash
# Container loglarını görüntüle
docker-compose logs -f

# Nginx logları
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log

# PostgreSQL logları
tail -f /var/log/postgresql/postgresql-*.log
```

## 🛠️ Bakım Komutları
```bash
# Uygulamayı güncelle
cd /var/www/apphane
git pull origin main
docker-compose down
docker-compose build
docker-compose up -d

# Backup oluştur
docker-compose exec postgres pg_dump -U ahmet21 fxdb > backup_$(date +%Y%m%d).sql

# Restore
docker-compose exec -T postgres psql -U ahmet21 fxdb < backup_file.sql
```

## 📧 Ortam Değişkenleri (.env)
```env
SECRET_KEY=your-secret-key-here
DEBUG=False
DATABASE_URL=postgresql://ahmet21:diclem2121@165.227.130.23:5432/fxdb
REDIS_URL=redis://redis:6379/0
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

Bu talimatları takip ederek Django projenizi başarılı bir şekilde sunucuya deploy edebilirsiniz!

