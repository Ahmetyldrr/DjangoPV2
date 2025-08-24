from django.contrib import admin
from django.contrib import messages
from django.http import HttpResponseRedirect
from .models import ChatRoom, Message, ProjectOffer
from .email_notifications import (
    send_new_message_notification,
    send_support_chat_notification,
    send_project_offer_notification,
    send_admin_daily_chat_summary
)


@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'get_participants_count', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['name', 'participants__email', 'participants__first_name', 'participants__last_name']
    filter_horizontal = ['participants']
    readonly_fields = ['created_at', 'updated_at']
    
    def get_participants_count(self, obj):
        return obj.participants.count()
    get_participants_count.short_description = 'Katılımcı Sayısı'


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'room', 'message_type', 'content_preview', 'is_read', 'created_at']
    list_filter = ['message_type', 'is_read', 'created_at']
    search_fields = ['sender__email', 'content', 'room__name']
    readonly_fields = ['created_at', 'updated_at', 'read_at']
    actions = ['send_notification_manually']
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'İçerik'
    
    def send_notification_manually(self, request, queryset):
        """Admin tarafından manuel olarak bildirim gönder"""
        sent_count = 0
        for message in queryset:
            if send_new_message_notification(message):
                sent_count += 1
        
        if sent_count > 0:
            messages.success(request, f"{sent_count} mesaj için bildirim gönderildi.")
        else:
            messages.warning(request, "Hiçbir bildirim gönderilemedi.")
    
    send_notification_manually.short_description = "Seçili mesajlar için bildirim gönder"


@admin.register(ProjectOffer)
class ProjectOfferAdmin(admin.ModelAdmin):
    list_display = ['title', 'sender', 'receiver', 'budget', 'status', 'deadline', 'created_at']
    list_filter = ['status', 'created_at', 'deadline']
    search_fields = ['title', 'sender__email', 'receiver__email', 'description']
    readonly_fields = ['created_at', 'updated_at']
    actions = ['send_offer_notification']
    
    def send_offer_notification(self, request, queryset):
        """Admin tarafından manuel olarak proje teklifi bildirimi gönder"""
        sent_count = 0
        for offer in queryset:
            if send_project_offer_notification(offer):
                sent_count += 1
        
        if sent_count > 0:
            messages.success(request, f"{sent_count} proje teklifi için bildirim gönderildi.")
        else:
            messages.warning(request, "Hiçbir bildirim gönderilemedi.")
    
    send_offer_notification.short_description = "Seçili teklifler için bildirim gönder"


# Admin paneline özel view'lar eklemek için
class ChatAdminActions:
    """Chat admin panel için özel işlemler"""
    
    @staticmethod
    def send_daily_summary_action(request):
        """Günlük özet gönder"""
        if send_admin_daily_chat_summary():
            messages.success(request, "Günlük chat özeti gönderildi.")
        else:
            messages.warning(request, "Günlük özet gönderilemedi.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/admin/'))
