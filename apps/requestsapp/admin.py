from django.contrib import admin
from .models import UserRequest


@admin.register(UserRequest)
class UserRequestAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'subject', 'created_at']
    list_filter = ['created_at']
    search_fields = ['full_name', 'email', 'subject']
    readonly_fields = ['created_at']
    list_per_page = 20
