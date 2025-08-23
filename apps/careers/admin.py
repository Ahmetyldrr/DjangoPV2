from django.contrib import admin
from django.utils.html import format_html
from .models import (
    FreelancerApplication, ProjectCategory,
    FreelancerProject, ProjectOffer, ProjectImage
)

@admin.register(FreelancerApplication)
class FreelancerApplicationAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'title', 'status', 'applied_at', 'experience_years']
    list_filter = ['status', 'skill_level', 'applied_at', 'city']
    search_fields = ['full_name', 'email', 'title', 'skills']
    list_editable = ['status']
    readonly_fields = ['applied_at']
    
    fieldsets = (
        ('Kişisel Bilgiler', {
            'fields': ('full_name', 'email', 'phone', 'city')
        }),
        ('Profesyonel Bilgiler', {
            'fields': ('title', 'experience_years', 'skill_level', 'skills')
        }),
        ('Portföy', {
            'fields': ('portfolio_url', 'github_url', 'linkedin_url', 'cv_file')
        }),
        ('Başvuru', {
            'fields': ('cover_letter', 'status', 'applied_at', 'reviewed_at', 'reviewer_notes')
        }),
    )
    
    def has_delete_permission(self, request, obj=None):
        # Onaylanmış başvuruları silmeyi engelle
        if obj and obj.status == 'approved':
            return False
        return super().has_delete_permission(request, obj)


class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 1
    fields = ['image', 'caption', 'order']


@admin.register(ProjectCategory)
class ProjectCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'get_icon', 'slug']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    
    def get_icon(self, obj):
        return format_html('<i class="{}"></i>', obj.icon)
    get_icon.short_description = 'Icon'


@admin.register(FreelancerProject)
class FreelancerProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'get_freelancer', 'category', 'status', 'budget_range', 'views', 'offers_count', 'is_featured']
    list_filter = ['status', 'category', 'is_featured', 'created_at', 'budget_range']
    search_fields = ['title', 'description', 'technologies', 'freelancer__user__first_name', 'freelancer__user__last_name']
    list_editable = ['status', 'is_featured']
    readonly_fields = ['views', 'offers_count', 'created_at', 'updated_at']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ProjectImageInline]
    
    fieldsets = (
        ('Temel Bilgiler', {
            'fields': ('freelancer', 'category', 'title', 'slug', 'description')
        }),
        ('Teknik Detaylar', {
            'fields': ('technologies', 'requirements', 'deliverables')
        }),
        ('Zaman ve Bütçe', {
            'fields': ('estimated_duration', 'budget_range')
        }),
        ('Medya', {
            'fields': ('featured_image', 'demo_url', 'github_url')
        }),
        ('Durum ve İstatistikler', {
            'fields': ('status', 'is_featured', 'views', 'offers_count')
        }),
        ('Tarihler', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_freelancer(self, obj):
        return obj.freelancer.user.get_full_name() if obj.freelancer.user else 'N/A'
    get_freelancer.short_description = 'Freelancer'


@admin.register(ProjectOffer)
class ProjectOfferAdmin(admin.ModelAdmin):
    list_display = ['get_project', 'client_name', 'offer_amount', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['client_name', 'client_email', 'company_name', 'project__title']
    list_editable = ['status']
    readonly_fields = ['created_at', 'responded_at']
    
    fieldsets = (
        ('Proje Bilgisi', {
            'fields': ('project',)
        }),
        ('Müşteri Bilgileri', {
            'fields': ('client_name', 'client_email', 'client_phone', 'company_name')
        }),
        ('Teklif Detayları', {
            'fields': ('offer_amount', 'message', 'timeline')
        }),
        ('Durum', {
            'fields': ('status', 'response_message')
        }),
        ('Tarihler', {
            'fields': ('created_at', 'responded_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_project(self, obj):
        return obj.project.title
    get_project.short_description = 'Proje'


@admin.register(ProjectImage)
class ProjectImageAdmin(admin.ModelAdmin):
    list_display = ['get_project', 'caption', 'order']
    list_filter = ['project']
    search_fields = ['project__title', 'caption']
    list_editable = ['order']
    
    def get_project(self, obj):
        return obj.project.title
    get_project.short_description = 'Proje'
