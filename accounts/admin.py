from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User, FreelancerProfile


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'first_name', 'last_name', 'user_type', 'is_verified', 'is_active', 'created_at']
    list_filter = ['user_type', 'is_verified', 'is_active', 'created_at']
    search_fields = ['email', 'first_name', 'last_name']
    ordering = ['-created_at']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Kişisel Bilgiler', {'fields': ('first_name', 'last_name', 'phone', 'bio', 'avatar', 'website')}),
        ('Kullanıcı Tipi', {'fields': ('user_type', 'is_verified')}),
        ('İzinler', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Önemli Tarihler', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'user_type', 'password1', 'password2'),
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related()


@admin.register(FreelancerProfile)
class FreelancerProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'city', 'hourly_rate', 'rating', 'total_projects', 'is_available', 'is_verified']
    list_filter = ['is_available', 'is_verified', 'city', 'experience_years']
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'title', 'skills']
    readonly_fields = ['total_projects', 'total_earnings', 'rating_count', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Kullanıcı', {'fields': ('user',)}),
        ('Profesyonel Bilgiler', {'fields': ('title', 'skills', 'experience_years', 'hourly_rate')}),
        ('Konum', {'fields': ('city', 'country')}),
        ('Portfolio', {'fields': ('portfolio_url', 'github_url', 'linkedin_url')}),
        ('Durum', {'fields': ('is_available', 'is_verified')}),
        ('İstatistikler', {'fields': ('total_projects', 'total_earnings', 'rating', 'rating_count')}),
        ('Tarihler', {'fields': ('created_at', 'updated_at')}),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')
