from django.db import models


class UserRequest(models.Model):
    full_name = models.CharField(max_length=100, verbose_name="Ad Soyad")
    email = models.EmailField(verbose_name="E-posta")
    subject = models.CharField(max_length=200, verbose_name="Konu")
    message = models.TextField(verbose_name="Mesaj")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")
    
    class Meta:
        verbose_name = "Kullanıcı Talebi"
        verbose_name_plural = "Kullanıcı Talepleri"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.full_name} - {self.subject}"
