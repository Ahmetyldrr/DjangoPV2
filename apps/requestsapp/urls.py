from django.urls import path
from . import views

app_name = 'requestsapp'

urlpatterns = [
    path('yeni/', views.UserRequestCreateView.as_view(), name='create'),
    path('basarili/', views.UserRequestSuccessView.as_view(), name='success'),
]
