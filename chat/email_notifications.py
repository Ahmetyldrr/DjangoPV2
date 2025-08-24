from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import reverse
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


def send_new_message_notification(message):
    """
    Yeni mesaj geldiğinde admin'lere email bildirim gönder
    """
    if not getattr(settings, 'CHAT_ADMIN_EMAIL_NOTIFICATIONS', False):
        return False
    
    try:
        # Admin email listesini al
        admin_emails = getattr(settings, 'CHAT_ADMIN_EMAILS', [])
        if not admin_emails:
            # Fallback: ADMINS setting'inden al
            admin_emails = [email for name, email in getattr(settings, 'ADMINS', [])]
        
        if not admin_emails:
            logger.warning("No admin emails configured for chat notifications")
            return False
        
        # Mesaj bilgileri
        sender = message.sender
        room = message.room
        other_participant = room.get_other_participant(sender)
        
        # Email içeriği
        subject = f"🔔 Yeni Mesaj: {sender.get_full_name()}"
        
        # Email context
        context = {
            'sender': sender,
            'message': message,
            'room': room,
            'other_participant': other_participant,
            'site_url': 'https://apphane.com.tr',
            'chat_url': f"https://apphane.com.tr{room.get_absolute_url()}",
        }
        
        # HTML email içeriği
        html_content = render_to_string('chat/emails/new_message_notification.html', context)
        
        # Plain text email içeriği
        text_content = f"""
Yeni Mesaj Bildirimi - Apphane.com.tr

Gönderen: {sender.get_full_name()} ({sender.email})
Mesaj: {message.content[:100]}{'...' if len(message.content) > 100 else ''}

Chat'i görüntülemek için: {context['chat_url']}

Admin Paneli: https://apphane.com.tr/admin/chat/message/{message.id}/change/

--
Bu otomatik bir bildirimdir.
Apphane Platform
        """
        
        # Email gönder
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=admin_emails,
        )
        email.attach_alternative(html_content, "text/html")
        email.send()
        
        logger.info(f"New message notification sent to {len(admin_emails)} admins for message {message.id}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send new message notification: {str(e)}")
        return False


def send_support_chat_notification(chat_room, first_message):
    """
    Yeni destek chat'i başlatıldığında admin'lere bildirim gönder
    """
    if not getattr(settings, 'CHAT_ADMIN_EMAIL_NOTIFICATIONS', False):
        return False
    
    try:
        admin_emails = getattr(settings, 'CHAT_ADMIN_EMAILS', [])
        if not admin_emails:
            admin_emails = [email for name, email in getattr(settings, 'ADMINS', [])]
        
        if not admin_emails:
            return False
        
        user = chat_room.participants.exclude(
            is_superuser=True
        ).exclude(
            user_type='admin'
        ).first()
        
        if not user:
            return False
        
        subject = f"🆘 Yeni Destek Talebi: {user.get_full_name()}"
        
        context = {
            'user': user,
            'chat_room': chat_room,
            'first_message': first_message,
            'site_url': 'https://apphane.com.tr',
            'chat_url': f"https://apphane.com.tr{chat_room.get_absolute_url()}",
        }
        
        html_content = render_to_string('chat/emails/support_chat_notification.html', context)
        
        text_content = f"""
Yeni Destek Chat Talebi - Apphane.com.tr

Kullanıcı: {user.get_full_name()} ({user.email})
Kullanıcı Tipi: {user.get_user_type_display() if hasattr(user, 'get_user_type_display') else 'Bilinmiyor'}

İlk Mesaj: {first_message.content if first_message else 'Henüz mesaj yok'}

Chat'e yanıt vermek için: {context['chat_url']}

Admin Paneli: https://apphane.com.tr/admin/chat/chatroom/{chat_room.id}/change/

--
Bu otomatik bir bildirimdir.
Apphane Platform
        """
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=admin_emails,
        )
        email.attach_alternative(html_content, "text/html")
        email.send()
        
        logger.info(f"Support chat notification sent to {len(admin_emails)} admins for room {chat_room.id}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send support chat notification: {str(e)}")
        return False


