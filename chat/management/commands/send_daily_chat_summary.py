from django.core.management.base import BaseCommand
from chat.email_notifications import send_admin_daily_chat_summary


class Command(BaseCommand):
    help = 'Admin\'lere günlük chat özeti gönder'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Aktivite olmasa bile özet gönder',
        )

    def handle(self, *args, **options):
        force = options['force']
        
        self.stdout.write(
            self.style.SUCCESS('Günlük chat özeti gönderiliyor...')
        )
        
        # Email gönder
        success = send_admin_daily_chat_summary()
        
        if success:
            self.stdout.write(
                self.style.SUCCESS('✅ Günlük chat özeti başarıyla gönderildi!')
            )
        else:
            if force:
                self.stdout.write(
                    self.style.WARNING('⚠️ Günlük özet gönderilemedi (aktivite yok veya hata)')
                )
            else:
                self.stdout.write(
                    self.style.WARNING('ℹ️ Günlük özet gönderilmedi (aktivite yok)')
                )
