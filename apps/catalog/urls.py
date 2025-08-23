from django.urls import path
from . import views

app_name = 'catalog'

urlpatterns = [
    # Uygulamalar
    path('', views.ApplicationListView.as_view(), name='application_list'),
    path('<slug:slug>/', views.ApplicationDetailView.as_view(), name='application_detail'),
]
