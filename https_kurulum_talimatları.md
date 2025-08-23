# HTTPS SSL Sertifikası Kurulum Talimatları
**Sunucu: 165.227.130.23 | Domain: apphane.com.tr**

## 🚀 Hızlı HTTPS Kurulumu

### 1. Sunucuya Bağlan
```bash
ssh root@165.227.130.23
cd /var/www/apphane
```

### 2. Yeni Dosyaları Çek
```bash
git pull origin main
```

### 3. SSL Kurulum Script'ini Çalıştır
```bash
chmod +x setup_ssl_production.sh
./setup_ssl_production.sh
```

Bu script otomatik olarak:
- ✅ Domain DNS kontrolü yapar
- ✅ Let's Encrypt SSL sertifikası oluşturur
- ✅ Nginx'i HTTPS için yapılandırır
- ✅ Django settings'i HTTPS için ayarlar
- ✅ Otomatik SSL yenileme kurar
- ✅ Güvenlik duvarını yapılandırır

## 🔧 Manuel Kurulum (İsteğe Bağlı)

### 1. Önce Docker'ı Durdur
```bash
docker-compose down
```

### 2. Certbot Kurulumu
```bash
sudo apt update
sudo snap install --classic certbot
sudo ln -sf /snap/bin/certbot /usr/bin/certbot
```

### 3. SSL Sertifikası Oluştur
```bash
sudo certbot certonly --standalone \
  --email admin@apphane.com.tr \
  --agree-tos \
  --domains apphane.com.tr,www.apphane.com.tr
```

### 4. Docker'ı HTTPS Konfigürasyonuyla Başlat
```bash
docker-compose up -d
```

## 📋 Kurulum Sonrası Kontroller

### 1. SSL Sertifikası Kontrolü
```bash
sudo certbot certificates
```

### 2. Servis Durumları
```bash
docker-compose ps
```

### 3. HTTPS Test
```bash
curl -I https://apphane.com.tr
curl -I https://apphane.com.tr/health/
```

### 4. HTTP -> HTTPS Yönlendirme Test
```bash
curl -I http://apphane.com.tr
# 301 veya 302 redirect beklenmelidir
```

## 🔒 Güvenlik Özellikleri

### Aktif Olan Güvenlik Önlemleri:
- ✅ **SSL/TLS Şifreleme**: Let's Encrypt sertifikası
- ✅ **HSTS (HTTP Strict Transport Security)**: 1 yıl
- ✅ **Secure Cookies**: HTTPS üzerinden cookie güvenliği
- ✅ **XSS Protection**: Browser XSS koruması
- ✅ **Content Type Sniffing Protection**: MIME type koruması
- ✅ **Frame Options**: Clickjacking koruması
- ✅ **CSRF Protection**: Cross-site request forgery koruması

### Django Settings (HTTPS):
```python
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

## 🔄 SSL Otomatik Yenileme

SSL sertifikası her gün saat 12:00'da otomatik olarak kontrol edilir ve gerekirse yenilenir:

```bash
# Crontab kontrolü
crontab -l

# Manuel yenileme testi
sudo certbot renew --dry-run
```

## 🌐 Erişim URL'leri

- **Ana Site**: https://apphane.com.tr
- **Admin Panel**: https://apphane.com.tr/admin/
- **Health Check**: https://apphane.com.tr/health/
- **Static Files**: https://apphane.com.tr/static/
- **Media Files**: https://apphane.com.tr/media/

## 🚨 Sorun Giderme

### SSL Sertifikası Sorunu
```bash
# Sertifika durumunu kontrol et
sudo certbot certificates

# Manuel sertifika yenileme
sudo certbot renew --force-renewal

# Docker'ı yeniden başlat
docker-compose restart
```

### Nginx Konfigürasyon Sorunu
```bash
# Nginx konfigürasyon test
docker-compose exec nginx nginx -t

# Nginx logları
docker-compose logs nginx
```

### Django HTTPS Sorunu
```bash
# Django logları
docker-compose logs web

# Environment variables kontrol
docker-compose exec web env | grep SECURE
```

### Port Sorunu
```bash
# Port kullanım kontrolü
sudo netstat -tlnp | grep ':80\|:443'

# UFW güvenlik duvarı durumu
sudo ufw status
```

## 📊 Performans Kontrolleri

### 1. SSL Lab Test
https://www.ssllabs.com/ssltest/analyze.html?d=apphane.com.tr

### 2. Security Headers Test
https://securityheaders.com/?q=apphane.com.tr

### 3. Site Hızı Test
https://pagespeed.web.dev/report?url=https://apphane.com.tr

## 💾 Backup ve Güvenlik

### 1. SSL Sertifika Backup
```bash
sudo cp -r /etc/letsencrypt/ /backup/letsencrypt-$(date +%Y%m%d)/
```

### 2. Database Backup
```bash
docker-compose exec db pg_dump -U username dbname > backup_$(date +%Y%m%d).sql
```

### 3. Proje Backup
```bash
tar -czf apphane-backup-$(date +%Y%m%d).tar.gz /var/www/apphane/
```

## ✅ Başarı Kriterleri

Kurulum başarılı ise aşağıdaki kontroller yeşil olmalıdır:

- [ ] https://apphane.com.tr erişilebilir
- [ ] http://apphane.com.tr otomatik olarak HTTPS'e yönlendiriyor
- [ ] SSL sertifikası geçerli (🔒 yeşil kilit ikonu)
- [ ] Health check çalışıyor: https://apphane.com.tr/health/
- [ ] Admin panel erişilebilir: https://apphane.com.tr/admin/
- [ ] Static dosyalar yükleniyor
- [ ] Browser'da güvenlik uyarısı yok

---

**🎉 HTTPS kurulumu tamamlandıktan sonra siteniz tamamen güvenli olacak!**
