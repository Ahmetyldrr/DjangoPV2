from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.conf import settings
from django.core.paginator import Paginator
from django.db.models import Q, Count
from datetime import datetime, timedelta
from chat.models import Message, ChatRoom, ProjectOffer
from django.contrib.auth import get_user_model

User = get_user_model()


@staff_member_required
def admin_control_center(request):
    """Ana admin kontrol merkezi - Tüm sistem takibi"""
    
    # Zaman filtreleri
    filter_hours = int(request.GET.get('hours', 24))
    time_filter = datetime.now() - timedelta(hours=filter_hours)
    
    # Temel istatistikler
    stats = {
        'messages_count': Message.objects.filter(created_at__gte=time_filter).count(),
        'chats_count': ChatRoom.objects.filter(created_at__gte=time_filter).count(),
        'offers_count': ProjectOffer.objects.filter(created_at__gte=time_filter).count(),
        'active_users': User.objects.filter(
            sent_messages__created_at__gte=time_filter
        ).distinct().count(),
        'unread_messages': Message.objects.filter(is_read=False).count(),
        'pending_offers': ProjectOffer.objects.filter(status='pending').count(),
    }
    
    # Toplam istatistikler
    total_stats = {
        'total_messages': Message.objects.count(),
        'total_chats': ChatRoom.objects.count(),
        'total_users': User.objects.count(),
        'total_offers': ProjectOffer.objects.count(),
    }
    
    # Son aktiviteler
    recent_messages = Message.objects.select_related('sender', 'room').order_by('-created_at')[:20]
    recent_chats = ChatRoom.objects.prefetch_related('participants').order_by('-created_at')[:10]
    recent_offers = ProjectOffer.objects.select_related('sender', 'receiver').order_by('-created_at')[:10]
    
    # Kullanıcı aktiviteleri
    active_users = User.objects.filter(
        sent_messages__created_at__gte=time_filter
    ).annotate(
        message_count=Count('sent_messages')
    ).order_by('-message_count')[:10]
    
    # Email sistemi durumu
    email_status = {
        'backend': getattr(settings, 'EMAIL_BACKEND', 'Not configured'),
        'notifications_enabled': getattr(settings, 'CHAT_ADMIN_EMAIL_NOTIFICATIONS', False),
        'admin_emails': getattr(settings, 'CHAT_ADMIN_EMAILS', []),
        'host': getattr(settings, 'EMAIL_HOST', 'Not configured'),
    }
    
    context = {
        'stats': stats,
        'total_stats': total_stats,
        'recent_messages': recent_messages,
        'recent_chats': recent_chats,
        'recent_offers': recent_offers,
        'active_users': active_users,
        'email_status': email_status,
        'filter_hours': filter_hours,
        'time_filter': time_filter,
    }
    
    return render(request, 'admin/control_center.html', context)


@staff_member_required
def api_live_messages(request):
    """Canlı mesaj takibi API"""
    
    # Son güncelleme zamanı
    last_update = request.GET.get('last_update')
    if last_update:
        try:
            last_update = datetime.fromisoformat(last_update.replace('Z', '+00:00'))
            messages = Message.objects.filter(created_at__gt=last_update)
        except:
            messages = Message.objects.none()
    else:
        # Son 50 mesaj
        messages = Message.objects.order_by('-created_at')[:50]
    
    messages_data = []
    for msg in messages.select_related('sender', 'room'):
        participants = list(msg.room.participants.values_list('first_name', 'last_name', 'email'))
        
        messages_data.append({
            'id': msg.id,
            'sender': msg.sender.get_full_name(),
            'sender_email': msg.sender.email,
            'content': msg.content[:100],
            'content_full': msg.content,
            'room_id': msg.room.id,
            'participants': [f"{p[0]} {p[1]} ({p[2]})" for p in participants],
            'is_read': msg.is_read,
            'message_type': msg.message_type,
            'created_at': msg.created_at.isoformat(),
        })
    
    return JsonResponse({
        'messages': messages_data,
        'count': len(messages_data),
        'timestamp': datetime.now().isoformat(),
    })


