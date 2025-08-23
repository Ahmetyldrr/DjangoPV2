from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.urls import reverse
from decimal import Decimal


class UserManager(BaseUserManager):
    """Custom user manager for email-based authentication"""
    
    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular user with the given email and password."""
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """Create and save a superuser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('user_type', 'admin')
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Custom user model"""
    
    USER_TYPE_CHOICES = [
        ('client', 'Müşteri'),
        ('freelancer', 'Freelancer'),
        ('admin', 'Admin'),
    ]
    
    email = models.EmailField('E-posta', unique=True)
    user_type = models.CharField('Kullanıcı Tipi', max_length=20, 
                                choices=USER_TYPE_CHOICES, default='client')
    phone = models.CharField('Telefon', max_length=20, blank=True)
    avatar = models.ImageField('Avatar', upload_to='avatars/', blank=True, null=True)
    bio = models.TextField('Hakkında', blank=True)
    website = models.URLField('Website', blank=True)
    is_verified = models.BooleanField('Doğrulanmış', default=False)
    created_at = models.DateTimeField('Kayıt Tarihi', auto_now_add=True)
    updated_at = models.DateTimeField('Güncellenme Tarihi', auto_now=True)
    
    # Remove username field
    username = None
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    # Use custom manager
    objects = UserManager()
    
    class Meta:
        verbose_name = 'Kullanıcı'
        verbose_name_plural = 'Kullanıcılar'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.get_full_name() or self.email
    
    def get_absolute_url(self):
        if self.user_type == 'freelancer':
            return reverse('accounts:freelancer_dashboard')
        return reverse('accounts:profile')
    
    @property
    def is_freelancer(self):
        return self.user_type == 'freelancer'
    
    @property
    def is_client(self):
        return self.user_type == 'client'


class FreelancerProfile(models.Model):
    """Freelancer için ek profil bilgileri"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='freelancer_profile')
    
    # Professional Info
    title = models.CharField('Ünvan', max_length=200)
    skills = models.TextField('Yetenekler (virgülle ayırın)')
    experience_years = models.IntegerField('Deneyim (yıl)', default=0)
    hourly_rate = models.DecimalField('Saatlik Ücret (TL)', max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Location
    city = models.CharField('Şehir', max_length=100)
    country = models.CharField('Ülke', max_length=100, default='Türkiye')
    
    # Portfolio
    portfolio_url = models.URLField('Portfolio URL', blank=True)
    github_url = models.URLField('GitHub URL', blank=True)
    linkedin_url = models.URLField('LinkedIn URL', blank=True)
    
    # Status
    is_available = models.BooleanField('Müsait', default=True)
    is_verified = models.BooleanField('Doğrulanmış', default=False)
    
    # Stats
    total_projects = models.IntegerField('Toplam Proje', default=0)
    total_earnings = models.DecimalField('Toplam Kazanç', max_digits=12, decimal_places=2, default=Decimal('0.00'))
    rating = models.DecimalField('Puan', max_digits=3, decimal_places=2, default=Decimal('5.00'))
    rating_count = models.IntegerField('Puan Sayısı', default=0)
    
    created_at = models.DateTimeField('Oluşturulma Tarihi', auto_now_add=True)
    updated_at = models.DateTimeField('Güncellenme Tarihi', auto_now=True)
    
    class Meta:
        verbose_name = 'Freelancer Profili'
        verbose_name_plural = 'Freelancer Profilleri'
        ordering = ['-rating', '-total_projects']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.title}"
    
    def get_absolute_url(self):
        """Freelancer'ın public profil sayfası"""
        return reverse('accounts:freelancer_public_profile', kwargs={'user_id': self.user.pk})
    
    @property
    def skills_list(self):
        return [skill.strip() for skill in self.skills.split(',') if skill.strip()]
    
    def update_stats(self):
        """İstatistikleri güncelle"""
        from apps.careers.models import FreelancerProject
        projects = FreelancerProject.objects.filter(freelancer=self)
        self.total_projects = projects.filter(status='completed').count()
        # Diğer istatistikler de buraya eklenebilir
        self.save()
