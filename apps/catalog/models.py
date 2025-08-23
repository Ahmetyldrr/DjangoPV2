from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Kategori Adı")
    slug = models.SlugField(max_length=100, unique=True, verbose_name="Slug")
    description = models.TextField(blank=True, verbose_name="Açıklama")
    is_active = models.BooleanField(default=True, verbose_name="Aktif")
    
    class Meta:
        verbose_name = "Kategori"
        verbose_name_plural = "Kategoriler"
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('categories:category_detail', kwargs={'slug': self.slug})


class Application(models.Model):
    title = models.CharField(max_length=200, verbose_name="Uygulama Adı")
    slug = models.SlugField(max_length=200, unique=True, verbose_name="Slug")
    short_description = models.CharField(max_length=300, verbose_name="Kısa Açıklama")
    description_markdown = models.TextField(verbose_name="Detaylı Açıklama (Markdown)")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='applications', verbose_name="Kategori")
    tags = models.CharField(max_length=200, blank=True, help_text="Virgülle ayırın", verbose_name="Etiketler")
    
    # Medya dosyaları
    image = models.ImageField(upload_to='apps/images/', blank=True, null=True, verbose_name="Uygulama Resmi")
    screenshot1 = models.ImageField(upload_to='apps/screenshots/', blank=True, null=True, verbose_name="Ekran Görüntüsü 1")
    screenshot2 = models.ImageField(upload_to='apps/screenshots/', blank=True, null=True, verbose_name="Ekran Görüntüsü 2")
    screenshot3 = models.ImageField(upload_to='apps/screenshots/', blank=True, null=True, verbose_name="Ekran Görüntüsü 3")
    pdf_file = models.FileField(upload_to='apps/docs/', blank=True, null=True, verbose_name="PDF Döküman")
    youtube_url = models.URLField(blank=True, null=True, verbose_name="YouTube Video Linki")
    
    is_active = models.BooleanField(default=True, verbose_name="Aktif")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Güncellenme Tarihi")
    view_count = models.PositiveIntegerField(default=0, verbose_name="Görüntülenme Sayısı")
    
    class Meta:
        verbose_name = "Uygulama"
        verbose_name_plural = "Uygulamalar"
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('catalog:application_detail', kwargs={'slug': self.slug})
    
    def get_tags_list(self):
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()]
    
    def get_youtube_embed_url(self):
        """YouTube URL'sini embed formatına çevirir"""
        if self.youtube_url:
            if 'watch?v=' in self.youtube_url:
                video_id = self.youtube_url.split('watch?v=')[1].split('&')[0]
                return f"https://www.youtube.com/embed/{video_id}"
            elif 'youtu.be/' in self.youtube_url:
                video_id = self.youtube_url.split('youtu.be/')[1].split('?')[0]
                return f"https://www.youtube.com/embed/{video_id}"
        return None
    
    def get_screenshots(self):
        """Tüm ekran görüntülerini liste olarak döndürür"""
        screenshots = []
        for i in range(1, 4):
            screenshot = getattr(self, f'screenshot{i}')
            if screenshot:
                screenshots.append(screenshot)
        return screenshots
