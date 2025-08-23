from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Application


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'application_count', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    
    def application_count(self, obj):
        return obj.applications.count()
    application_count.short_description = 'Uygulama Sayısı'


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'view_count', 'has_media', 'is_active', 'created_at']
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['title', 'short_description', 'tags']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['view_count', 'created_at', 'updated_at']
    list_per_page = 20
    
    fieldsets = (
        ('Temel Bilgiler', {
            'fields': ('title', 'slug', 'category', 'short_description', 'description_markdown', 'tags', 'is_active')
        }),
        ('Medya Dosyaları', {
            'fields': ('image', 'screenshot1', 'screenshot2', 'screenshot3', 'pdf_file', 'youtube_url'),
            'classes': ('collapse',)
        }),
        ('İstatistikler', {
            'fields': ('view_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_media(self, obj):
        media_count = 0
        if obj.image: media_count += 1
        if obj.pdf_file: media_count += 1
        if obj.youtube_url: media_count += 1
        if obj.get_screenshots(): media_count += len(obj.get_screenshots())
        
        if media_count == 0:
            return format_html('<span style="color: red;">❌ Yok</span>')
        elif media_count <= 2:
            return format_html('<span style="color: orange;">⚠️ Kısmi ({})</span>', media_count)
        else:
            return format_html('<span style="color: green;">✅ Tam ({})</span>', media_count)
    
    has_media.short_description = 'Medya Durumu'
    has_media.admin_order_field = 'title'