@staff_member_required
def api_system_stats(request):
    """Sistem istatistikleri API"""
    
    filter_hours = int(request.GET.get('hours', 24))
    time_filter = datetime.now() - timedelta(hours=filter_hours)
    
    # Saatlik mesaj dağılımı (son 24 saat)
    hourly_stats = []
    for i in range(24):
        hour_start = datetime.now() - timedelta(hours=i+1)
        hour_end = datetime.now() - timedelta(hours=i)
        count = Message.objects.filter(
            created_at__gte=hour_start,
            created_at__lt=hour_end
        ).count()
        hourly_stats.append({
            'hour': hour_start.strftime('%H:00'),
            'count': count
        })
    
    # Kullanıcı tipi dağılımı
    user_types = User.objects.values('user_type').annotate(count=Count('id'))
    
    # Mesaj tipi dağılımı
    message_types = Message.objects.filter(
        created_at__gte=time_filter
    ).values('message_type').annotate(count=Count('id'))
    
    # En aktif kullanıcılar
    top_users = User.objects.filter(
        sent_messages__created_at__gte=time_filter
    ).annotate(
        message_count=Count('sent_messages')
    ).order_by('-message_count')[:5]
    
    top_users_data = [{
        'name': user.get_full_name(),
        'email': user.email,
        'message_count': user.message_count,
        'user_type': getattr(user, 'user_type', 'Unknown')
    } for user in top_users]
    
    return JsonResponse({
        'hourly_stats': list(reversed(hourly_stats)),
        'user_types': list(user_types),
        'message_types': list(message_types),
        'top_users': top_users_data,
        'timestamp': datetime.now().isoformat(),
    })


@staff_member_required
def api_send_broadcast_message(request):
    """Toplu mesaj gönderme API"""
    
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)
    
    try:
        import json
        data = json.loads(request.body)
        
        subject = data.get('subject')
        message = data.get('message')
        recipient_type = data.get('recipient_type', 'all')  # all, active, developers, clients
        
        if not subject or not message:
            return JsonResponse({'error': 'Subject and message required'}, status=400)
        
        # Alıcıları belirle
        if recipient_type == 'active':
            # Son 7 günde aktif olan kullanıcılar
            week_ago = datetime.now() - timedelta(days=7)
            recipients = User.objects.filter(
                sent_messages__created_at__gte=week_ago
            ).distinct()
        elif recipient_type == 'developers':
            recipients = User.objects.filter(user_type='developer')
        elif recipient_type == 'clients':
            recipients = User.objects.filter(user_type='client')
        else:
            recipients = User.objects.all()
        
        # Email gönder
        from django.core.mail import send_mass_mail
        
        email_messages = []
        for user in recipients[:100]:  # Güvenlik için 100 ile sınırla
            email_messages.append((
                f"[Apphane] {subject}",
                f"Merhaba {user.get_full_name()},\n\n{message}\n\n--\nApphane Platform\nhttps://apphane.com.tr",
                settings.DEFAULT_FROM_EMAIL,
                [user.email]
            ))
        
        sent_count = send_mass_mail(email_messages, fail_silently=False)
        
        return JsonResponse({
            'success': True,
            'sent_count': sent_count,
            'recipient_count': recipients.count()
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@staff_member_required
def api_message_actions(request):
    """Mesaj üzerinde işlemler"""
    
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)
    
    try:
        import json
        data = json.loads(request.body)
        
        action = data.get('action')
        message_ids = data.get('message_ids', [])
        
        if not action or not message_ids:
            return JsonResponse({'error': 'Action and message_ids required'}, status=400)
        
        messages = Message.objects.filter(id__in=message_ids)
        
        if action == 'mark_read':
            from django.utils import timezone
            updated = messages.update(is_read=True, read_at=timezone.now())
            return JsonResponse({'success': True, 'updated': updated})
        
        elif action == 'delete':
            deleted, _ = messages.delete()
            return JsonResponse({'success': True, 'deleted': deleted})
        
        elif action == 'export':
            # CSV export fonksiyonu
            import csv
            from django.http import HttpResponse
            
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="messages_{datetime.now().strftime("%Y%m%d")}.csv"'
            
            writer = csv.writer(response)
            writer.writerow(['Tarih', 'Gönderen', 'İçerik', 'Okundu', 'Oda'])
            
            for msg in messages:
                writer.writerow([
                    msg.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    msg.sender.get_full_name(),
                    msg.content,
                    'Evet' if msg.is_read else 'Hayır',
                    str(msg.room)
                ])
            
            return response
        
        else:
            return JsonResponse({'error': 'Invalid action'}, status=400)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
