from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils.text import slugify
from decimal import Decimal

class FreelancerApplication(models.Model):
    """Freelancer başvuru modeli"""
    
    STATUS_CHOICES = [
        ('pending', 'Beklemede'),
        ('approved', 'Onaylandı'),
        ('rejected', 'Reddedildi'),
    ]
    
    SKILL_LEVEL_CHOICES = [
        ('beginner', 'Başlangıç'),
        ('intermediate', 'Orta'),
        ('advanced', 'İleri'),
        ('expert', 'Uzman'),
    ]
    
    # Kişisel Bilgiler
    full_name = models.CharField('Ad Soyad', max_length=200)
    email = models.EmailField('E-posta')
    phone = models.CharField('Telefon', max_length=20)
    city = models.CharField('Şehir', max_length=100)
    
    # Profesyonel Bilgiler
    title = models.CharField('Uzmanlık Alanı', max_length=200)
    experience_years = models.IntegerField('Deneyim Yılı')
    skill_level = models.CharField('Seviye', max_length=20, choices=SKILL_LEVEL_CHOICES)
    skills = models.TextField('Teknik Yetenekler', help_text='Virgülle ayırarak yazın')
    
    # Portföy
    portfolio_url = models.URLField('Portföy/Website', blank=True)
    github_url = models.URLField('GitHub', blank=True)
    linkedin_url = models.URLField('LinkedIn', blank=True)
    
    # Özgeçmiş ve Açıklama
    cv_file = models.FileField('CV Dosyası', upload_to='careers/cvs/', blank=True)
    cover_letter = models.TextField('Kapak Mektubu', max_length=1000)
    
    # Başvuru Bilgileri
    status = models.CharField('Durum', max_length=20, choices=STATUS_CHOICES, default='pending')
    applied_at = models.DateTimeField('Başvuru Tarihi', auto_now_add=True)
    reviewed_at = models.DateTimeField('İnceleme Tarihi', blank=True, null=True)
    reviewer_notes = models.TextField('İnceleme Notları', blank=True)
    
    class Meta:
        verbose_name = 'Freelancer Başvurusu'
        verbose_name_plural = 'Freelancer Başvuruları'
        ordering = ['-applied_at']
    
    def __str__(self):
        return f"{self.full_name} - {self.title}"
    
    @property
    def skills_list(self):
        """Yetenekleri liste olarak döndür"""
        return [skill.strip() for skill in self.skills.split(',') if skill.strip()]


class FreelancerProfile(models.Model):
    """Onaylanmış freelancer profilleri"""
    
    application = models.OneToOneField(FreelancerApplication, on_delete=models.CASCADE, 
                                     related_name='profile')
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)
    slug = models.SlugField(unique=True, blank=True)
    
    # Profil Bilgileri
    bio = models.TextField('Kısa Biyografi', max_length=500, blank=True)
    profile_image = models.ImageField('Profil Resmi', upload_to='careers/profiles/', 
                                    blank=True, null=True)
    
    # İstatistikler
    total_projects = models.IntegerField('Toplam Proje', default=0)
    total_earnings = models.DecimalField('Toplam Kazanç', max_digits=10, decimal_places=2, default=Decimal('0.00'))
    rating = models.FloatField('Değerlendirme', default=5.0)
    
    # Ayarlar
    is_active = models.BooleanField('Aktif', default=True)
    is_available = models.BooleanField('Çalışmaya Uygun', default=True)
    hourly_rate = models.DecimalField('Saatlik Ücret (TL)', max_digits=10, decimal_places=2, 
                                    blank=True, null=True)
    
    created_at = models.DateTimeField('Oluşturulma Tarihi', auto_now_add=True)
    updated_at = models.DateTimeField('Güncellenme Tarihi', auto_now=True)
    
    class Meta:
        verbose_name = 'Freelancer Profili'
        verbose_name_plural = 'Freelancer Profilleri'
        ordering = ['-rating', '-total_projects']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.application.full_name}")
            self.slug = base_slug
            counter = 1
            while FreelancerProfile.objects.filter(slug=self.slug).exists():
                self.slug = f"{base_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('careers:freelancer_detail', kwargs={'slug': self.slug})
    
    def __str__(self):
        return f"{self.application.full_name} - {self.application.title}"


class ProjectCategory(models.Model):
    """Proje kategorileri"""
    name = models.CharField('Kategori Adı', max_length=100)
    description = models.TextField('Açıklama', blank=True)
    icon = models.CharField('Icon Sınıfı', max_length=50, default='fas fa-code')
    slug = models.SlugField(unique=True, blank=True)
    
    class Meta:
        verbose_name = 'Proje Kategorisi'
        verbose_name_plural = 'Proje Kategorileri'
        ordering = ['name']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name


