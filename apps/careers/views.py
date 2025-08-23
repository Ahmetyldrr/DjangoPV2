from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.views.generic import ListView, DetailView, CreateView
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator

from .models import (
    FreelancerApplication, ProjectCategory,
    FreelancerProject, ProjectOffer
)
from accounts.models import FreelancerProfile  # accounts app'indeki FreelancerProfile
from .forms import FreelancerApplicationForm, ProjectOfferForm, FreelancerProjectForm


class FreelancerApplicationView(CreateView):
    """Freelancer başvuru formu"""
    model = FreelancerApplication
    form_class = FreelancerApplicationForm
    template_name = 'careers/application_form.html'
    success_url = reverse_lazy('careers:application_success')
    
    def form_valid(self, form):
        messages.success(self.request, 
                        'Başvurunuz başarıyla alınmıştır. En kısa sürede inceleyeceğiz.')
        return super().form_valid(form)


def application_success(request):
    """Başvuru başarılı sayfası"""
    return render(request, 'careers/application_success.html')


class FreelancerListView(ListView):
    """Freelancer listesi"""
    model = FreelancerProfile
    template_name = 'careers/freelancers.html'
    context_object_name = 'freelancers'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = FreelancerProfile.objects.filter(is_verified=True)
        
        # Arama
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(user__first_name__icontains=search) |
                Q(user__last_name__icontains=search) |
                Q(title__icontains=search) |
                Q(skills__icontains=search)
            )
        
        # Filtreleme
        experience_years = self.request.GET.get('experience_years')
        if experience_years:
            queryset = queryset.filter(experience_years__gte=experience_years)
        
        city = self.request.GET.get('city')
        if city:
            queryset = queryset.filter(city__icontains=city)
        
        available = self.request.GET.get('available')
        if available == 'true':
            queryset = queryset.filter(is_available=True)
        
        # Sıralama
        sort = self.request.GET.get('sort', '-rating')
        if sort in ['-rating', '-total_projects', '-created_at', 'hourly_rate']:
            queryset = queryset.order_by(sort)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['skill_level'] = self.request.GET.get('skill_level', '')
        context['city'] = self.request.GET.get('city', '')
        context['available'] = self.request.GET.get('available', '')
        context['sort'] = self.request.GET.get('sort', '-rating')
        
        # Filtre seçenekleri
        context['skill_levels'] = FreelancerApplication.SKILL_LEVEL_CHOICES
        context['cities'] = FreelancerProfile.objects.filter(
            is_verified=True
        ).values_list('city', flat=True).distinct()
        
        return context


class FreelancerDetailView(DetailView):
    """Freelancer detay sayfası"""
    model = FreelancerProfile
    template_name = 'careers/freelancer_detail.html'
    context_object_name = 'freelancer'
    
    def get_object(self):
        return get_object_or_404(FreelancerProfile, user__id=self.kwargs['user_id'], is_verified=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        freelancer = self.get_object()
        
        # Freelancer'ın projeleri
        context['projects'] = FreelancerProject.objects.filter(
            freelancer=freelancer,
            status='published'
        ).order_by('-is_featured', '-created_at')[:6]
        
        return context


class ProjectListView(ListView):
    """Proje listesi"""
    model = FreelancerProject
    template_name = 'careers/projects.html'
    context_object_name = 'projects'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = FreelancerProject.objects.filter(status='published')
        
        # Arama
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(technologies__icontains=search) |
                Q(freelancer__application__full_name__icontains=search)
            )
        
        # Kategori filtresi
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category__slug=category)
        
        # Bütçe filtresi
        budget = self.request.GET.get('budget')
        if budget:
            queryset = queryset.filter(budget_range=budget)
        
        # Sıralama
        sort = self.request.GET.get('sort', '-is_featured')
        if sort in ['-is_featured', '-created_at', '-views', 'budget_range']:
            queryset = queryset.order_by(sort, '-created_at')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['category'] = self.request.GET.get('category', '')
        context['budget'] = self.request.GET.get('budget', '')
        context['sort'] = self.request.GET.get('sort', '-is_featured')
        
        # Filtre seçenekleri
        context['categories'] = ProjectCategory.objects.all()
        context['budget_ranges'] = FreelancerProject.BUDGET_CHOICES
        
        return context


