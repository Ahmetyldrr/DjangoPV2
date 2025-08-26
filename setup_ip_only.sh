#!/bin/bash

echo "🔐 IP Tabanlı SSL Kurulumu"
echo "========================="
echo "Sunucu IP: 165.227.130.23"
echo ""

# 1. Sistem güncellemesi
echo "1. Sistem paketleri güncelleniyor..."
sudo apt update -y

# 2. Docker'ı durdur
echo "2. Docker servislerini durduruyor..."
docker-compose down

# 3. Port temizliği
echo "3. Port temizliği..."
sudo fuser -k 80/tcp 2>/dev/null || true
sudo fuser -k 443/tcp 2>/dev/null || true

# 4. Self-signed SSL sertifikası oluştur
echo "4. Self-signed SSL sertifikası oluşturuluyor..."
sudo mkdir -p /etc/ssl/private
sudo mkdir -p /etc/ssl/certs

sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/ssl/private/server.key \
    -out /etc/ssl/certs/server.crt \
    -subj "/C=TR/ST=Istanbul/L=Istanbul/O=Apphane/CN=165.227.130.23"

# 5. IP tabanlı nginx konfigürasyonu
echo "5. Nginx konfigürasyonu oluşturuluyor..."
cat > nginx.conf << 'EOF'
events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    upstream django {
        server web:9000;
    }

    # HTTP Server
    server {
        listen 80;
        server_name _;

        location /health/ {
            proxy_pass http://django;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

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

    # HTTPS Server
    server {
        listen 443 ssl http2;
        server_name _;

        ssl_certificate /etc/ssl/certs/server.crt;
        ssl_certificate_key /etc/ssl/private/server.key;
        
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_prefer_server_ciphers off;
        ssl_session_cache shared:SSL:10m;
        ssl_session_timeout 10m;

        client_max_body_size 100M;

        location /health/ {
            proxy_pass http://django;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto https;
        }

        location / {
            proxy_pass http://django;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto https;
        }

        location /static/ {
            alias /var/www/static/;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }

        location /media/ {
            alias /var/www/media/;
        }

        location /ws/ {
            proxy_pass http://django;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto https;
        }
    }
}
EOF

# 6. Django ayarlarını HTTP için düzenle (.env güncellemesi)
echo "6. Django ayarları HTTP için düzenleniyor..."
cat > .env << 'EOF'
SECRET_KEY=73y4=dgfoqs+z*a2yv94#=f*p$(v)58e1qytozm5kh=3p#x$s#
DEBUG=False
DATABASE_URL=postgresql://ahmet21:diclem2121@165.227.130.23:5432/fxdb
REDIS_URL=redis://redis:9379/0
EMAIL_HOST_USER=ahmetyildirir1@gmail.com
EMAIL_HOST_PASSWORD=impm timj vbts ywej
SECURE_SSL_REDIRECT=False
ALLOWED_HOSTS=165.227.130.23,localhost,127.0.0.1
EOF

# 7. Docker Compose güncellemesi
echo "7. Docker Compose konfigürasyonu güncelleniyor..."
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  web:
    build: .
    ports:
      - "9000:9000"
    environment:
      - DEBUG=False
      - DATABASE_URL=postgresql://ahmet21:diclem2121@165.227.130.23:5432/fxdb
      - REDIS_URL=redis://redis:9379/0
      - SECURE_SSL_REDIRECT=False
    depends_on:
      redis:
        condition: service_healthy
    volumes:
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9000/health/"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  redis:
    image: redis:alpine
    ports:
      - "9379:6379"
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 3
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - static_volume:/var/www/static
      - media_volume:/var/www/media
      - /etc/ssl/certs:/etc/ssl/certs:ro
      - /etc/ssl/private:/etc/ssl/private:ro
    depends_on:
      web:
        condition: service_healthy
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost/health/"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  static_volume:
  media_volume:
  redis_data:
EOF

# 8. UFW güvenlik duvarı
echo "8. Güvenlik duvarı ayarları..."
sudo ufw --force enable
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 9000/tcp

# 9. Docker'ı başlat
echo "9. Docker servisleri başlatılıyor..."
docker-compose up -d --build

# 10. Servislerin başlaması için bekle
echo "10. Servislerin başlaması bekleniyor..."
sleep 45

# 11. Test et
echo "11. Servisler test ediliyor..."
echo ""
echo "🔍 HTTP Test:"
if curl -f http://localhost:80/health/ > /dev/null 2>&1; then
    echo "✅ HTTP Health Check: BAŞARILI"
else
    echo "❌ HTTP Health Check: BAŞARISIZ"
fi

echo "🔍 HTTPS Test:"
if curl -k -f https://localhost:443/health/ > /dev/null 2>&1; then
    echo "✅ HTTPS Health Check: BAŞARILI (Self-signed)"
else
    echo "❌ HTTPS Health Check: BAŞARISIZ"
fi

echo "🔍 External HTTP Test:"
if curl -f http://165.227.130.23/health/ > /dev/null 2>&1; then
    echo "✅ External HTTP: BAŞARILI"
else
    echo "❌ External HTTP: BAŞARISIZ"
fi

echo "🔍 External HTTPS Test:"
if curl -k -f https://165.227.130.23/health/ > /dev/null 2>&1; then
    echo "✅ External HTTPS: BAŞARILI (Self-signed)"
else
    echo "❌ External HTTPS: BAŞARISIZ"
fi

echo ""
echo "🎉 IP TABANLI KURULUM TAMAMLANDI!"
echo "================================"
echo "🌐 HTTP Erişim: http://165.227.130.23"
echo "🔒 HTTPS Erişim: https://165.227.130.23 (self-signed sertifika)"
echo "📋 Admin Panel: http://165.227.130.23/admin/"
echo "🏥 Health Check: http://165.227.130.23/health/"
echo ""
echo "📊 Servis Durumu:"
docker-compose ps
echo ""
echo "🔧 Faydalı Komutlar:"
echo "- Logları izle: docker-compose logs -f"
echo "- Servisleri yeniden başlat: docker-compose restart"
echo "- Durum kontrol: curl -I http://165.227.130.23"
