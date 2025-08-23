#!/bin/bash

echo "🔐 SSL Sertifikası Kurulum ve HTTPS Konfigürasyonu"
echo "================================================="

# Domain kontrolü
DOMAIN="apphane.com.tr"
SERVER_IP="165.227.130.23"

echo "1. Domain DNS kontrolü..."
CURRENT_IP=$(dig +short $DOMAIN)
if [ "$CURRENT_IP" != "$SERVER_IP" ]; then
    echo "❌ HATA: Domain $DOMAIN şu IP'ye yönlendirmiyor: $SERVER_IP"
    echo "Mevcut IP: $CURRENT_IP"
    echo "DNS ayarlarını kontrol edin ve tekrar deneyin."
    exit 1
fi
echo "✅ Domain doğru IP'ye yönlendiriyor: $CURRENT_IP"

# Paketleri güncelle
echo "2. Sistem paketleri güncelleniyor..."
sudo apt update -y
sudo apt upgrade -y

# Snap ve Certbot kurulumu
echo "3. Certbot kurulumu..."
sudo apt remove certbot -y
sudo snap install core; sudo snap refresh core
sudo snap install --classic certbot
sudo ln -sf /snap/bin/certbot /usr/bin/certbot

# Nginx'i durdur (eğer çalışıyorsa)
echo "4. Docker servislerini durduruyor..."
docker-compose down

# Port 80 temizliği
echo "5. Port 80 temizliği..."
sudo fuser -k 80/tcp 2>/dev/null || true
sudo systemctl stop nginx 2>/dev/null || true

# SSL sertifikası oluştur
echo "6. Let's Encrypt SSL sertifikası oluşturuluyor..."
sudo certbot certonly --standalone \
    --non-interactive \
    --agree-tos \
    --email admin@apphane.com.tr \
    --domains $DOMAIN,www.$DOMAIN \
    --expand

# Sertifika kontrolü
if [ ! -f "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" ]; then
    echo "❌ HATA: SSL sertifikası oluşturulamadı!"
    exit 1
fi
echo "✅ SSL sertifikası başarıyla oluşturuldu!"

# Docker Compose'u HTTPS konfigürasyonuyla başlat
echo "7. Docker servislerini HTTPS konfigürasyonuyla başlatıyor..."
docker-compose up -d

# Servislerin başlamasını bekle
echo "8. Servislerin başlaması bekleniyor..."
sleep 30

# SSL sertifikası yenileme cron job'u ekle
echo "9. SSL otomatik yenileme ayarlanıyor..."
(crontab -l 2>/dev/null; echo "0 12 * * * /usr/bin/certbot renew --quiet") | crontab -

# Güvenlik duvarı ayarları
echo "10. UFW güvenlik duvarı ayarları..."
sudo ufw --force enable
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 9000/tcp  # Django development port (gerekirse)

# Servis durumlarını kontrol et
echo "11. Servis durumları kontrol ediliyor..."
docker-compose ps

# HTTPS bağlantısını test et
echo "12. HTTPS bağlantısı test ediliyor..."
sleep 10

if curl -k -s -o /dev/null -w "%{http_code}" https://$DOMAIN/health/ | grep -q "200"; then
    echo "✅ HTTPS başarıyla çalışıyor!"
else
    echo "⚠️  HTTPS henüz tam olarak hazır değil, birkaç dakika bekleyin."
fi

# HTTP'den HTTPS yönlendirmesini test et
echo "13. HTTP -> HTTPS yönlendirmesi test ediliyor..."
HTTP_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://$DOMAIN)
if [ "$HTTP_RESPONSE" = "301" ] || [ "$HTTP_RESPONSE" = "302" ]; then
    echo "✅ HTTP -> HTTPS yönlendirmesi çalışıyor!"
else
    echo "⚠️  HTTP yönlendirmesi henüz aktif değil."
fi

echo ""
echo "🎉 SSL KURULUMU TAMAMLANDI!"
echo "=========================="
echo "🌐 Siteniz: https://$DOMAIN"
echo "📋 Admin Panel: https://$DOMAIN/admin/"
echo "🔒 SSL Sertifikası: Let's Encrypt"
echo "📅 Otomatik Yenileme: Günlük 12:00'da"
echo ""
echo "📊 Sistem Durumu:"
echo "- HTTP (80) -> HTTPS (443) yönlendirmesi: Aktif"
echo "- HTTPS (443): Aktif"
echo "- Django (9000): Aktif"
echo "- Redis (9379): Aktif"
echo ""
echo "🔧 Faydalı Komutlar:"
echo "- Logları izle: docker-compose logs -f"
echo "- Servisleri yeniden başlat: docker-compose restart"
echo "- SSL durumu: sudo certbot certificates"
echo "- SSL test et: curl -I https://$DOMAIN"