class ProjectDetailView(DetailView):
    """Proje detay sayfası"""
    model = FreelancerProject
    template_name = 'careers/project_detail.html'
    context_object_name = 'project'
    
    def get_object(self):
        project = get_object_or_404(FreelancerProject, slug=self.kwargs['slug'], status='published')
        # Görüntülenme sayısını artır
        project.views += 1
        project.save(update_fields=['views'])
        return project
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = self.get_object()
        
        # Teklif formu (kullanıcı bilgisiyle)
        context['offer_form'] = ProjectOfferForm(user=self.request.user)
        
        # Benzer projeler
        context['similar_projects'] = FreelancerProject.objects.filter(
            category=project.category,
            status='published'
        ).exclude(pk=project.pk)[:4]
        
        # Freelancer'ın diğer projeleri
        context['other_projects'] = FreelancerProject.objects.filter(
            freelancer=project.freelancer,
            status='published'
        ).exclude(pk=project.pk)[:3]
        
        return context


def submit_offer(request, slug):
    """Proje teklifini gönder"""
    if request.method == 'POST':
        project = get_object_or_404(FreelancerProject, slug=slug, status='published')
        form = ProjectOfferForm(request.POST, user=request.user)
        
        if form.is_valid():
            offer = form.save(commit=False)
            offer.project = project
            offer.save()
            
            # Teklif sayısını güncelle
            project.offers_count = ProjectOffer.objects.filter(project=project).count()
            project.save(update_fields=['offers_count'])
            
            messages.success(request, 'Teklifiniz başarıyla gönderilmiştir. Freelancer en kısa sürede size dönüş yapacaktır.')
            return redirect('careers:project_detail', slug=slug)
        else:
            messages.error(request, 'Teklif gönderilirken bir hata oluştu. Lütfen formu kontrol edin.')
            return redirect('careers:project_detail', slug=slug)
    
    return redirect('careers:project_list')


class FreelancerProjectCreateView(LoginRequiredMixin, CreateView):
    """Freelancer proje oluşturma"""
    model = FreelancerProject
    form_class = FreelancerProjectForm
    template_name = 'careers/project_create.html'
    
    def dispatch(self, request, *args, **kwargs):
        # Kullanıcının freelancer profili olup olmadığını kontrol et
        try:
            freelancer_profile = FreelancerProfile.objects.get(user=request.user)
            if not freelancer_profile.is_verified:
                messages.error(request, 'Proje oluşturmak için onaylanmış freelancer profilinizin olması gerekir.')
                return redirect('accounts:freelancer_dashboard')
        except FreelancerProfile.DoesNotExist:
            messages.error(request, 'Proje oluşturmak için önce freelancer profilinizi tamamlamanız gerekir.')
            return redirect('accounts:freelancer_profile_edit')
        
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        freelancer_profile = FreelancerProfile.objects.get(user=self.request.user)
        form.instance.freelancer = freelancer_profile
        form.instance.status = 'published'  # Varsayılan olarak yayınla
        
        messages.success(self.request, 'Projeniz başarıyla oluşturulmuştur!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('accounts:freelancer_dashboard')


def careers_home(request):
    """Kariyer ana sayfası"""
    context = {
        'featured_freelancers': FreelancerProfile.objects.filter(
            is_verified=True, is_available=True
        ).order_by('-rating', '-total_projects')[:6],
        
        'featured_projects': FreelancerProject.objects.filter(
            status='published', is_featured=True
        ).order_by('-created_at')[:6],
        
        'recent_projects': FreelancerProject.objects.filter(
            status='published'
        ).order_by('-created_at')[:8],
        
        'categories': ProjectCategory.objects.all()[:8],
        
        'stats': {
            'total_freelancers': FreelancerProfile.objects.filter(is_verified=True).count(),
            'total_projects': FreelancerProject.objects.filter(status='published').count(),
            'total_offers': ProjectOffer.objects.count(),
        }
    }
    
    return render(request, 'careers/home.html', context)
