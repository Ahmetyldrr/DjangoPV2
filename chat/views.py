from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db.models import Q
import json

from .models import ChatRoom, Message, ProjectOffer

User = get_user_model()


@login_required
def chat_list(request):
    """Kullanıcının chat odalarını listele"""
    chat_rooms = ChatRoom.objects.filter(
        participants=request.user
    ).order_by('-updated_at')
    
    # Her chat room için son mesaj ve okunmamış mesaj sayısını al
    chat_data = []
    for room in chat_rooms:
        last_message = room.get_last_message()
        unread_count = room.messages.filter(
            is_read=False
        ).exclude(sender=request.user).count()
        
        other_participant = room.get_other_participant(request.user)
        
        chat_data.append({
            'room': room,
            'last_message': last_message,
            'unread_count': unread_count,
            'other_participant': other_participant,
        })
    
    context = {
        'chat_data': chat_data,
    }
    
    return render(request, 'chat/chat_list.html', context)


@login_required
def chat_room(request, room_id):
    """Chat odası sayfası"""
    room = get_object_or_404(ChatRoom, id=room_id, participants=request.user)
    
    # Mesajları okundu olarak işaretle
    room.messages.filter(is_read=False).exclude(sender=request.user).update(
        is_read=True,
        read_at=timezone.now()
    )
    
    # Son 50 mesajı getir
    messages = room.messages.order_by('-created_at')[:50]
    messages = reversed(messages)
    
    other_participant = room.get_other_participant(request.user)
    
    context = {
        'room': room,
        'messages': messages,
        'other_participant': other_participant,
    }
    
    return render(request, 'chat/chat_room.html', context)


@login_required
def start_chat(request, user_id):
    """Belirli bir kullanıcıyla chat başlat"""
    other_user = get_object_or_404(User, id=user_id)
    
    if other_user == request.user:
        return redirect('chat:chat_list')
    
    # Mevcut chat odasını ara
    existing_room = ChatRoom.objects.filter(
        participants=request.user
    ).filter(
        participants=other_user
    ).first()
    
    if existing_room:
        return redirect('chat:room', room_id=existing_room.id)
    
    # Yeni chat odası oluştur
    room = ChatRoom.objects.create()
    room.participants.set([request.user, other_user])
    
    return redirect('chat:room', room_id=room.id)


@csrf_exempt
@login_required
def send_message(request):
    """AJAX ile mesaj gönder"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)
    
    try:
        data = json.loads(request.body)
        room_id = data.get('room_id')
        content = data.get('content')
        message_type = data.get('message_type', 'text')
        
        if not room_id or not content:
            return JsonResponse({'error': 'Room ID and content required'}, status=400)
        
        room = get_object_or_404(ChatRoom, id=room_id, participants=request.user)
        
        # Mesajı oluştur
        message = Message.objects.create(
            room=room,
            sender=request.user,
            content=content,
            message_type=message_type
        )
        
        # Chat odasının güncellenme tarihini güncelle
        room.updated_at = timezone.now()
        room.save(update_fields=['updated_at'])
        
        return JsonResponse({
            'success': True,
            'message': {
                'id': message.id,
                'content': message.content,
                'sender': message.sender.get_full_name(),
                'created_at': message.created_at.isoformat(),
                'is_own': True
            }
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def get_messages(request, room_id):
    """Belirli bir chat odasının mesajlarını getir"""
    room = get_object_or_404(ChatRoom, id=room_id, participants=request.user)
    
    # Offset parametresi varsa (pagination için)
    offset = int(request.GET.get('offset', 0))
    limit = 20
    
    messages = room.messages.order_by('-created_at')[offset:offset + limit]
    
    message_data = []
    for message in reversed(messages):
        message_data.append({
            'id': message.id,
            'content': message.content,
            'sender': message.sender.get_full_name(),
            'created_at': message.created_at.isoformat(),
            'is_own': message.sender == request.user,
            'is_read': message.is_read,
        })
    
    return JsonResponse({
        'messages': message_data,
        'has_more': room.messages.count() > offset + limit
    })


@csrf_exempt
@login_required
def mark_message_read(request, message_id):
    """Mesajı okundu olarak işaretle"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)
    
    message = get_object_or_404(Message, id=message_id)
    
    # Sadece alıcı mesajı okundu olarak işaretleyebilir
    if message.sender != request.user:
        message.mark_as_read()
        return JsonResponse({'success': True})
    
    return JsonResponse({'error': 'Cannot mark own message as read'}, status=400)


@login_required
def start_support_chat(request):
    """Admin ile destek chat'i başlat"""
    # İlk admin kullanıcıyı bul
    admin_user = User.objects.filter(
        Q(user_type='admin') | Q(is_superuser=True)
    ).first()
    
    if not admin_user:
        # Eğer admin yoksa, superuser oluştur
        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            # Hiç admin yoksa hata mesajı
            return redirect('chat:chat_list')
    
    if admin_user == request.user:
        # Admin kendisiyle chat başlatamaz
        return redirect('chat:chat_list')
    
    # Mevcut destek chat odasını ara
    existing_room = ChatRoom.objects.filter(
        participants=request.user
    ).filter(
        participants=admin_user
    ).first()
    
    if existing_room:
        return redirect('chat:room', room_id=existing_room.id)
    
    # Yeni destek chat odası oluştur
    room = ChatRoom.objects.create(
        name=f"Destek Chat - {request.user.get_full_name()}"
    )
    room.participants.set([request.user, admin_user])
    
    # Hoş geldin mesajı gönder
    Message.objects.create(
        room=room,
        sender=admin_user,
        content=f"Merhaba {request.user.get_full_name()}! Size nasıl yardımcı olabilirim?",
        message_type='text'
    )
    
    return redirect('chat:room', room_id=room.id)
