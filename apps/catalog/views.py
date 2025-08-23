from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.db.models import Q
from django.contrib.auth import get_user_model
from .models import Application, Category
from apps.careers.models import FreelancerApplication, FreelancerProject
from accounts.models import FreelancerProfile

User = get_user_model()


class ApplicationListView(ListView):
    model = Application
    template_name = 'catalog/application_list.html'
    context_object_name = 'applications'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Application.objects.filter(is_active=True)
        
        # Arama
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(short_description__icontains=search_query) |
                Q(tags__icontains=search_query)
            )
        
        # Kategori filtresi
        category_slug = self.request.GET.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(is_active=True)
        context['search_query'] = self.request.GET.get('q', '')
        context['selected_category'] = self.request.GET.get('category', '')
        
        # Freelancer profilleri ve projelerini getir
        freelancer_profiles = FreelancerProfile.objects.select_related('user').all()[:8]
        
        # Her freelancer için projelerini de getir
        freelancer_data = []
        for profile in freelancer_profiles:
            projects = FreelancerProject.objects.filter(
                freelancer=profile
            ).order_by('-created_at')[:3]  # Son 3 proje
            
            freelancer_data.append({
                'profile': profile,
                'user': profile.user,
                'projects': projects,
                'project_count': FreelancerProject.objects.filter(freelancer=profile).count()
            })
        
        context['freelancer_data'] = freelancer_data
        
        # Ayrıca tüm freelancer projelerini de gönder
        context['recent_projects'] = FreelancerProject.objects.select_related(
            'freelancer__user'
        ).order_by('-created_at')[:6]
        
        return context


class ApplicationDetailView(DetailView):
    model = Application
    template_name = 'catalog/application_detail.html'
    context_object_name = 'application'
    
    def get_queryset(self):
        return Application.objects.filter(is_active=True)
    
    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        # Görüntülenme sayısını artır
        obj.view_count += 1
        obj.save(update_fields=['view_count'])
        return obj
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['releases'] = self.object.releases.filter(is_active=True).order_by('-published_at')
        return context


class CategoryListView(ListView):
    model = Category
    template_name = 'catalog/category_list.html'
    context_object_name = 'categories'
    
    def get_queryset(self):
        return Category.objects.filter(is_active=True)


class CategoryDetailView(DetailView):
    model = Category
    template_name = 'catalog/category_detail.html'
    context_object_name = 'category'
    
    def get_queryset(self):
        return Category.objects.filter(is_active=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['applications'] = self.object.applications.filter(is_active=True).order_by('-created_at')
        return context
