#!/bin/bash
# Emergency Deployment Fix Script
# apphane.com.tr için 502 Bad Gateway sorununu çözer

echo "🚨 EMERGENCY DEPLOYMENT FIX BAŞLIYOR..."
echo "================================================"

cd /var/www/apphane

echo "📊 Mevcut durum kontrolü:"
echo "Docker containers:"
docker-compose ps

echo "📋 Web container logs (son 20 satır):"
docker-compose logs --tail=20 web

echo "🔄 Containers'ları yeniden başlatıyoruz..."

# Stop all containers
docker-compose down --timeout 30

# Clean up
docker container prune -f
docker system prune -f

# Pull latest code
git stash
git pull origin main

# Use simple compose file
cp docker-compose-simple.yml docker-compose.yml

# Rebuild and start
echo "🔨 Rebuilding containers..."
docker-compose build web

echo "🚀 Starting services..."
docker-compose up -d

echo "⏳ Waiting for services..."
sleep 30

echo "📊 New container status:"
docker-compose ps

# Test Django directly
echo "🔍 Testing Django management:"
if docker-compose exec -T web python manage.py check; then
    echo "✅ Django management commands OK"
else
    echo "❌ Django management commands FAILED"
    echo "Container logs:"
    docker-compose logs web
fi

# Test HTTP endpoint
echo "🔍 Testing HTTP endpoint:"
if curl -f http://localhost:9000/health/; then
    echo "✅ Django HTTP endpoint OK"
else
    echo "❌ Django HTTP endpoint FAILED"
    echo "Port check:"
    netstat -tulpn | grep 9000
fi

# Restart Nginx
echo "🔄 Restarting Nginx..."
systemctl restart nginx
systemctl status nginx --no-pager | head -10

# Test HTTPS site
echo "🔍 Testing HTTPS site:"
if curl -f https://apphane.com.tr/; then
    echo "✅ HTTPS site working"
else
    echo "❌ HTTPS site failed"
fi

echo "================================================"
echo "🎯 EMERGENCY FIX TAMAMLANDI"
echo "Site: https://apphane.com.tr"
echo "Admin: https://apphane.com.tr/admin/"
echo "Health: https://apphane.com.tr/health/"
echo "================================================"
