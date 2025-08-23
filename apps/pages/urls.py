from django.urls import path
from . import views

app_name = 'pages'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('hakkinda/', views.AboutView.as_view(), name='about'),
    path('iletisim/', views.ContactView.as_view(), name='contact'),
    
    # Admin Panel
    path('admin-panel/', views.AdminDashboardView.as_view(), name='admin_dashboard'),
    path('admin-panel/mesajlar/', views.AdminContactMessagesView.as_view(), name='admin_contact_messages'),
    path('admin-panel/mesaj/<int:pk>/', views.AdminContactMessageDetailView.as_view(), name='admin_contact_message_detail'),
    path('admin-panel/chat-odalari/', views.AdminChatRoomsView.as_view(), name='admin_chat_rooms'),
]
