from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.conf import settings
from django.core.paginator import Paginator
from django.db.models import Q, Count
import os
import json
from datetime import datetime, timedelta
from chat.models import Message, ChatRoom, ProjectOffer
from django.contrib.auth import get_user_model

User = get_user_model()


@staff_member_required
def system_dashboard(request):
    """Admin sistem dashboard'u"""
    
    # Son 24 saatin istatistikleri
    yesterday = datetime.now() - timedelta(days=1)
    
    stats = {
        'messages_24h': Message.objects.filter(created_at__gte=yesterday).count(),
        'new_chats_24h': ChatRoom.objects.filter(created_at__gte=yesterday).count(),
        'active_users_24h': User.objects.filter(
            sent_messages__created_at__gte=yesterday
        ).distinct().count(),
        'total_messages': Message.objects.count(),
        'total_chats': ChatRoom.objects.count(),
        'total_users': User.objects.count(),
    }
    
    # Son mesajlar
    recent_messages = Message.objects.select_related('sender', 'room').order_by('-created_at')[:10]
    
    # Email ayarları
    email_settings = {
        'backend': getattr(settings, 'EMAIL_BACKEND', 'Not set'),
        'host': getattr(settings, 'EMAIL_HOST', 'Not set'),
        'notifications_enabled': getattr(settings, 'CHAT_ADMIN_EMAIL_NOTIFICATIONS', False),
        'admin_emails': getattr(settings, 'CHAT_ADMIN_EMAILS', []),
    }
    
    context = {
        'stats': stats,
        'recent_messages': recent_messages,
        'email_settings': email_settings,
    }
    
    return render(request, 'admin/system_dashboard.html', context)


@staff_member_required
def api_logs(request):
    """AJAX ile log verilerini getir"""
    log_type = request.GET.get('type', 'email')
    tail_count = int(request.GET.get('tail', 50))
    
    logs_dir = os.path.join(settings.BASE_DIR, 'logs')
    
    if log_type == 'email':
        log_file = os.path.join(logs_dir, 'chat_emails.log')
    else:
        log_file = os.path.join(logs_dir, 'django.log')
    
    try:
        if os.path.exists(log_file):
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            recent_lines = lines[-tail_count:] if len(lines) > tail_count else lines
            
            return JsonResponse({
                'success': True,
                'logs': [line.strip() for line in recent_lines if line.strip()],
                'total_lines': len(lines),
                'file_path': log_file,
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Log dosyası bulunamadı',
                'file_path': log_file,
            })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
        })


@staff_member_required
def test_email_system(request):
    """Admin panelinden email sistemi test et"""
    if request.method == 'POST':
        test_type = request.POST.get('test_type')
        
        try:
            if test_type == 'basic':
                from django.core.mail import send_mail
                
                admin_emails = getattr(settings, 'CHAT_ADMIN_EMAILS', [])
                if not admin_emails:
                    admin_emails = [email for name, email in getattr(settings, 'ADMINS', [])]
                
                if admin_emails:
                    send_mail(
                        subject='🧪 Admin Panel Test Email',
                        message=f'Bu test email\'i admin panel\'den {request.user.get_full_name()} tarafından gönderilmiştir.\n\nZaman: {datetime.now()}',
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[admin_emails[0]],
                        fail_silently=False,
                    )
                    
                    return JsonResponse({
                        'success': True,
                        'message': f'Test email gönderildi: {admin_emails[0]}'
                    })
                else:
                    return JsonResponse({
                        'success': False,
                        'error': 'Admin email bulunamadı'
                    })
                    
            elif test_type == 'notification':
                from chat.email_notifications import send_new_message_notification
                
                # Son mesajı al ve test et
                recent_message = Message.objects.order_by('-created_at').first()
                
                if recent_message:
                    success = send_new_message_notification(recent_message)
                    
                    return JsonResponse({
                        'success': success,
                        'message': f'Chat bildirimi {"gönderildi" if success else "gönderilemedi"}'
                    })
                else:
                    return JsonResponse({
                        'success': False,
                        'error': 'Test için mesaj bulunamadı'
                    })
                    
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})
