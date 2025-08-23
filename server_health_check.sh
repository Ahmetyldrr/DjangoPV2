#!/bin/bash

echo "🔍 APPHANE SUNUCU SAĞLIK KONTROLÜ"
echo "=================================="
echo "Sunucu: 165.227.130.23"
echo "Domain: apphane.com.tr"
echo "Tarih: $(date)"
echo ""

# Renk kodları
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 1. SISTEM DURUMU
echo -e "${BLUE}1. 💻 SİSTEM DURUMU${NC}"
echo "=================================="
echo "🖥️ Sistem Bilgileri:"
uname -a
echo ""
echo "💾 Disk Kullanımı:"
df -h | grep -E '(Filesystem|/dev/)'
echo ""
echo "🧠 RAM Kullanımı:"
free -h
echo ""
echo "⚡ CPU Yükü:"
uptime
echo ""

# 2. DOCKER SERVİSLERİ
echo -e "${BLUE}2. 🐳 DOCKER SERVİSLERİ${NC}"
echo "=================================="
echo "📋 Docker Compose Durumu:"
if docker-compose ps; then
    echo -e "${GREEN}✅ Docker servisleri çalışıyor${NC}"
else
    echo -e "${RED}❌ Docker servisleri ÇALIŞMIYOR!${NC}"
fi
echo ""

echo "📊 Container Durumları:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo ""

echo "💾 Docker Resource Kullanımı:"
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"
echo ""

# 3. PORT KONTROLLERI
echo -e "${BLUE}3. 🌐 PORT KONTROLLERI${NC}"
echo "=================================="

check_port() {
    local port=$1
    local service=$2
    if ss -tlnp | grep ":$port " > /dev/null; then
        echo -e "✅ Port $port ($service): ${GREEN}AÇIK${NC}"
    else
        echo -e "❌ Port $port ($service): ${RED}KAPALI${NC}"
    fi
}

check_port 80 "HTTP"
check_port 443 "HTTPS" 
check_port 8000 "Nginx Docker"
check_port 9000 "Django"
check_port 9379 "Redis"
check_port 5432 "PostgreSQL"
check_port 22 "SSH"
echo ""

# 4. SAĞLIK KONTROLLERI
echo -e "${BLUE}4. 🏥 SAĞLIK KONTROLLERI${NC}"
echo "=================================="

echo "🔍 Local Health Check (Django):"
if curl -s -f http://localhost:9000/health/ > /dev/null; then
    echo -e "${GREEN}✅ Django Health Check: BAŞARILI${NC}"
else
    echo -e "${RED}❌ Django Health Check: BAŞARISIZ${NC}"
fi

echo "🔍 Nginx Health Check:"
if curl -s -f http://localhost:8000/health/ > /dev/null; then
    echo -e "${GREEN}✅ Nginx Health Check: BAŞARILI${NC}"
else
    echo -e "${RED}❌ Nginx Health Check: BAŞARISIZ${NC}"
fi

echo "🔍 External HTTP Check:"
if curl -s -f http://apphane.com.tr/health/ > /dev/null; then
    echo -e "${GREEN}✅ External HTTP: BAŞARILI${NC}"
else
    echo -e "${RED}❌ External HTTP: BAŞARISIZ${NC}"
    echo "HTTP Response Code: $(curl -s -o /dev/null -w "%{http_code}" http://apphane.com.tr/health/)"
fi

echo "🔍 External HTTPS Check:"
if curl -s -k -f https://apphane.com.tr/health/ > /dev/null; then
    echo -e "${GREEN}✅ External HTTPS: BAŞARILI${NC}"
else
    echo -e "${RED}❌ External HTTPS: BAŞARISIZ${NC}"
    echo "HTTPS Response Code: $(curl -s -k -o /dev/null -w "%{http_code}" https://apphane.com.tr/health/)"
fi
echo ""

# 5. SSL SERTİFİKASI KONTROLÜ
echo -e "${BLUE}5. 🔒 SSL SERTİFİKASI KONTROLÜ${NC}"
echo "=================================="
if [ -f "/etc/letsencrypt/live/apphane.com.tr/fullchain.pem" ]; then
    echo -e "${GREEN}✅ SSL Sertifikası mevcut${NC}"
    echo "📅 Sertifika Bilgileri:"
    openssl x509 -in /etc/letsencrypt/live/apphane.com.tr/fullchain.pem -text -noout | grep -E "(Not Before|Not After|Subject:|Issuer:)"
    echo ""
    
    # Sertifika bitiş tarihi kontrolü
    EXPIRE_DATE=$(openssl x509 -in /etc/letsencrypt/live/apphane.com.tr/fullchain.pem -enddate -noout | sed 's/notAfter=//')
    EXPIRE_EPOCH=$(date -d "$EXPIRE_DATE" +%s)
    CURRENT_EPOCH=$(date +%s)
    DAYS_LEFT=$(( (EXPIRE_EPOCH - CURRENT_EPOCH) / 86400 ))
    
    if [ $DAYS_LEFT -gt 30 ]; then
        echo -e "⏰ Sertifika Süresi: ${GREEN}$DAYS_LEFT gün kaldı${NC}"
    elif [ $DAYS_LEFT -gt 7 ]; then
        echo -e "⏰ Sertifika Süresi: ${YELLOW}$DAYS_LEFT gün kaldı (yakında yenilenecek)${NC}"
    else
        echo -e "⏰ Sertifika Süresi: ${RED}$DAYS_LEFT gün kaldı (ACİL YENİLENMELİ!)${NC}"
    fi
