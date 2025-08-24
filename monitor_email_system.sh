#!/bin/bash
# Sunucu Email Monitoring Script
# apphane.com.tr - Email sistem durumu kontrolü

echo "🔍 APPHANE EMAIL SİSTEM KONTROLÜ"
echo "================================="
echo "Tarih: $(date)"
echo "Server: $(hostname)"
echo ""

# Django konteyner durumu
echo "📦 DOCKER CONTAINER DURUMU:"
echo "-----------------------------"
cd /var/www/apphane
docker-compose ps

echo ""
echo "📧 EMAIL AYARLARI KONTROLÜ:"
echo "-----------------------------"
docker-compose exec web python manage.py debug_emails --check-settings

echo ""
echo "🧪 BASİT EMAIL TESİ:"
echo "-----------------------------"
docker-compose exec web python manage.py debug_emails --test-basic

echo ""
echo "📋 SON EMAIL LOGLARI:"
echo "-----------------------------"
docker-compose exec web python manage.py show_logs --email-logs --tail 20

echo ""
echo "📊 CHAT İSTATİSTİKLERİ:"
echo "-----------------------------"
docker-compose exec web python manage.py shell << 'EOF'
from chat.models import Message, ChatRoom
from django.utils import timezone
from datetime import timedelta

# Son 24 saatin istatistikleri
yesterday = timezone.now() - timedelta(days=1)
messages_24h = Message.objects.filter(created_at__gte=yesterday).count()
chats_24h = ChatRoom.objects.filter(created_at__gte=yesterday).count()

print(f"🔢 Son 24 Saatte:")
print(f"   Mesajlar: {messages_24h}")
print(f"   Yeni Chat'ler: {chats_24h}")
print(f"   Toplam Mesaj: {Message.objects.count()}")
print(f"   Toplam Chat: {ChatRoom.objects.count()}")
EOF

echo ""
echo "🔄 SİSTEM SERVİSLERİ:"
echo "-----------------------------"
echo "Nginx Status:"
systemctl is-active nginx

echo "Docker Status:"
systemctl is-active docker

echo ""
echo "📁 LOG DOSYA BOYUTLARI:"
echo "-----------------------------"
if docker-compose exec web ls -la logs/ 2>/dev/null; then
    docker-compose exec web ls -lah logs/
else
    echo "⚠️ Logs klasörü bulunamadı"
fi

echo ""
echo "🌐 WEBSITE DURUMU:"
echo "-----------------------------"
if curl -s -o /dev/null -w "%{http_code}" https://apphane.com.tr | grep -q "200"; then
    echo "✅ Website çalışıyor (200 OK)"
else
    echo "❌ Website sorunu var"
fi

if curl -s -o /dev/null -w "%{http_code}" https://apphane.com.tr/health/ | grep -q "200"; then
    echo "✅ Health check OK"
else
    echo "❌ Health check problemi"
fi

echo ""
echo "================================="
echo "Email Monitoring Tamamlandı"
echo "$(date)"
