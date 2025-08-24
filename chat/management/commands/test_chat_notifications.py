from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from chat.models import Message, ChatRoom
from chat.email_notifications import send_new_message_notification
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


class Command(BaseCommand):
    help = 'Test email bildirimleri'

    def add_arguments(self, parser):
        parser.add_argument(
            '--test-message',
            action='store_true',
            help='Test mesaj bildirimi gönder',
        )
        parser.add_argument(
            '--list-recent',
            action='store_true',
            help='Son mesajları listele',
        )

    def handle(self, *args, **options):
        if options['test_message']:
            self.test_message_notification()
        
        if options['list_recent']:
            self.list_recent_messages()

    def test_message_notification(self):
        """Test mesaj bildirimi gönder"""
        self.stdout.write('📧 Test email bildirimi gönderiliyor...')
        
        # Son mesajı al
        recent_message = Message.objects.order_by('-created_at').first()
        
        if not recent_message:
            self.stdout.write(
                self.style.WARNING('❌ Test için mesaj bulunamadı')
            )
            return
        
        # Test bildirimi gönder
        success = send_new_message_notification(recent_message)
        
        if success:
            self.stdout.write(
                self.style.SUCCESS(f'✅ Test bildirimi gönderildi! Mesaj ID: {recent_message.id}')
            )
        else:
            self.stdout.write(
                self.style.ERROR('❌ Test bildirimi gönderilemedi')
            )

    def list_recent_messages(self):
        """Son mesajları listele"""
        self.stdout.write('📋 Son 10 mesaj:')
        
        recent_messages = Message.objects.order_by('-created_at')[:10]
        
        for i, msg in enumerate(recent_messages, 1):
            self.stdout.write(
                f'{i}. {msg.sender.get_full_name()}: {msg.content[:50]}... '
                f'({msg.created_at.strftime("%d/%m/%Y %H:%M")})'
            )
