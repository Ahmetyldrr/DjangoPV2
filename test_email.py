#!/usr/bin/env python3
"""
Gmail SMTP Test Script
E-posta gönderim sistemini test eder
"""

import os
import django
from django.core.mail import send_mail
from django.conf import settings

# Django ayarlarını yükle
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

def test_email():
    """E-posta gönderim testini yapar"""
    
    print("📧 Gmail SMTP E-posta Testi")
    print("=" * 40)
    
    try:
        # Test e-postası gönder
        result = send_mail(
            subject='🧪 Apphane E-posta Sistemi Test',
            message='''
Merhaba,

Bu bir test e-postasıdır. 

✅ Gmail SMTP başarıyla çalışıyor!
🌐 Gönderildiği site: https://apphane.com.tr
📨 Gönderen: Apphane Team
📅 Tarih: %(date)s

Bu e-postayı aldıysanız, e-posta sisteminiz düzgün çalışıyor demektir.

İyi çalışmalar!
Apphane Team
            ''' % {'date': 'Bugün'},
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.CONTACT_EMAIL],
            fail_silently=False,
        )
        
        if result:
            print("✅ E-posta başarıyla gönderildi!")
            print(f"📤 Gönderen: {settings.DEFAULT_FROM_EMAIL}")
            print(f"📥 Alıcı: {settings.CONTACT_EMAIL}")
            print(f"📊 SMTP Host: {settings.EMAIL_HOST}")
            print("\n💡 Gmail SMTP sisteminiz çalışıyor!")
        else:
            print("❌ E-posta gönderilemedi!")
            
    except Exception as e:
        print(f"❌ HATA: {str(e)}")
        print("\n🔧 Olası Çözümler:")
        print("1. Gmail'de 2-Factor Authentication açık olmalı")
        print("2. App Password oluşturulmuş olmalı") 
        print("3. .env dosyasında EMAIL_HOST_PASSWORD doğru olmalı")

if __name__ == "__main__":
    test_email()
