from django.urls import path
from . import views

app_name = 'careers'

urlpatterns = [
    # Ana sayfa
    path('', views.careers_home, name='home'),
    
    # Başvuru
    path('basvuru/', views.FreelancerApplicationView.as_view(), name='apply'),
    path('basvuru/basarili/', views.application_success, name='application_success'),
    
    # Freelancer'lar
    path('freelancerlar/', views.FreelancerListView.as_view(), name='freelancer_list'),
    path('freelancer/<int:user_id>/', views.FreelancerDetailView.as_view(), name='freelancer_detail'),
    
    # Projeler
    path('projeler/', views.ProjectListView.as_view(), name='project_list'),
    path('proje/olustur/', views.FreelancerProjectCreateView.as_view(), name='project_create'),
    path('proje/<slug:slug>/', views.ProjectDetailView.as_view(), name='project_detail'),
    path('proje/<slug:slug>/teklif/', views.submit_offer, name='submit_offer'),
]
