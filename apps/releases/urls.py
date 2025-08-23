from django.urls import path
from . import views

app_name = 'releases'

urlpatterns = [
    path('<int:pk>/', views.ReleaseDownloadView.as_view(), name='download'),
]
