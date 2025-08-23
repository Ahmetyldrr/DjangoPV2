from django import forms
from .models import FreelancerApplication, ProjectOffer, FreelancerProject, ProjectCategory


class FreelancerApplicationForm(forms.ModelForm):
    """Freelancer başvuru formu"""
    
    class Meta:
        model = FreelancerApplication
        fields = [
            'full_name', 'email', 'phone', 'city',
            'title', 'experience_years', 'skill_level', 'skills',
            'portfolio_url', 'github_url', 'linkedin_url', 'cv_file',
            'cover_letter'
        ]
        
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ad Soyad'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'E-posta adresiniz'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '0555 123 45 67'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Yaşadığınız şehir'
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Örn: Full Stack Developer, UI/UX Designer'
            }),
            'experience_years': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'max': 50
            }),
            'skill_level': forms.Select(attrs={
                'class': 'form-select'
            }),
            'skills': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Python, Django, React, JavaScript, vb. (virgülle ayırın)'
            }),
            'portfolio_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://portfoyunuz.com'
            }),
            'github_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://github.com/kullaniciadi'
            }),
            'linkedin_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://linkedin.com/in/kullaniciadi'
            }),
            'cv_file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx'
            }),
            'cover_letter': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Neden FxApp freelancer platformunda çalışmak istiyorsunuz? Deneyimleriniz ve hedefleriniz hakkında bilgi verin.'
            }),
        }
    
    def clean_experience_years(self):
        experience = self.cleaned_data.get('experience_years')
        if experience is not None and experience < 0:
            raise forms.ValidationError('Deneyim yılı negatif olamaz.')
        return experience
    
    def clean_cv_file(self):
        cv = self.cleaned_data.get('cv_file')
        if cv:
            # Dosya boyutu kontrolü (5MB)
            if cv.size > 5 * 1024 * 1024:
                raise forms.ValidationError('CV dosyası 5MB\'dan büyük olamaz.')
            
            # Dosya uzantısı kontrolü
            allowed_extensions = ['.pdf', '.doc', '.docx']
            file_name = cv.name.lower()
            if not any(file_name.endswith(ext) for ext in allowed_extensions):
                raise forms.ValidationError('Sadece PDF, DOC ve DOCX dosyaları kabul edilir.')
        
        return cv


class FreelancerProjectForm(forms.ModelForm):
    """Freelancer proje oluşturma formu"""
    
    class Meta:
        model = FreelancerProject
        fields = [
            'title', 'description', 'category', 'technologies', 
            'project_url', 'github_url', 'image', 'budget_range',
            'completion_date', 'is_featured'
        ]
        
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Proje başlığı',
                'required': True
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Proje hakkında detaylı açıklama...',
                'required': True
            }),
            'category': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'technologies': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Python, Django, React, JavaScript (virgülle ayırın)',
                'required': True
            }),
            'project_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://proje-url.com (opsiyonel)'
            }),
            'github_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://github.com/kullanici/proje (opsiyonel)'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'budget_range': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'completion_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'is_featured': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Kategori seçeneklerini ayarla
        category_choices = [('', 'Kategori seçin')] + [
            (cat.id, cat.name) for cat in ProjectCategory.objects.all()
        ]
        self.fields['category'].choices = category_choices
    
    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            # Dosya boyutu kontrolü (5MB)
            if image.size > 5 * 1024 * 1024:
                raise forms.ValidationError('Görsel 5MB\'dan büyük olamaz.')
            
            # Dosya uzantısı kontrolü
            allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
            file_name = image.name.lower()
            if not any(file_name.endswith(ext) for ext in allowed_extensions):
                raise forms.ValidationError('Sadece JPG, PNG, GIF ve WebP formatları kabul edilir.')
        
        return image


class ProjectOfferForm(forms.ModelForm):
    """Proje teklif formu"""
    
    class Meta:
        model = ProjectOffer
        fields = [
            'client_name', 'client_email', 'client_phone', 'company_name',
            'offer_amount', 'message', 'timeline'
        ]
        
        widgets = {
            'client_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ad Soyad',
                'required': True
            }),
            'client_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'E-posta adresiniz',
                'required': True
            }),
            'client_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '0555 123 45 67'
            }),
            'company_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Firma adınız (opsiyonel)'
            }),
            'offer_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'step': '0.01',
                'placeholder': 'Teklif tutarınız (TL)',
                'required': True
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Proje hakkında detaylar ve talepleriniz...',
                'required': True
            }),
            'timeline': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Örn: 2 hafta, 1 ay, acil',
                'required': True
            }),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Eğer kullanıcı giriş yapmışsa, form alanlarını otomatik doldur
        if user and user.is_authenticated:
            self.fields['client_name'].initial = user.get_full_name()
            self.fields['client_email'].initial = user.email
    
    def clean_offer_amount(self):
        amount = self.cleaned_data.get('offer_amount')
        if amount is not None and amount <= 0:
            raise forms.ValidationError('Teklif tutarı pozitif bir değer olmalıdır.')
        return amount


class ProjectSearchForm(forms.Form):
    """Proje arama formu"""
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Proje ara...'
        })
    )
    
    category = forms.CharField(
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    budget = forms.CharField(
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    sort = forms.CharField(
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )


class FreelancerSearchForm(forms.Form):
    """Freelancer arama formu"""
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Freelancer ara...'
        })
    )
    
    skill_level = forms.CharField(
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    city = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Şehir'
        })
    )
    
    available = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    
    sort = forms.CharField(
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
