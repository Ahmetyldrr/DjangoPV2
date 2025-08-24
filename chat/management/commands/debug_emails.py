from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from chat.email_notifications import send_new_message_notification
from chat.models import Message, ChatRoom
from django.contrib.auth import get_user_model
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


class Command(BaseCommand):
    help = 'Email sistemi debug ve test komutu'

    def add_arguments(self, parser):
        parser.add_argument(
            '--test-basic',
            action='store_true',
            help='Basit email testi',
        )
        parser.add_argument(
            '--test-notification',
            action='store_true',
            help='Chat bildirim testi',
        )
        parser.add_argument(
            '--check-settings',
            action='store_true',
            help='Email ayarlarını kontrol et',
        )
        parser.add_argument(
            '--create-test-message',
            action='store_true',
            help='Test mesajı oluştur ve bildirim gönder',
        )

    def handle(self, *args, **options):
        self.stdout.write('🔍 EMAIL DEBUG MODU BAŞLATILIYOR...')
        self.stdout.write('=' * 50)
        
        if options['check_settings']:
            self.check_email_settings()
        
        if options['test_basic']:
            self.test_basic_email()
        
        if options['test_notification']:
            self.test_notification_system()
        
        if options['create_test_message']:
            self.create_test_message()

    def check_email_settings(self):
        """Email ayarlarını kontrol et"""
        self.stdout.write('\n📧 EMAIL AYARLARI:')
        self.stdout.write('-' * 30)
        
        # Basic settings
        self.stdout.write(f'EMAIL_BACKEND: {getattr(settings, "EMAIL_BACKEND", "Not set")}')
        self.stdout.write(f'EMAIL_HOST: {getattr(settings, "EMAIL_HOST", "Not set")}')
        self.stdout.write(f'EMAIL_PORT: {getattr(settings, "EMAIL_PORT", "Not set")}')
        self.stdout.write(f'EMAIL_USE_TLS: {getattr(settings, "EMAIL_USE_TLS", "Not set")}')
        self.stdout.write(f'EMAIL_HOST_USER: {getattr(settings, "EMAIL_HOST_USER", "Not set")}')
        self.stdout.write(f'EMAIL_HOST_PASSWORD: {"Set" if getattr(settings, "EMAIL_HOST_PASSWORD", "") else "Not set"}')
        self.stdout.write(f'DEFAULT_FROM_EMAIL: {getattr(settings, "DEFAULT_FROM_EMAIL", "Not set")}')
        
        # Chat settings
        self.stdout.write(f'\n🔔 CHAT AYARLARI:')
        self.stdout.write(f'CHAT_ADMIN_EMAIL_NOTIFICATIONS: {getattr(settings, "CHAT_ADMIN_EMAIL_NOTIFICATIONS", "Not set")}')
        admin_emails = getattr(settings, "CHAT_ADMIN_EMAILS", [])
        self.stdout.write(f'CHAT_ADMIN_EMAILS: {admin_emails}')
        
        # ADMINS setting
        admins = getattr(settings, "ADMINS", [])
        self.stdout.write(f'ADMINS: {admins}')

    def test_basic_email(self):
        """Basit email testi"""
        self.stdout.write('\n📤 BASIT EMAIL TESTI:')
        self.stdout.write('-' * 30)
        
        try:
            admin_emails = getattr(settings, 'CHAT_ADMIN_EMAILS', [])
            if not admin_emails:
                admin_emails = [email for name, email in getattr(settings, 'ADMINS', [])]
            
            if not admin_emails:
                self.stdout.write(self.style.ERROR('❌ Admin email bulunamadı!'))
                return
            
            subject = '🧪 Test Email - Apphane Debug'
            message = '''
Bu bir test email'idir.

Email sistemi çalışıyor ise bu mesajı alacaksınız.

Debug bilgileri:
- Gönderen: Django Debug System
- Zaman: Şimdi
- Sistem: Apphane.com.tr

Eğer bu email'i aldıysanız, email sistemi çalışıyor demektir.
            '''
            
            self.stdout.write(f'📧 Gönderiliyor: {admin_emails[0]}')
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[admin_emails[0]],
                fail_silently=False,
            )
            
            self.stdout.write(self.style.SUCCESS('✅ Test email gönderildi!'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Email gönderilemedi: {str(e)}'))
            logger.error(f'Test email failed: {str(e)}')

    def test_notification_system(self):
        """Chat bildirim sistemini test et"""
        self.stdout.write('\n🔔 CHAT BİLDİRİM TESİ:')
        self.stdout.write('-' * 30)
        
        # Son mesajı al
        recent_message = Message.objects.order_by('-created_at').first()
        
        if not recent_message:
            self.stdout.write(self.style.WARNING('⚠️ Test için mesaj bulunamadı'))
            return
        
        self.stdout.write(f'📋 Test Mesajı:')
        self.stdout.write(f'   Gönderen: {recent_message.sender.get_full_name()}')
        self.stdout.write(f'   İçerik: {recent_message.content[:50]}...')
        self.stdout.write(f'   Tarih: {recent_message.created_at}')
        
        try:
            success = send_new_message_notification(recent_message)
            
            if success:
                self.stdout.write(self.style.SUCCESS('✅ Chat bildirimi gönderildi!'))
            else:
                self.stdout.write(self.style.WARNING('⚠️ Chat bildirimi gönderilemedi'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Chat bildirim hatası: {str(e)}'))
            logger.error(f'Chat notification test failed: {str(e)}')

    def create_test_message(self):
        """Test mesajı oluştur ve bildirim gönder"""
        self.stdout.write('\n💬 TEST MESAJI OLUŞTURULUYOR:')
        self.stdout.write('-' * 30)
        
        try:
            # Admin olmayan bir kullanıcı bul
            test_user = User.objects.exclude(is_superuser=True).exclude(user_type='admin').first()
            
            if not test_user:
                self.stdout.write(self.style.WARNING('⚠️ Test kullanıcısı bulunamadı'))
                return
            
            # Admin kullanıcı bul
            admin_user = User.objects.filter(is_superuser=True).first()
            
            if not admin_user:
                self.stdout.write(self.style.WARNING('⚠️ Admin kullanıcısı bulunamadı'))
                return
            
            # Chat odası oluştur veya bul
            chat_room = ChatRoom.objects.filter(
                participants=test_user
            ).filter(
                participants=admin_user
            ).first()
            
            if not chat_room:
                chat_room = ChatRoom.objects.create(
                    name=f"Debug Test Chat - {test_user.get_full_name()}"
                )
                chat_room.participants.set([test_user, admin_user])
            
            # Test mesajı oluştur
            test_message = Message.objects.create(
                room=chat_room,
                sender=test_user,
                content=f"🧪 Bu bir DEBUG test mesajıdır. Email sistemi test ediliyor. Zaman: {timezone.now()}",
                message_type='text'
            )
            
            self.stdout.write(f'✅ Test mesajı oluşturuldu (ID: {test_message.id})')
            
            # Bildirim gönder
            success = send_new_message_notification(test_message)
            
            if success:
                self.stdout.write(self.style.SUCCESS('✅ Test mesajı bildirimi gönderildi!'))
                self.stdout.write(f'📧 Admin email\'ine bildirim gitti')
            else:
                self.stdout.write(self.style.ERROR('❌ Test mesajı bildirimi gönderilemedi'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Test mesajı oluşturulamadı: {str(e)}'))
            logger.error(f'Test message creation failed: {str(e)}')


# Timezone import ekleyelim
from django.utils import timezone
