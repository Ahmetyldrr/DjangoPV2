#!/bin/bash

# Sunucuda çalıştırılacak komutlar

# 1. Public key'i authorized_keys'e ekle
echo "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQDP+Rr8E6CSLfzuI4E26STdpBMEAJ9zyxICboabHdQWf94MZQnpyEiF7q1Krk157+EHgPge5V1Zegadl0oRUgzRh7ue4uiYH8eU7rW4T6QcdnF9NhFiCHKJT84xXhwqG9agExfCDgPInj2ESe37dBbEEKG/PHKFB4PlIZqG4VKGeptbI65LURQ5VEKpZ0WYBJeWFXTZHrWB7B6b6BoHrieKGKthTf72igTYkch1T6Jv8sWYpULp1JNmyLEjKbzmFCm1KgGM8Z3VdYl595X/31GRFRDE0tu6+FkrvnuWKxzDP0iinTo/ACb8LferDPecj0DzP+EwIm19u7+1Kow6Tb8HjmCrT1h+iAy2I3Re5NmWHEc+2cpBPqVtlhMa3oVAO70PM/Sj2dDzF/z6I2Fmn3HsSrg5PPXiWqYbeOPzQWB3GGbRG1gQPfBnC9E52ef2nGgYYvDX2KYTkKeai9AcAhAB5fQYTonwHbTEgk8zhbdZf1z3dwksQhDZJniChNo8Hr66sAtLl2ZIttXWA5p6Diwxgas9vs2JEcEQcIb+xKsDbe0ntFzrlDJmaOIR13x6WybHDB9Tg2aU440zsJQGzotNuw1UG3BD1gLWViWK/jFFYYTCpBW7/Uyf7cqFvOWEzqx3SJP6Rcy92hflnlZjVWoXqn9z9ko4B6aZK41S8TU7Vw== github-actions@apphane.com.tr" >> ~/.ssh/authorized_keys

# 2. Proje dizinini oluştur
sudo mkdir -p /var/www/apphane
sudo chown root:root /var/www/apphane

# 3. Git ayarları
cd /var/www/apphane
git config --global --add safe.directory /var/www/apphane

echo "✅ SSH key eklendi!"
echo "✅ Proje dizini oluşturuldu!"
echo "✅ Git ayarları yapıldı!"
echo ""
echo "🚀 Şimdi GitHub Actions çalıştırılabilir!"
