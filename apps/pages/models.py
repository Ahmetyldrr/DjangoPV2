from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class ContactMessage(models.Model):
    """İletişim formu mesajları"""
    
    STATUS_CHOICES = [
        ('new', 'Yeni'),
        ('read', 'Okundu'),
        ('replied', 'Cevaplandı'),
        ('closed', 'Kapatıldı'),
    ]
    
    name = models.CharField('Ad Soyad', max_length=100)
    email = models.EmailField('E-posta')
    phone = models.CharField('Telefon', max_length=20, blank=True)
    subject = models.CharField('Konu', max_length=200)
    message = models.TextField('Mesaj')
    
    status = models.CharField('Durum', max_length=20, choices=STATUS_CHOICES, default='new')
    admin_reply = models.TextField('Admin Cevabı', blank=True)
    admin_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                  verbose_name='Cevaplayan Admin')
    
    created_at = models.DateTimeField('Oluşturulma', auto_now_add=True)
    updated_at = models.DateTimeField('Güncellenme', auto_now=True)
    read_at = models.DateTimeField('Okunma Tarihi', null=True, blank=True)
    replied_at = models.DateTimeField('Cevaplama Tarihi', null=True, blank=True)
    
    class Meta:
        verbose_name = 'İletişim Mesajı'
        verbose_name_plural = 'İletişim Mesajları'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.subject}"
    
    @property
    def is_new(self):
        return self.status == 'new'
    
    @property
    def is_urgent(self):
        # 24 saatten fazla cevapsız mesajlar acil
        from django.utils import timezone
        from datetime import timedelta
        return (timezone.now() - self.created_at) > timedelta(hours=24) and self.status == 'new'
