#!/bin/bash

echo "🚀 APPHANE CI/CD DEPLOYMENT SCRIPT"
echo "=================================="
echo "Bu script CI/CD ile aynı komutları çalıştırır"
echo ""

# Renk kodları
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 1. Proje dizinine git
echo -e "${BLUE}1. Proje dizinine geçiliyor...${NC}"
cd /var/www/apphane || exit 1

# 2. Git güncellemesi
echo -e "${BLUE}2. Git güncellemesi yapılıyor...${NC}"
git stash
git pull origin main

# 3. Basit Docker Compose kullan
echo -e "${BLUE}3. Basit Docker Compose konfigürasyonu kullanılıyor...${NC}"
cp docker-compose-simple.yml docker-compose.yml

# 4. Mevcut servisleri durdur
echo -e "${BLUE}4. Mevcut servisler durduruluyor...${NC}"
docker-compose down --timeout 30

# 5. Cache temizliği (isteğe bağlı)
echo -e "${BLUE}5. Docker cache temizliği (gerekirse)...${NC}"
read -p "Docker cache temizlensin mi? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    docker system prune -f
fi

# 6. Clean build
echo -e "${BLUE}6. Clean build yapılıyor...${NC}"
docker-compose build --no-cache web

# 7. Servisleri başlat
echo -e "${BLUE}7. Servisler başlatılıyor...${NC}"
docker-compose up -d

# 8. Servislerin hazır olmasını bekle
echo -e "${BLUE}8. Servislerin hazır olması bekleniyor (max 5 dakika)...${NC}"
timeout 300 bash -c 'until curl -f http://localhost:9000/health/ > /dev/null 2>&1; do echo "Web servisi bekleniyor..."; sleep 10; done'

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Web servisi hazır!${NC}"
else
    echo -e "${RED}❌ Web servisi 5 dakikada hazır olmadı!${NC}"
    exit 1
fi

# 9. Migrations çalıştır
echo -e "${BLUE}9. Database migrations çalıştırılıyor...${NC}"
docker-compose exec -T web python manage.py migrate --noinput

# 10. Static files topla
echo -e "${BLUE}10. Static files toplanıyor...${NC}"
docker-compose exec -T web python manage.py collectstatic --noinput --clear

# 10.1. Static dosyaları host'a kopyala (Nginx için)
echo -e "${BLUE}10.1. Static dosyalar Nginx için kopyalanıyor...${NC}"
docker cp apphane_web_1:/app/staticfiles/. /var/www/apphane/staticfiles/ 2>/dev/null || true
docker cp apphane_web_1:/app/media/. /var/www/apphane/media/ 2>/dev/null || true

# 11. Final verification
echo -e "${BLUE}11. Final kontrol yapılıyor...${NC}"
if curl -f http://localhost:9000/health/ > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Deployment başarılı!${NC}"
else
    echo -e "${RED}❌ Final kontrol başarısız!${NC}"
    exit 1
fi

# 12. Servis durumlarını göster
echo -e "${BLUE}12. Servis durumları:${NC}"
docker-compose ps

echo ""
echo -e "${GREEN}🎉 DEPLOYMENT TAMAMLANDI!${NC}"
echo "=================================="
echo "🌐 Site: http://165.227.130.23"
echo "📋 Admin: http://165.227.130.23/admin/"
echo "🏥 Health: http://165.227.130.23/health/"
echo ""
echo "🔧 Faydalı komutlar:"
echo "- Logları izle: docker-compose logs -f"
echo "- Servisleri yeniden başlat: docker-compose restart"
echo "- Servis durumu: docker-compose ps"
