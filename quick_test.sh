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
echo -n "Health check: "
if curl -s -f http://localhost:9000/health/ > /dev/null; then
    echo -e "${GREEN}✅ Başarılı${NC}"
else
    echo -e "${RED}❌ Başarısız${NC}"
fi

# 3. Admin panel
echo -n "Admin panel: "
ADMIN_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:9000/admin/)
if [ "$ADMIN_CODE" = "200" ] || [ "$ADMIN_CODE" = "302" ]; then
    echo -e "${GREEN}✅ Erişilebilir (HTTP $ADMIN_CODE)${NC}"
else
    echo -e "${RED}❌ Erişilemiyor (HTTP $ADMIN_CODE)${NC}"
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
echo "Health check response:"
curl -s http://localhost:9000/health/ | python3 -m json.tool 2>/dev/null || curl -s http://localhost:9000/health/

echo ""
echo "🔚 Test tamamlandı!"
