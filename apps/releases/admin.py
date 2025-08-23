from django.contrib import admin
from .models import Release


@admin.register(Release)
class ReleaseAdmin(admin.ModelAdmin):
    list_display = ['application', 'version', 'channel', 'is_active', 'published_at', 'download_count']
    list_filter = ['channel', 'is_active', 'published_at', 'application__category']
    search_fields = ['application__title', 'version']
    readonly_fields = ['download_count', 'published_at']
    list_per_page = 20
    
    fieldsets = (
        ('Temel Bilgiler', {
            'fields': ('application', 'version', 'channel', 'is_active')
        }),
        ('Dosya Bilgileri', {
            'fields': ('file', 'file_size', 'sha256')
        }),
        ('Açıklama', {
            'fields': ('changelog_markdown',)
        }),
        ('İstatistikler', {
            'fields': ('download_count', 'published_at'),
            'classes': ('collapse',)
        }),
    )
