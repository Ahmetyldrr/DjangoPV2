from django import forms
from django.core.mail import send_mail
from django.conf import settings
from .models import ContactMessage


class ContactForm(forms.Form):
    """İletişim formu"""
    
    name = forms.CharField(
        label='Ad Soyad',
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Adınız ve soyadınız'
        })
    )
    
    email = forms.EmailField(
        label='E-posta',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'ornek@email.com'
        })
    )
    
    phone = forms.CharField(
        label='Telefon',
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+90 5xx xxx xx xx'
        })
    )
    
    subject = forms.CharField(
        label='Konu',
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Mesajınızın konusu'
        })
    )
    
    message = forms.CharField(
        label='Mesaj',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'placeholder': 'Mesajınızı buraya yazın...'
        })
    )
    
    def save_to_database(self):
        """Mesajı veritabanına kaydet"""
        contact_message = ContactMessage.objects.create(
            name=self.cleaned_data['name'],
            email=self.cleaned_data['email'],
            phone=self.cleaned_data.get('phone', ''),
            subject=self.cleaned_data['subject'],
            message=self.cleaned_data['message']
        )
        return contact_message
    
    def send_email(self):
        """Formu e-posta olarak gönder"""
        name = self.cleaned_data['name']
        email = self.cleaned_data['email']
        phone = self.cleaned_data.get('phone', '')
        subject = self.cleaned_data['subject']
        message = self.cleaned_data['message']
        
        # E-posta içeriği
        email_message = f"""
Yeni İletişim Formu Mesajı

Ad Soyad: {name}
E-posta: {email}
Telefon: {phone if phone else 'Belirtilmemiş'}
Konu: {subject}

Mesaj:
{message}

---
Bu mesaj FxApp iletişim formu üzerinden gönderilmiştir.
        """
        
        try:
            # E-posta gönder
            send_mail(
                subject=f'İletişim Formu: {subject}',
                message=email_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.CONTACT_EMAIL],
                fail_silently=False,
            )
            return True
        except Exception as e:
            print(f"E-posta gönderilemedi: {e}")
            return False


class AdminReplyForm(forms.ModelForm):
    """Admin cevap formu"""
    
    class Meta:
        model = ContactMessage
        fields = ['admin_reply', 'status']
        widgets = {
            'admin_reply': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Cevabınızı buraya yazın...'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            })
        }
        labels = {
            'admin_reply': 'Cevap',
            'status': 'Durum'
        }
