from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils import timezone


class ChatRoom(models.Model):
    """Chat odası - iki kullanıcı arasındaki konuşma"""
    
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='chat_rooms')
    name = models.CharField('Oda Adı', max_length=255, blank=True)
    created_at = models.DateTimeField('Oluşturulma Tarihi', auto_now_add=True)
    updated_at = models.DateTimeField('Son Güncelleme', auto_now=True)
    
    class Meta:
        verbose_name = 'Chat Odası'
        verbose_name_plural = 'Chat Odaları'
        ordering = ['-updated_at']
    
    def __str__(self):
        if self.name:
            return self.name
        participants = list(self.participants.all())
        if len(participants) >= 2:
            return f"{participants[0].get_full_name()} - {participants[1].get_full_name()}"
        return f"Chat {self.id}"
    
    def get_absolute_url(self):
        return reverse('chat:room', kwargs={'room_id': self.id})
    
    def get_other_participant(self, user):
        """Karşı taraftaki kullanıcıyı getir"""
        return self.participants.exclude(id=user.id).first()
    
    def get_last_message(self):
        """Son mesajı getir"""
        return self.messages.first()


class Message(models.Model):
    """Chat mesajı"""
    
    MESSAGE_TYPE_CHOICES = [
        ('text', 'Metin'),
        ('image', 'Görsel'),
        ('file', 'Dosya'),
        ('offer', 'Teklif'),
    ]
    
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    
    message_type = models.CharField('Mesaj Tipi', max_length=20, choices=MESSAGE_TYPE_CHOICES, default='text')
    content = models.TextField('İçerik')
    
    # Dosya/görsel için
    attachment = models.FileField('Ek Dosya', upload_to='chat/attachments/', blank=True, null=True)
    
    # Mesaj durumu
    is_read = models.BooleanField('Okundu', default=False)
    read_at = models.DateTimeField('Okunma Tarihi', blank=True, null=True)
    
    created_at = models.DateTimeField('Gönderilme Tarihi', auto_now_add=True)
    updated_at = models.DateTimeField('Güncellenme Tarihi', auto_now=True)
    
    class Meta:
        verbose_name = 'Mesaj'
        verbose_name_plural = 'Mesajlar'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.sender.get_full_name()}: {self.content[:50]}"
    
    def mark_as_read(self):
        """Mesajı okundu olarak işaretle"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])


class ProjectOffer(models.Model):
    """Proje teklifi - chat içinden gönderilebilir"""
    
    STATUS_CHOICES = [
        ('pending', 'Beklemede'),
        ('accepted', 'Kabul Edildi'),
        ('rejected', 'Reddedildi'),
        ('cancelled', 'İptal Edildi'),
    ]
    
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_offers')
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_offers')
    chat_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='offers')
    message = models.OneToOneField(Message, on_delete=models.CASCADE, related_name='offer', blank=True, null=True)
    
    title = models.CharField('Proje Başlığı', max_length=200)
    description = models.TextField('Proje Açıklaması')
    budget = models.DecimalField('Bütçe (TL)', max_digits=10, decimal_places=2)
    deadline = models.DateField('Teslim Tarihi')
    
    status = models.CharField('Durum', max_length=20, choices=STATUS_CHOICES, default='pending')
    
    created_at = models.DateTimeField('Oluşturulma Tarihi', auto_now_add=True)
    updated_at = models.DateTimeField('Güncellenme Tarihi', auto_now=True)
    
    class Meta:
        verbose_name = 'Proje Teklifi'
        verbose_name_plural = 'Proje Teklifleri'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.sender.get_full_name()} → {self.receiver.get_full_name()}"
