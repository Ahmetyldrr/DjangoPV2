from django.core.management.base import BaseCommand
import os
from django.conf import settings


class Command(BaseCommand):
    help = 'Sistem loglarını görüntüle'

    def add_arguments(self, parser):
        parser.add_argument(
            '--tail',
            type=int,
            default=50,
            help='Son N satırı göster (default: 50)',
        )
        parser.add_argument(
            '--email-logs',
            action='store_true',
            help='Sadece email loglarını göster',
        )
        parser.add_argument(
            '--django-logs',
            action='store_true',
            help='Sadece Django loglarını göster',
        )
        parser.add_argument(
            '--follow',
            action='store_true',
            help='Log dosyasını canlı takip et',
        )

    def handle(self, *args, **options):
        logs_dir = os.path.join(settings.BASE_DIR, 'logs')
        
        if not os.path.exists(logs_dir):
            self.stdout.write(self.style.ERROR('❌ Logs klasörü bulunamadı!'))
            return
        
        if options['email_logs']:
            self.show_email_logs(logs_dir, options['tail'])
        elif options['django_logs']:
            self.show_django_logs(logs_dir, options['tail'])
        else:
            self.show_all_logs(logs_dir, options['tail'])

    def show_email_logs(self, logs_dir, tail_count):
        """Email loglarını göster"""
        email_log_file = os.path.join(logs_dir, 'chat_emails.log')
        
        self.stdout.write('📧 EMAIL LOGLARI:')
        self.stdout.write('=' * 50)
        
        if os.path.exists(email_log_file):
            self.show_log_file(email_log_file, tail_count)
        else:
            self.stdout.write(self.style.WARNING('⚠️ Email log dosyası bulunamadı'))

    def show_django_logs(self, logs_dir, tail_count):
        """Django loglarını göster"""
        django_log_file = os.path.join(logs_dir, 'django.log')
        
        self.stdout.write('🐍 DJANGO LOGLARI:')
        self.stdout.write('=' * 50)
        
        if os.path.exists(django_log_file):
            self.show_log_file(django_log_file, tail_count)
        else:
            self.stdout.write(self.style.WARNING('⚠️ Django log dosyası bulunamadı'))

    def show_all_logs(self, logs_dir, tail_count):
        """Tüm logları göster"""
        self.stdout.write('📊 TÜM SİSTEM LOGLARI:')
        self.stdout.write('=' * 50)
        
        # Email logs
        self.show_email_logs(logs_dir, tail_count)
        
        self.stdout.write('\n' + '-' * 50 + '\n')
        
        # Django logs
        self.show_django_logs(logs_dir, tail_count)

    def show_log_file(self, file_path, tail_count):
        """Log dosyasının son N satırını göster"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            if not lines:
                self.stdout.write(self.style.WARNING('📄 Log dosyası boş'))
                return
            
            # Son N satırı al
            recent_lines = lines[-tail_count:] if len(lines) > tail_count else lines
            
            self.stdout.write(f'📋 Son {len(recent_lines)} satır:')
            self.stdout.write('-' * 30)
            
            for line in recent_lines:
                line = line.strip()
                if line:
                    # Log seviyesine göre renklendirme
                    if 'ERROR' in line:
                        self.stdout.write(self.style.ERROR(line))
                    elif 'WARNING' in line:
                        self.stdout.write(self.style.WARNING(line))
                    elif 'SUCCESS' in line or '✅' in line:
                        self.stdout.write(self.style.SUCCESS(line))
                    else:
                        self.stdout.write(line)
            
            self.stdout.write(f'\n📁 Dosya: {file_path}')
            self.stdout.write(f'📏 Toplam satır: {len(lines)}')
                        
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'❌ Log dosyası bulunamadı: {file_path}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Log dosyası okunamadı: {str(e)}'))