class FreelancerProject(models.Model):
    """Freelancer'ların paylaştığı projeler"""
    
    STATUS_CHOICES = [
        ('draft', 'Taslak'),
        ('published', 'Yayında'),
        ('completed', 'Tamamlandı'),
        ('cancelled', 'İptal Edildi'),
    ]
    
    BUDGET_CHOICES = [
        ('under_1000', '1.000 TL altı'),
        ('1000_5000', '1.000 - 5.000 TL'),
        ('5000_10000', '5.000 - 10.000 TL'),
        ('10000_25000', '10.000 - 25.000 TL'),
        ('25000_50000', '25.000 - 50.000 TL'),
        ('over_50000', '50.000 TL üzeri'),
    ]
    
    freelancer = models.ForeignKey('accounts.FreelancerProfile', on_delete=models.CASCADE, 
                                 related_name='career_projects')
    category = models.ForeignKey(ProjectCategory, on_delete=models.SET_NULL, 
                               null=True, blank=True)
    
    # Proje Bilgileri
    title = models.CharField('Proje Başlığı', max_length=200)
    description = models.TextField('Proje Açıklaması')
    slug = models.SlugField(unique=True, blank=True)
    
    # Teknik Detaylar
    technologies = models.CharField('Kullanılan Teknolojiler', max_length=500)
    requirements = models.TextField('Gereksinimler', blank=True)
    deliverables = models.TextField('Teslim Edilecekler')
    
    # Zaman ve Bütçe
    estimated_duration = models.CharField('Tahmini Süre', max_length=100)
    budget_range = models.CharField('Bütçe Aralığı', max_length=20, choices=BUDGET_CHOICES)
    
    # Medya
    image = models.ImageField('Proje Görseli', upload_to='careers/projects/', 
                             blank=True, null=True)
    featured_image = models.ImageField('Öne Çıkan Görsel', upload_to='careers/projects/', 
                                     blank=True, null=True)
    project_url = models.URLField('Proje URL', blank=True, help_text='Canlı proje bağlantısı')
    demo_url = models.URLField('Demo/Canlı Link', blank=True)
    github_url = models.URLField('GitHub Repo', blank=True)
    
    # Tarih
    completion_date = models.DateField('Tamamlanma Tarihi', blank=True, null=True)
    
    # Durum
    status = models.CharField('Durum', max_length=20, choices=STATUS_CHOICES, default='draft')
    is_featured = models.BooleanField('Öne Çıkan', default=False)
    
    # İstatistikler
    views = models.IntegerField('Görüntülenme', default=0)
    offers_count = models.IntegerField('Teklif Sayısı', default=0)
    
    created_at = models.DateTimeField('Oluşturulma Tarihi', auto_now_add=True)
    updated_at = models.DateTimeField('Güncellenme Tarihi', auto_now=True)
    
    class Meta:
        verbose_name = 'Freelancer Projesi'
        verbose_name_plural = 'Freelancer Projeleri'
        ordering = ['-is_featured', '-created_at']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            self.slug = base_slug
            counter = 1
            while FreelancerProject.objects.filter(slug=self.slug).exists():
                self.slug = f"{base_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('careers:project_detail', kwargs={'slug': self.slug})
    
    def __str__(self):
        return f"{self.title} - {self.freelancer.user.get_full_name()}"
    
    @property
    def technologies_list(self):
        """Teknolojileri liste olarak döndür"""
        return [tech.strip() for tech in self.technologies.split(',') if tech.strip()]


class ProjectOffer(models.Model):
    """Projelere gelen teklifler"""
    
    STATUS_CHOICES = [
        ('pending', 'Beklemede'),
        ('accepted', 'Kabul Edildi'),
        ('rejected', 'Reddedildi'),
        ('withdrawn', 'Geri Çekildi'),
    ]
    
    project = models.ForeignKey(FreelancerProject, on_delete=models.CASCADE, 
                              related_name='offers')
    
    # Teklif Veren Bilgileri
    client_name = models.CharField('Müşteri Adı', max_length=200)
    client_email = models.EmailField('Müşteri E-posta')
    client_phone = models.CharField('Müşteri Telefon', max_length=20, blank=True)
    company_name = models.CharField('Firma Adı', max_length=200, blank=True)
    
    # Teklif Detayları
    offer_amount = models.DecimalField('Teklif Tutarı (TL)', max_digits=10, decimal_places=2)
    message = models.TextField('Mesaj', max_length=1000)
    timeline = models.CharField('Zaman Çizelgesi', max_length=200)
    
    # Durum
    status = models.CharField('Durum', max_length=20, choices=STATUS_CHOICES, default='pending')
    
    created_at = models.DateTimeField('Teklif Tarihi', auto_now_add=True)
    responded_at = models.DateTimeField('Yanıtlanma Tarihi', blank=True, null=True)
    response_message = models.TextField('Yanıt Mesajı', blank=True)
    
    class Meta:
        verbose_name = 'Proje Teklifi'
        verbose_name_plural = 'Proje Teklifleri'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.client_name} -> {self.project.title} ({self.offer_amount} TL)"


class ProjectImage(models.Model):
    """Proje görselleri"""
    project = models.ForeignKey(FreelancerProject, on_delete=models.CASCADE, 
                              related_name='images')
    image = models.ImageField('Görsel', upload_to='careers/project_images/')
    caption = models.CharField('Açıklama', max_length=200, blank=True)
    order = models.IntegerField('Sıra', default=0)
    
    class Meta:
        verbose_name = 'Proje Görseli'
        verbose_name_plural = 'Proje Görselleri'
        ordering = ['order']
    
    def __str__(self):
        return f"{self.project.title} - Görsel {self.order}"
