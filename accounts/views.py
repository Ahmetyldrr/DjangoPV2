from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import UpdateView, DetailView
from django.urls import reverse_lazy
from django.db.models import Q
from .models import User, FreelancerProfile
from .forms import UserProfileForm, FreelancerProfileForm


@login_required
def profile_view(request):
    """Kullanıcı profil sayfası"""
    if request.user.is_freelancer:
        return redirect('accounts:freelancer_dashboard')
    
    context = {
        'user': request.user,
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def freelancer_dashboard(request):
    """Freelancer dashboard"""
    if not request.user.is_freelancer:
        messages.error(request, 'Bu sayfaya erişim yetkiniz yok.')
        return redirect('accounts:profile')
    
    # Freelancer profili oluştur eğer yoksa
    freelancer_profile, created = FreelancerProfile.objects.get_or_create(
        user=request.user,
        defaults={
            'title': 'Freelancer',
            'skills': '',
            'city': '',
        }
    )
    
    from chat.models import ChatRoom, Message
    from apps.careers.models import FreelancerProject
    
    # Son projeler
    recent_projects = FreelancerProject.objects.filter(
        freelancer=freelancer_profile
    ).order_by('-created_at')[:5]
    
    # İstatistikler
    stats = {
        'total_projects': FreelancerProject.objects.filter(freelancer=freelancer_profile).count(),
        'active_projects': FreelancerProject.objects.filter(
            freelancer=freelancer_profile, 
            status__in=['published', 'draft']
        ).count(),
        'completed_projects': FreelancerProject.objects.filter(
            freelancer=freelancer_profile, 
            status='completed'
        ).count(),
        'total_earnings': freelancer_profile.total_earnings,
        'unread_messages': Message.objects.filter(
            room__participants=request.user,
            is_read=False
        ).exclude(sender=request.user).count(),
    }
    
    # Son mesajlar
    recent_chats = ChatRoom.objects.filter(
        participants=request.user
    ).order_by('-updated_at')[:5]
    
    context = {
        'freelancer_profile': freelancer_profile,
        'stats': stats,
        'recent_projects': recent_projects,
        'recent_chats': recent_chats,
    }
    
    return render(request, 'accounts/freelancer_dashboard.html', context)


class UserProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Kullanıcı profil güncelleme"""
    model = User
    form_class = UserProfileForm
    template_name = 'accounts/profile_edit.html'
    success_url = reverse_lazy('accounts:profile')
    
    def get_object(self):
        return self.request.user
    
    def form_valid(self, form):
        messages.success(self.request, 'Profiliniz başarıyla güncellendi.')
        return super().form_valid(form)


class FreelancerProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Freelancer profil güncelleme"""
    model = FreelancerProfile
    form_class = FreelancerProfileForm
    template_name = 'accounts/freelancer_profile_edit.html'
    success_url = reverse_lazy('accounts:freelancer_dashboard')
    
    def get_object(self):
        freelancer_profile, created = FreelancerProfile.objects.get_or_create(
            user=self.request.user,
            defaults={
                'title': 'Freelancer',
                'skills': '',
                'city': '',
            }
        )
        return freelancer_profile
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_freelancer:
            messages.error(request, 'Bu sayfaya erişim yetkiniz yok.')
            return redirect('accounts:profile')
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        messages.success(self.request, 'Freelancer profiliniz başarıyla güncellendi.')
        return super().form_valid(form)


@login_required
def become_freelancer(request):
    """Freelancer olmak için başvuru"""
    if request.user.is_freelancer:
        messages.info(request, 'Zaten freelancer hesabınız bulunmakta.')
        return redirect('accounts:freelancer_dashboard')
    
    if request.method == 'POST':
        # Kullanıcıyı freelancer yap
        request.user.user_type = 'freelancer'
        request.user.save()
        
        # Freelancer profili oluştur
        FreelancerProfile.objects.get_or_create(
            user=request.user,
            defaults={
                'title': 'Freelancer',
                'skills': '',
                'city': '',
            }
        )
        
        messages.success(request, 'Tebrikler! Freelancer hesabınız oluşturuldu. Profilinizi tamamlayın.')
        return redirect('accounts:freelancer_profile_edit')
    
    return render(request, 'accounts/become_freelancer.html')


def freelancer_public_profile(request, user_id):
    """Freelancer'ın herkese açık profili"""
    user = get_object_or_404(User, id=user_id, user_type='freelancer')
    
    try:
        freelancer_profile = user.freelancer_profile
    except FreelancerProfile.DoesNotExist:
        messages.error(request, 'Freelancer profili bulunamadı.')
        return redirect('careers:freelancer_list')
    
    # Freelancer'ın projelerini çek
    from apps.careers.models import FreelancerProject
    projects = FreelancerProject.objects.filter(
        freelancer=freelancer_profile,
        status='published'
    ).order_by('-created_at')
    
    context = {
        'freelancer': user,
        'freelancer_profile': freelancer_profile,
        'projects': projects,
        'can_message': request.user.is_authenticated and request.user != user,
    }
    
    return render(request, 'accounts/freelancer_public_profile.html', context)
