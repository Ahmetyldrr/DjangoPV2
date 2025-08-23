# 🔍 SUNUCU SAĞLIK KONTROLÜ KOMUTLARI

## 🚀 Hızlı Kontrol (Tek Komut)

### Sunucuya bağlandıktan sonra:
```bash
cd /var/www/apphane
chmod +x server_health_check.sh
./server_health_check.sh
```

**Bu script otomatik olarak kontrol eder:**
- ✅ Sistem durumu (CPU, RAM, Disk)
- ✅ Docker servisleri
- ✅ Port durumları
- ✅ Site erişilebilirliği
- ✅ SSL sertifikası
- ✅ Database bağlantısı
- ✅ Redis durumu
- ✅ Log kontrolleri
- ✅ Güvenlik durumu

---

## 🔧 Manuel Kontrol Komutları

### 1. Docker Servisleri Kontrolü
```bash
# Tüm servislerin durumu
docker-compose ps

# Hangi portların açık olduğunu gör
ss -tlnp | grep -E ':80|:443|:9000|:9379'

# Container resource kullanımı
docker stats --no-stream
```

### 2. Site Erişim Kontrolleri
```bash
# Local Django health check
curl -f http://localhost:9000/health/

# Nginx üzerinden health check
curl -f http://localhost:8000/health/

# External HTTP test
curl -I http://apphane.com.tr

# External HTTPS test  
curl -I https://apphane.com.tr

# Admin panel kontrolü
curl -I https://apphane.com.tr/admin/
```

### 3. SSL Sertifika Kontrolleri
```bash
# SSL sertifikası var mı?
sudo certbot certificates

# Sertifika detayları
openssl x509 -in /etc/letsencrypt/live/apphane.com.tr/fullchain.pem -text -noout | grep -E "(Not Before|Not After)"

# SSL test
echo | openssl s_client -connect apphane.com.tr:443 -servername apphane.com.tr 2>/dev/null | openssl x509 -noout -dates
```

### 4. Database ve Redis Kontrolleri
```bash
# PostgreSQL bağlantı testi
docker-compose exec web python manage.py dbshell --command="SELECT version();"

# Redis bağlantı testi
docker-compose exec redis redis-cli ping

# Database migration durumu
docker-compose exec web python manage.py showmigrations
```

### 5. Log Kontrolleri
```bash
# Django aplikasyon logları
docker-compose logs web --tail=50

# Nginx logları  
docker-compose logs nginx --tail=20

# Hata logları arama
docker-compose logs web | grep -i error

# Real-time log takibi
docker-compose logs -f
```

### 6. Sistem Performans Kontrolleri
```bash
# Sistem kaynak kullanımı
htop

# Disk kullanımı
df -h

# RAM kullanımı
free -h

# CPU load
uptime

# Network bağlantıları
netstat -tlnp
```

### 7. Güvenlik Kontrolleri
```bash
# UFW güvenlik duvarı durumu
sudo ufw status

# Aktif bağlantılar
ss -tuln

# Son sistem logları
journalctl --since "1 hour ago" --priority=err

# Fail2ban durumu (varsa)
sudo fail2ban-client status
```

### 8. Hızlı Sorun Giderme
```bash
# Servisleri yeniden başlat
docker-compose restart

# Cache temizleme
docker-compose exec web python manage.py clear_cache

# Static files yeniden topla
docker-compose exec web python manage.py collectstatic --noinput

# Nginx konfigürasyon test
docker-compose exec nginx nginx -t

# Container'ları yeniden build et
docker-compose down && docker-compose up -d --build
```

---

## ⚡ Kritik Durum Kontrol Listesi

### ❌ Site erişilemiyor ise:
```bash
# 1. Docker servisleri çalışıyor mu?
docker-compose ps

# 2. Portlar açık mı?
ss -tlnp | grep ':80\|:443'

# 3. Health check çalışıyor mu?
curl http://localhost:9000/health/

# 4. Nginx çalışıyor mu?
docker-compose logs nginx
```

### ❌ HTTPS sorunu varsa:
```bash
# 1. SSL sertifikası var mı?
ls -la /etc/letsencrypt/live/apphane.com.tr/

# 2. Nginx SSL konfigürasyonu doğru mu?
docker-compose exec nginx nginx -t

# 3. SSL sertifikasını yenile
sudo certbot renew --force-renewal
```

### ❌ Database bağlantı sorunu:
```bash
# 1. PostgreSQL erişilebilir mi?
telnet 165.227.130.23 5432

# 2. Django database ayarları
docker-compose exec web python manage.py check --database default

# 3. Migration durumu
docker-compose exec web python manage.py showmigrations
```

---

## 📊 Başarı Göstergeleri

### ✅ **Her şey normal ise göreceğiniz değerler:**

- **Docker**: Tüm serviceler "Up" durumunda
- **HTTP Codes**: 200 (başarılı) veya 302 (redirect)  
- **SSL**: Geçerli sertifika, 30+ gün geçerlilik
- **Response Time**: <2 saniye
- **CPU Load**: <1.0 (ortalama)
- **RAM**: %80'den az kullanım
- **Disk**: %90'dan az kullanım

### ⚠️ **Dikkat gereken durumlar:**

- **HTTP 5xx**: Server hatası
- **HTTP 4xx**: Sayfa bulunamıyor  
- **SSL Expire**: <7 gün kaldıysa
- **High Load**: CPU >2.0
- **Low Memory**: RAM >%90
- **Disk Full**: >%95 doluysa

---

## 🔄 Otomatik İzleme Kurulumu

### Cron job ile otomatik kontrol:
```bash
# Her 5 dakikada health check
echo "*/5 * * * * /var/www/apphane/server_health_check.sh >> /var/log/health_check.log 2>&1" | crontab -

# Log dosyasını kontrol et
tail -f /var/log/health_check.log
```

---

**💡 İpucu:** İlk önce `./server_health_check.sh` komutunu çalıştırın. Bu size genel bir durum raporu verecek. Sorun varsa yukarıdaki manuel komutlarla detaylı inceleme yapın.
