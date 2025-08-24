#!/bin/bash

echo "🧪 APPHANE HIZLI TEST SCRIPT"
echo "============================"

# Renk kodları
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Temel kontroller
echo "🔍 Temel kontroller..."

# 1. Docker servisleri çalışıyor mu?
echo -n "Docker servisleri: "
if docker-compose ps | grep -q "Up"; then
    echo -e "${GREEN}✅ Çalışıyor${NC}"
else
    echo -e "${RED}❌ Çalışmıyor${NC}"
fi

# 2. Health check
echo -n "Django backend: "
if curl -s -f http://localhost:9000/health/ > /dev/null; then
    echo -e "${GREEN}✅ Çalışıyor${NC}"
else
    echo -e "${RED}❌ Health check başarısız${NC}"
fi

# 2.1. HTTPS site check
echo -n "HTTPS site: "
if curl -s -f https://apphane.com.tr/ > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Çalışıyor${NC}"
else
    echo -e "${RED}❌ HTTPS erişim başarısız${NC}"
fi

# 3. Admin panel
echo -n "Admin panel: "
ADMIN_CODE=$(curl -s -o /dev/null -w "%{http_code}" https://apphane.com.tr/admin/ 2>/dev/null)
if [ "$ADMIN_CODE" = "200" ] || [ "$ADMIN_CODE" = "302" ]; then
    echo -e "${GREEN}✅ Erişilebilir (HTTPS $ADMIN_CODE)${NC}"
else
    echo -e "${RED}❌ Erişilemiyor (HTTPS $ADMIN_CODE)${NC}"
fi

# 3.1. Static files check
echo -n "Static files: "
CSS_CODE=$(curl -s -o /dev/null -w "%{http_code}" https://apphane.com.tr/static/css/style.css 2>/dev/null)
if [ "$CSS_CODE" = "200" ]; then
    echo -e "${GREEN}✅ CSS yükleniyor (HTTPS $CSS_CODE)${NC}"
else
    echo -e "${RED}❌ CSS yüklenmiyor (HTTPS $CSS_CODE)${NC}"
fi

# 4. Database bağlantısı
echo -n "Database: "
if docker-compose exec -T web python manage.py check --database default > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Bağlantılı${NC}"
else
    echo -e "${RED}❌ Bağlantı sorunu${NC}"
fi

# 5. Redis bağlantısı
echo -n "Redis: "
if docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Bağlantılı${NC}"
else
    echo -e "${RED}❌ Bağlantı sorunu${NC}"
fi

echo ""
echo "📊 Detaylı bilgiler:"
echo "Servis durumu:"
docker-compose ps

echo ""
echo "Nginx durumu:"
systemctl status nginx --no-pager | head -5 2>/dev/null || echo "Nginx status alınamadı"

echo ""
echo "Port kullanımı:"
netstat -tulpn | grep -E ':(80|443|9000)' 2>/dev/null || echo "Port bilgisi alınamadı"

echo ""
echo "Health check response:"
curl -s https://apphane.com.tr/health/ 2>/dev/null | python3 -m json.tool 2>/dev/null || curl -s http://localhost:9000/health/ | python3 -m json.tool 2>/dev/null || echo "Health check response alınamadı"

echo ""
echo "🔚 Test tamamlandı!"
