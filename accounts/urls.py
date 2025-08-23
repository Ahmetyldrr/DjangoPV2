from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Profil sayfaları
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.UserProfileUpdateView.as_view(), name='profile_edit'),
    
    # Freelancer sayfaları
    path('freelancer/dashboard/', views.freelancer_dashboard, name='freelancer_dashboard'),
    path('freelancer/profile/edit/', views.FreelancerProfileUpdateView.as_view(), name='freelancer_profile_edit'),
    path('freelancer/become/', views.become_freelancer, name='become_freelancer'),
    path('freelancer/<int:user_id>/', views.freelancer_public_profile, name='freelancer_public_profile'),
]
