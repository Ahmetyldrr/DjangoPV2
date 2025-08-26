#!/bin/bash

echo "🔐 SSL Sertifikası Kurulum - IP Tabanlı"
echo "======================================"

# Geçici olarak IP ile SSL kurulumu
SERVER_IP="165.227.130.23"

echo "1. Sistem paketleri güncelleniyor..."
sudo apt update -y

echo "2. Certbot kurulumu..."
sudo apt remove certbot -y
sudo snap install core; sudo snap refresh core
sudo snap install --classic certbot
sudo ln -sf /snap/bin/certbot /usr/bin/certbot

echo "3. Docker servislerini durduruyor..."
docker-compose down

echo "4. Port 80 temizliği..."
sudo fuser -k 80/tcp 2>/dev/null || true
sudo systemctl stop nginx 2>/dev/null || true

echo "5. Geçici olarak IP ile self-signed SSL sertifikası oluşturuluyor..."
sudo mkdir -p /etc/ssl/private
sudo mkdir -p /etc/ssl/certs

# Self-signed sertifika oluştur
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/ssl/private/apphane.key \
    -out /etc/ssl/certs/apphane.crt \
    -subj "/C=TR/ST=Istanbul/L=Istanbul/O=Apphane/OU=IT Department/CN=apphane.com.tr"

echo "6. Geçici nginx konfigürasyonu oluşturuluyor..."
cat > nginx-temp.conf << 'EOF'
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

        location / {
            proxy_pass http://django;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location /health/ {
            proxy_pass http://django;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location /static/ {
            alias /var/www/static/;
        }

        location /media/ {
            alias /var/www/media/;
        }
    }

    # HTTPS Server (Self-signed)
    server {
        listen 443 ssl http2;
        server_name _;

        ssl_certificate /etc/ssl/certs/apphane.crt;
        ssl_certificate_key /etc/ssl/private/apphane.key;
        
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_prefer_server_ciphers off;

        location / {
            proxy_pass http://django;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location /health/ {
            proxy_pass http://django;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location /static/ {
            alias /var/www/static/;
        }

        location /media/ {
            alias /var/www/media/;
        }
    }
}
EOF

echo "7. Geçici docker-compose.yml oluşturuluyor..."
cat > docker-compose-temp.yml << 'EOF'
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
      - ./nginx-temp.conf:/etc/nginx/nginx.conf
      - static_volume:/var/www/static
      - media_volume:/var/www/media
      - /etc/ssl/certs:/etc/ssl/certs:ro
      - /etc/ssl/private:/etc/ssl/private:ro
    depends_on:
      web:
        condition: service_healthy
    restart: unless-stopped

volumes:
  static_volume:
  media_volume:
  redis_data:
EOF

echo "8. Docker servislerini geçici konfigürasyonla başlatıyor..."
docker-compose -f docker-compose-temp.yml up -d

echo "9. Servislerin başlaması bekleniyor..."
sleep 30

echo "10. Güvenlik duvarı ayarları..."
sudo ufw --force enable
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

echo "11. Test ediliyor..."
echo "HTTP Test:"
curl -I http://165.227.130.23/health/ || echo "HTTP test başarısız"

echo "HTTPS Test (self-signed):"
curl -k -I https://165.227.130.23/health/ || echo "HTTPS test başarısız"

echo ""
echo "🎉 GEÇİCİ SSL KURULUMU TAMAMLANDI!"
echo "================================"
echo "🌐 HTTP Erişim: http://165.227.130.23"
echo "🔒 HTTPS Erişim: https://165.227.130.23 (self-signed)"
echo ""
echo "📋 DNS düzeltildikten sonra yapılacaklar:"
echo "1. DNS propagasyonunu bekleyin (15dk - 2 saat)"
echo "2. 'dig apphane.com.tr' ile IP kontrolü yapın"
echo "3. Let's Encrypt sertifikası için ./setup_ssl_production.sh çalıştırın"
echo ""
echo "🔧 DNS kontrol komutları:"
echo "dig apphane.com.tr"
echo "nslookup apphane.com.tr"
EOF