def send_project_offer_notification(offer):
    """
    Yeni proje teklifi geldiğinde admin'lere bildirim gönder
    """
    if not getattr(settings, 'CHAT_ADMIN_EMAIL_NOTIFICATIONS', False):
        return False
    
    try:
        admin_emails = getattr(settings, 'CHAT_ADMIN_EMAILS', [])
        if not admin_emails:
            admin_emails = [email for name, email in getattr(settings, 'ADMINS', [])]
        
        if not admin_emails:
            return False
        
        subject = f"💼 Yeni Proje Teklifi: {offer.title}"
        
        context = {
            'offer': offer,
            'sender': offer.sender,
            'receiver': offer.receiver,
            'site_url': 'https://apphane.com.tr',
            'chat_url': f"https://apphane.com.tr{offer.chat_room.get_absolute_url()}",
        }
        
        html_content = render_to_string('chat/emails/project_offer_notification.html', context)
        
        text_content = f"""
Yeni Proje Teklifi - Apphane.com.tr

Proje: {offer.title}
Gönderen: {offer.sender.get_full_name()} ({offer.sender.email})
Alıcı: {offer.receiver.get_full_name()} ({offer.receiver.email})
Bütçe: {offer.budget} TL
Teslim Tarihi: {offer.deadline}

Açıklama: {offer.description[:200]}{'...' if len(offer.description) > 200 else ''}

Chat'i görüntülemek için: {context['chat_url']}

Admin Paneli: https://apphane.com.tr/admin/chat/projectoffer/{offer.id}/change/

--
Bu otomatik bir bildirimdir.
Apphane Platform
        """
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=admin_emails,
        )
        email.attach_alternative(html_content, "text/html")
        email.send()
        
        logger.info(f"Project offer notification sent to {len(admin_emails)} admins for offer {offer.id}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send project offer notification: {str(e)}")
        return False


def send_admin_daily_chat_summary():
    """
    Günlük chat özeti gönder (Celery task olarak çalıştırılabilir)
    """
    from django.utils import timezone
    from datetime import timedelta
    from .models import Message, ChatRoom
    
    if not getattr(settings, 'CHAT_ADMIN_EMAIL_NOTIFICATIONS', False):
        return False
    
    try:
        admin_emails = getattr(settings, 'CHAT_ADMIN_EMAILS', [])
        if not admin_emails:
            return False
        
        # Son 24 saatin istatistikleri
        yesterday = timezone.now() - timedelta(days=1)
        
        new_messages_count = Message.objects.filter(created_at__gte=yesterday).count()
        new_chats_count = ChatRoom.objects.filter(created_at__gte=yesterday).count()
        active_users = User.objects.filter(
            sent_messages__created_at__gte=yesterday
        ).distinct().count()
        
        if new_messages_count == 0 and new_chats_count == 0:
            return False  # Hiç aktivite yoksa gönderme
        
        subject = f"📊 Günlük Chat Raporu - {timezone.now().strftime('%d/%m/%Y')}"
        
        context = {
            'new_messages_count': new_messages_count,
            'new_chats_count': new_chats_count,
            'active_users': active_users,
            'date': timezone.now().strftime('%d/%m/%Y'),
            'site_url': 'https://apphane.com.tr',
        }
        
        html_content = render_to_string('chat/emails/daily_summary.html', context)
        
        text_content = f"""
Günlük Chat Raporu - {context['date']}

📈 Son 24 Saatte:
- Yeni Mesajlar: {new_messages_count}
- Yeni Chat Odaları: {new_chats_count}
- Aktif Kullanıcılar: {active_users}

Admin Paneli: https://apphane.com.tr/admin/chat/

--
Apphane Platform
        """
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=admin_emails,
        )
        email.attach_alternative(html_content, "text/html")
        email.send()
        
        logger.info(f"Daily chat summary sent to {len(admin_emails)} admins")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send daily chat summary: {str(e)}")
        return False
