#!/bin/bash

# SSL Sertifikası Kurulum Scripti
# Let's Encrypt ile ücretsiz SSL sertifikası

echo "🔒 SSL Sertifikası kuruluyor..."

# Certbot kurulumu
apt update
apt install -y certbot

# Domain için SSL sertifikası al
certbot certonly --standalone \
  --email ahmetyildirir1@gmail.com \
  --agree-tos \
  --no-eff-email \
  -d apphane.com.tr \
  -d www.apphane.com.tr

# Sertifika yenileme için cron job
echo "0 12 * * * /usr/bin/certbot renew --quiet" | crontab -

echo "✅ SSL Sertifikası kuruldu!"
echo "📍 Sertifika konumu: /etc/letsencrypt/live/apphane.com.tr/"
