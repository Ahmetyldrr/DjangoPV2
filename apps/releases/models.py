from django.db import models
from django.urls import reverse
from apps.catalog.models import Application


class Release(models.Model):
    CHANNEL_CHOICES = [
        ('test', 'Test'),
        ('stable', 'Kararlı'),
    ]
    
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='releases', verbose_name="Uygulama")
    version = models.CharField(max_length=50, verbose_name="Sürüm")
    channel = models.CharField(max_length=10, choices=CHANNEL_CHOICES, default='stable', verbose_name="Kanal")
    file = models.FileField(upload_to='releases/', verbose_name="Dosya")
    file_size = models.BigIntegerField(verbose_name="Dosya Boyutu (Byte)")
    sha256 = models.CharField(max_length=64, verbose_name="SHA256 Hash")
    changelog_markdown = models.TextField(blank=True, verbose_name="Değişiklik Listesi (Markdown)")
    is_active = models.BooleanField(default=True, verbose_name="Aktif")
    published_at = models.DateTimeField(auto_now_add=True, verbose_name="Yayınlanma Tarihi")
    download_count = models.PositiveIntegerField(default=0, verbose_name="İndirme Sayısı")
    
    class Meta:
        verbose_name = "Sürüm"
        verbose_name_plural = "Sürümler"
        ordering = ['-published_at']
        unique_together = ['application', 'version']
    
    def __str__(self):
        return f"{self.application.title} - {self.version} ({self.get_channel_display()})"
    
    def get_download_url(self):
        return reverse('releases:download', kwargs={'pk': self.pk})
    
    def get_file_size_mb(self):
        return round(self.file_size / (1024 * 1024), 2)
    
    def get_channel_badge_class(self):
        return 'badge-warning' if self.channel == 'test' else 'badge-success'
