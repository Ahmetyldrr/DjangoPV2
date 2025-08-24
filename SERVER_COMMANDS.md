# APPHANE SUNUCU YÖNETİM KOMUTLARI
# ===================================

# SSH Bağlantısı:
ssh root@165.227.130.23

# Email Debug Komutları:
cd /var/www/apphane
docker-compose exec web python manage.py debug_emails --check-settings
docker-compose exec web python manage.py debug_emails --test-basic
docker-compose exec web python manage.py debug_emails --create-test-message

# Log Komutları:
docker-compose exec web python manage.py show_logs --email-logs
docker-compose exec web python manage.py show_logs --django-logs
docker-compose exec web python manage.py show_logs --tail 100

# Chat Test Komutları:
docker-compose exec web python manage.py test_chat_notifications --test-message
docker-compose exec web python manage.py test_chat_notifications --list-recent

# Container Durumu:
docker-compose ps
docker-compose logs web --tail=50
docker-compose logs web -f  # Canlı takip

# Email Monitoring Script:
./monitor_email_system.sh

# Django Shell ile Manuel Test:
docker-compose exec web python manage.py shell
>>> from django.core.mail import send_mail
>>> send_mail('Test', 'Test mesajı', 'apphane.platform@gmail.com', ['apphane.platform@gmail.com'])

# Log Dosyalarını Direkt Okuma:
docker-compose exec web cat logs/chat_emails.log
docker-compose exec web tail -f logs/chat_emails.log  # Canlı takip

# Nginx Log Kontrolü:
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log

# Sistem Durumu:
systemctl status nginx
systemctl status docker
df -h  # Disk kullanımı
free -m  # RAM kullanımı

# Website Test:
curl -I https://apphane.com.tr
curl -I https://apphane.com.tr/health/
curl -I https://apphane.com.tr/admin/

# Admin Panel Dashboard:
# https://apphane.com.tr/admin/system-dashboard/

# Email Test URL'leri:
# https://apphane.com.tr/admin/system-dashboard/
# https://apphane.com.tr/admin/test-email/

# Crontab Email Özeti (İsteğe bağlı):
# 0 20 * * * cd /var/www/apphane && docker-compose exec web python manage.py send_daily_chat_summary
