from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import Message, ChatRoom, ProjectOffer
from .email_notifications import (
    send_new_message_notification,
    send_support_chat_notification,
    send_project_offer_notification
)
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Message)
def send_message_notification(sender, instance, created, **kwargs):
    """
    Yeni mesaj oluşturulduğunda admin'e bildirim gönder
    """
    if not created:
        return  # Sadece yeni mesajlar için
    
    try:
        # Eğer mesajı admin gönderiyorsa bildirim gönderme
        if instance.sender.is_superuser or getattr(instance.sender, 'user_type', None) == 'admin':
            return
        
        # Email bildirimini gönder
        send_new_message_notification(instance)
        
    except Exception as e:
        logger.error(f"Failed to send message notification: {str(e)}")


@receiver(post_save, sender=ChatRoom)
def send_support_chat_created_notification(sender, instance, created, **kwargs):
    """
    Yeni destek chat odası oluşturulduğunda admin'e bildirim gönder
    """
    if not created:
        return
    
    try:
        # Sadece destek chat'leri için (adında "Destek" geçenler)
        if not instance.name or 'Destek' not in instance.name:
            return
        
        # İlk mesajı bul
        first_message = instance.messages.first()
        
        # Email bildirimini gönder
        send_support_chat_notification(instance, first_message)
        
    except Exception as e:
        logger.error(f"Failed to send support chat notification: {str(e)}")


@receiver(post_save, sender=ProjectOffer)
def send_project_offer_created_notification(sender, instance, created, **kwargs):
    """
    Yeni proje teklifi oluşturulduğunda admin'e bildirim gönder
    """
    if not created:
        return
    
    try:
        # Email bildirimini gönder
        send_project_offer_notification(instance)
        
    except Exception as e:
        logger.error(f"Failed to send project offer notification: {str(e)}")


# Chat mesajı okunduğunda bildirim (isteğe bağlı)
@receiver(post_save, sender=Message)
def log_message_read(sender, instance, created, **kwargs):
    """
    Mesaj okunduğunda log tut
    """
    if not created and instance.is_read and instance.read_at:
        logger.info(f"Message {instance.id} marked as read by recipient")
