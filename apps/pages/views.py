from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, ListView, DetailView
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from apps.catalog.models import Application, Category
from chat.models import ChatRoom, Message
from .models import ContactMessage
from .forms import ContactForm, AdminReplyForm


def is_admin_or_staff(user):
    return user.is_authenticated and (user.is_staff or user.user_type == 'admin')


class HomeView(TemplateView):
    template_name = 'pages/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['recent_applications'] = Application.objects.filter(is_active=True)[:6]
        context['categories'] = Category.objects.filter(is_active=True)
        return context


class AboutView(TemplateView):
    template_name = 'pages/about.html'


class ContactView(TemplateView):
    template_name = 'pages/contact.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ContactForm()
        return context
    
    def post(self, request, *args, **kwargs):
        form = ContactForm(request.POST)
        if form.is_valid():
            # Veritabanına kaydet
            contact_message = form.save_to_database()
            
            # E-posta gönder (opsiyonel)
            form.send_email()
            
            messages.success(request, 'Mesajınız başarıyla gönderildi! En kısa sürede size dönüş yapacağız.')
            return redirect('pages:contact')
        
        context = self.get_context_data(**kwargs)
        context['form'] = form
        return self.render_to_response(context)


@method_decorator([login_required, user_passes_test(is_admin_or_staff)], name='dispatch')
class AdminDashboardView(TemplateView):
    """Admin dashboard - mesaj ve chat yönetimi"""
    template_name = 'pages/admin_dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # İletişim mesajları istatistikleri
        context['new_messages_count'] = ContactMessage.objects.filter(status='new').count()
        context['urgent_messages_count'] = ContactMessage.objects.filter(
            status='new',
            created_at__lt=timezone.now() - timezone.timedelta(hours=24)
        ).count()
        
        # Chat istatistikleri
        context['total_chat_rooms'] = ChatRoom.objects.count()
        context['active_chats'] = ChatRoom.objects.filter(
            messages__created_at__gte=timezone.now() - timezone.timedelta(days=1)
        ).distinct().count()
        
        # Son mesajlar
        context['recent_contact_messages'] = ContactMessage.objects.all()[:5]
        context['recent_chat_messages'] = Message.objects.select_related(
            'sender', 'room'
        ).order_by('-created_at')[:10]
        
        return context


@method_decorator([login_required, user_passes_test(is_admin_or_staff)], name='dispatch')
class AdminContactMessagesView(ListView):
    """Admin iletişim mesajları listesi"""
    model = ContactMessage
    template_name = 'pages/admin_contact_messages.html'
    context_object_name = 'messages'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = ContactMessage.objects.all()
        
        # Filtreleme
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_filter'] = self.request.GET.get('status', '')
        context['status_choices'] = ContactMessage.STATUS_CHOICES
        return context


@method_decorator([login_required, user_passes_test(is_admin_or_staff)], name='dispatch')
class AdminContactMessageDetailView(DetailView):
    """Admin iletişim mesajı detay ve cevaplama"""
    model = ContactMessage
    template_name = 'pages/admin_contact_message_detail.html'
    context_object_name = 'message'
    
    def get_object(self):
        obj = super().get_object()
        # Mesajı okundu olarak işaretle
        if obj.status == 'new':
            obj.status = 'read'
            obj.read_at = timezone.now()
            obj.save()
        return obj
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reply_form'] = AdminReplyForm(instance=self.object)
        return context
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = AdminReplyForm(request.POST, instance=self.object)
        
        if form.is_valid():
            reply = form.save(commit=False)
            reply.admin_user = request.user
            
            if reply.admin_reply and reply.status in ['replied', 'closed']:
                reply.replied_at = timezone.now()
                
                # Müşteriye e-posta gönder
                try:
                    send_mail(
                        subject=f'Re: {reply.subject}',
                        message=f"""
Merhaba {reply.name},

Mesajınıza cevabımız:

{reply.admin_reply}

---
İyi günler,
FxApp Ekibi
                        """,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[reply.email],
                        fail_silently=True,
                    )
                    messages.success(request, 'Cevap gönderildi ve müşteriye e-posta ile bildirildi.')
                except:
                    messages.warning(request, 'Cevap kaydedildi ancak e-posta gönderilemedi.')
            
            reply.save()
            return redirect('pages:admin_contact_message_detail', pk=self.object.pk)
        
        context = self.get_context_data(**kwargs)
        context['reply_form'] = form
        return self.render_to_response(context)


@method_decorator([login_required, user_passes_test(is_admin_or_staff)], name='dispatch')
class AdminChatRoomsView(ListView):
    """Admin chat odaları listesi"""
    model = ChatRoom
    template_name = 'pages/admin_chat_rooms.html'
    context_object_name = 'chat_rooms'
    paginate_by = 20
    
    def get_queryset(self):
        return ChatRoom.objects.prefetch_related('participants').order_by('-updated_at')