else
    echo -e "${RED}❌ SSL Sertifikası BULUNAMADI!${NC}"
fi
echo ""

# 6. UYGULAMA KONTROLLERI
echo -e "${BLUE}6. 📱 UYGULAMA KONTROLLERI${NC}"
echo "=================================="

echo "🗄️ Database Bağlantısı:"
if docker-compose exec -T web python manage.py dbshell --command="SELECT 1;" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ PostgreSQL Bağlantısı: BAŞARILI${NC}"
else
    echo -e "${RED}❌ PostgreSQL Bağlantısı: BAŞARISIZ${NC}"
fi

echo "🔴 Redis Bağlantısı:"
if docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Redis Bağlantısı: BAŞARILI${NC}"
else
    echo -e "${RED}❌ Redis Bağlantısı: BAŞARISIZ${NC}"
fi

echo "📊 Django Admin Erişimi:"
ADMIN_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" https://apphane.com.tr/admin/)
if [ "$ADMIN_RESPONSE" = "200" ] || [ "$ADMIN_RESPONSE" = "302" ]; then
    echo -e "${GREEN}✅ Django Admin: ERİŞİLEBİLİR (HTTP $ADMIN_RESPONSE)${NC}"
else
    echo -e "${RED}❌ Django Admin: ERİŞİLEMİYOR (HTTP $ADMIN_RESPONSE)${NC}"
fi

echo "🎨 Static Files:"
STATIC_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" https://apphane.com.tr/static/css/style.css)
if [ "$STATIC_RESPONSE" = "200" ]; then
    echo -e "${GREEN}✅ Static Files: YÜKLENİYOR${NC}"
else
    echo -e "${YELLOW}⚠️ Static Files: Kontrol edilmeli (HTTP $STATIC_RESPONSE)${NC}"
fi
echo ""

# 7. LOG KONTROLLERI
echo -e "${BLUE}7. 📋 LOG KONTROLLERI${NC}"
echo "=================================="
echo "🔍 Son Django Logları (Son 10 satır):"
docker-compose logs --tail=10 web | grep -E "(ERROR|WARN|Exception)" || echo "Hata logu bulunamadı"
echo ""

echo "🔍 Son Nginx Logları (Son 5 satır):"
docker-compose logs --tail=5 nginx | grep -E "(error|warn)" || echo "Nginx hata logu bulunamadı"
echo ""

# 8. GÜVEN DUVARı VE GÜVENLİK
echo -e "${BLUE}8. 🛡️ GÜVENLİK KONTROLLERI${NC}"
echo "=================================="
echo "🔥 UFW Durum:"
sudo ufw status
echo ""

echo "🔐 Aktif SSH Bağlantıları:"
who
echo ""

echo "⚡ Son sistem logları (hata arayışı):"
journalctl --since "1 hour ago" --priority=err --no-pager | tail -5 || echo "Son 1 saatte sistem hatası yok"
echo ""

# 9. PERFORMANS ÖLÇÜMLERİ
echo -e "${BLUE}9. ⚡ PERFORMANS ÖLÇÜMLERİ${NC}"
echo "=================================="
echo "🚀 Site Yanıt Süresi Testi:"
echo "HTTP Yanıt Süresi: $(curl -s -o /dev/null -w "%{time_total}s" http://apphane.com.tr/health/)"
echo "HTTPS Yanıt Süresi: $(curl -s -k -o /dev/null -w "%{time_total}s" https://apphane.com.tr/health/)"
echo ""

echo "📈 Load Average:"
cat /proc/loadavg
echo ""

# 10. ÖZET RAPOR
echo -e "${BLUE}10. 📊 GENEL DURUM ÖZETİ${NC}"
echo "=================================="

# Kritik kontroller
CRITICAL_CHECKS=0
if ! docker-compose ps | grep -q "Up"; then ((CRITICAL_CHECKS++)); fi
if ! curl -s -f http://localhost:9000/health/ > /dev/null; then ((CRITICAL_CHECKS++)); fi
if ! curl -s -f https://apphane.com.tr/health/ > /dev/null; then ((CRITICAL_CHECKS++)); fi

if [ $CRITICAL_CHECKS -eq 0 ]; then
    echo -e "${GREEN}🎉 TÜM SİSTEMLER NORMAL ÇALIŞIYOR!${NC}"
    echo -e "${GREEN}✅ Site erişilebilir: https://apphane.com.tr${NC}"
    echo -e "${GREEN}✅ Tüm servisler aktif${NC}"
    echo -e "${GREEN}✅ SSL sertifikası geçerli${NC}"
else
    echo -e "${RED}⚠️ $CRITICAL_CHECKS KRITIK SORUN TESPIT EDİLDİ!${NC}"
    echo -e "${YELLOW}Yukarıdaki detayları kontrol edin ve gerekli düzeltmeleri yapın.${NC}"
fi

echo ""
echo "🔄 Bu kontrolü tekrarlamak için: ./server_health_check.sh"
echo "📞 Destek için: apphane.platform@gmail.com"
echo ""
echo "=================================="
echo "⏰ Kontrol tamamlandı: $(date)"
echo "=================================="
