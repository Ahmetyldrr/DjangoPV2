#!/usr/bin/env python
import os
import sys
import django
from decimal import Decimal

# Django kurulumu
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from accounts.models import FreelancerProfile
from apps.careers.models import FreelancerProject

# Her freelancer'ın istatistiklerini güncelle
for profile in FreelancerProfile.objects.all():
    projects = FreelancerProject.objects.filter(freelancer=profile)
    completed_count = projects.filter(status='completed').count()
    total_count = projects.count()
    
    profile.total_projects = total_count
    if completed_count > 0:
        # Completed projeler için kazanç simülasyonu
        profile.total_earnings = Decimal(completed_count * 8000)  # Ortalama 8000 TL per proje
    profile.save()
    print(f"{profile.user.get_full_name()}: {total_count} toplam proje, {completed_count} tamamlanan, {profile.total_earnings} TL kazanç")

print("İstatistikler güncellendi!")
