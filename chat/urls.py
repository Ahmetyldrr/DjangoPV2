from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.chat_list, name='chat_list'),
    path('room/<int:room_id>/', views.chat_room, name='room'),
    path('start/<int:user_id>/', views.start_chat, name='start_chat'),
    path('support/', views.start_support_chat, name='start_support_chat'),
    path('api/send-message/', views.send_message, name='send_message'),
    path('api/get-messages/<int:room_id>/', views.get_messages, name='get_messages'),
    path('api/mark-read/<int:message_id>/', views.mark_message_read, name='mark_message_read'),
]
