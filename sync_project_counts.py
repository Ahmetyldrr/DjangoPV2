#!/usr/bin/env python
import os
import sys
import django

# Django ayarlarını yükle
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from accounts.models import FreelancerProfile
from apps.careers.models import FreelancerProject

def sync_project_counts():
    """FreelancerProfile'daki total_projects field'ını gerçek proje sayısıyla senkronize et"""
    
    print("FreelancerProfile proje sayılarını güncelleniyor...")
    
    for profile in FreelancerProfile.objects.all():
        actual_count = FreelancerProject.objects.filter(freelancer=profile).count()
        
        if profile.total_projects != actual_count:
            print(f"Updating {profile.user.get_full_name()}: {profile.total_projects} -> {actual_count}")
            profile.total_projects = actual_count
            profile.save()
        else:
            print(f"Profile {profile.user.get_full_name()}: OK ({actual_count} projects)")
    
    print("Güncelleme tamamlandı!")

if __name__ == '__main__':
    sync_project_counts()
