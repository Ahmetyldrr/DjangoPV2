from django.contrib import admin
from .models import ChatRoom, Message, ProjectOffer


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
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'İçerik'


@admin.register(ProjectOffer)
class ProjectOfferAdmin(admin.ModelAdmin):
    list_display = ['title', 'sender', 'receiver', 'budget', 'status', 'deadline', 'created_at']
    list_filter = ['status', 'created_at', 'deadline']
    search_fields = ['title', 'sender__email', 'receiver__email', 'description']
    readonly_fields = ['created_at', 'updated_at']
