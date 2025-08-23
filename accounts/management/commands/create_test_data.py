from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.models import FreelancerProfile
from chat.models import ChatRoom, Message, ProjectOffer
from apps.careers.models import FreelancerApplication, ProjectCategory
from apps.requestsapp.models import UserRequest
from decimal import Decimal
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Test verileri oluşturur'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Test verileri oluşturuluyor...'))
        
        # Kategoriler oluştur
        categories = [
            ('Web Geliştirme', 'Web sitesi ve web uygulaması geliştirme', 'fas fa-code'),
            ('Mobil Uygulama', 'iOS ve Android uygulama geliştirme', 'fas fa-mobile-alt'),
            ('Grafik Tasarım', 'Logo, poster, web tasarımı', 'fas fa-paint-brush'),
            ('Yazılım Geliştirme', 'Masaüstü yazılım ve sistem geliştirme', 'fas fa-laptop-code'),
            ('Dijital Pazarlama', 'SEO, sosyal medya, reklam yönetimi', 'fas fa-chart-line'),
            ('İçerik Yazımı', 'Blog, makale, metin yazımı', 'fas fa-pen'),
        ]
        
        for name, desc, icon in categories:
            ProjectCategory.objects.get_or_create(
                name=name,
                defaults={'description': desc, 'icon': icon}
            )
        
        # Kullanıcılar oluştur
        users_data = [
            {
                'email': 'ahmet.yilmaz@test.com',
                'first_name': 'Ahmet',
                'last_name': 'Yılmaz',
                'user_type': 'freelancer',
                'phone': '+90 532 123 4567',
                'bio': 'Deneyimli web geliştirici. 5 yıllık sektör tecrübesi.',
                'freelancer_data': {
                    'title': 'Full Stack Web Developer',
                    'skills': 'Python, Django, React, JavaScript, PostgreSQL',
                    'experience_years': 5,
                    'hourly_rate': Decimal('150.00'),
                    'city': 'İstanbul',
                    'portfolio_url': 'https://ahmetyilmaz.dev',
                    'github_url': 'https://github.com/ahmetyilmaz',
                    'total_projects': 23,
                    'total_earnings': Decimal('45000.00'),
                    'rating': Decimal('4.8'),
                }
            },
            {
                'email': 'zeynep.kaya@test.com',
                'first_name': 'Zeynep',
                'last_name': 'Kaya',
                'user_type': 'freelancer',
                'phone': '+90 533 234 5678',
                'bio': 'UI/UX Designer ve Frontend Developer. Yaratıcı çözümler üretiyorum.',
                'freelancer_data': {
                    'title': 'UI/UX Designer & Frontend Developer',
                    'skills': 'Figma, Adobe XD, React, Vue.js, CSS, HTML',
                    'experience_years': 3,
                    'hourly_rate': Decimal('120.00'),
                    'city': 'Ankara',
                    'portfolio_url': 'https://zeynepkaya.design',
                    'linkedin_url': 'https://linkedin.com/in/zeynepkaya',
                    'total_projects': 18,
                    'total_earnings': Decimal('32000.00'),
                    'rating': Decimal('4.9'),
                }
            },
            {
                'email': 'mehmet.demir@test.com',
                'first_name': 'Mehmet',
                'last_name': 'Demir',
                'user_type': 'freelancer',
                'phone': '+90 534 345 6789',
                'bio': 'Mobil uygulama geliştirme uzmanı. iOS ve Android deneyimi.',
                'freelancer_data': {
                    'title': 'Mobile App Developer',
                    'skills': 'React Native, Flutter, Swift, Kotlin, Firebase',
                    'experience_years': 4,
                    'hourly_rate': Decimal('180.00'),
                    'city': 'İzmir',
                    'github_url': 'https://github.com/mehmetdemir',
                    'linkedin_url': 'https://linkedin.com/in/mehmetdemir',
                    'total_projects': 15,
                    'total_earnings': Decimal('38000.00'),
                    'rating': Decimal('4.7'),
                }
            },
            {
                'email': 'ayse.ozkan@test.com',
                'first_name': 'Ayşe',
                'last_name': 'Özkan',
                'user_type': 'client',
                'phone': '+90 535 456 7890',
                'bio': 'E-ticaret şirketi sahibi. Dijital çözümler arıyorum.',
            },
            {
                'email': 'can.yildirim@test.com',
                'first_name': 'Can',
                'last_name': 'Yıldırım',
                'user_type': 'client',
                'phone': '+90 536 567 8901',
                'bio': 'Startup kurucusu. Teknoloji projeleri geliştiriyorum.',
            },
            {
                'email': 'elif.celik@test.com',
                'first_name': 'Elif',
                'last_name': 'Çelik',
                'user_type': 'freelancer',
                'phone': '+90 537 678 9012',
                'bio': 'Grafik tasarım ve dijital pazarlama uzmanı.',
                'freelancer_data': {
                    'title': 'Graphic Designer & Digital Marketer',
                    'skills': 'Adobe Creative Suite, Canva, Google Ads, Facebook Ads',
                    'experience_years': 2,
                    'hourly_rate': Decimal('100.00'),
                    'city': 'Bursa',
                    'portfolio_url': 'https://elifcelik.art',
                    'total_projects': 12,
                    'total_earnings': Decimal('18000.00'),
                    'rating': Decimal('4.6'),
                }
            },
        ]
        
        created_users = []
        for user_data in users_data:
            user, created = User.objects.get_or_create(
                email=user_data['email'],
                defaults={
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name'],
                    'user_type': user_data['user_type'],
                    'phone': user_data.get('phone', ''),
                    'bio': user_data.get('bio', ''),
                    'is_verified': True,
                }
            )
            if created:
                user.set_password('test123456')
                user.save()
                self.stdout.write(f'Kullanıcı oluşturuldu: {user.get_full_name()}')
            
            created_users.append(user)
            
            # Freelancer profili oluştur
            if user.user_type == 'freelancer' and 'freelancer_data' in user_data:
                freelancer_data = user_data['freelancer_data']
                freelancer_profile, fp_created = FreelancerProfile.objects.get_or_create(
                    user=user,
                    defaults=freelancer_data
                )
                if fp_created:
                    self.stdout.write(f'Freelancer profili oluşturuldu: {freelancer_profile.title}')
        
        # Freelancer başvuruları oluştur
        applications_data = [
            {
                'full_name': 'Fatma Şahin',
                'email': 'fatma.sahin@test.com',
                'phone': '+90 538 789 0123',
                'city': 'Antalya',
                'title': 'Content Writer & Translator',
                'experience_years': 3,
                'skill_level': 'intermediate',
                'skills': 'Content Writing, SEO Writing, Turkish-English Translation',
                'cover_letter': 'Merhaba, 3 yıllık deneyimim ile kaliteli içerik üretimi konusunda uzmanım.',
                'status': 'pending',
            },
            {
                'full_name': 'Emre Kara',
                'email': 'emre.kara@test.com',
                'phone': '+90 539 890 1234',
                'city': 'Eskişehir',
                'title': 'Python Backend Developer',
                'experience_years': 6,
                'skill_level': 'expert',
                'skills': 'Python, Django, FastAPI, PostgreSQL, Docker, AWS',
                'cover_letter': 'Backend geliştirme konusunda 6 yıllık deneyimim bulunmaktadır.',
                'status': 'approved',
            },
        ]
        
        for app_data in applications_data:
            app, created = FreelancerApplication.objects.get_or_create(
                email=app_data['email'],
                defaults=app_data
            )
            if created:
                self.stdout.write(f'Freelancer başvurusu oluşturuldu: {app.full_name}')
        
        # Chat odaları oluştur
        freelancers = User.objects.filter(user_type='freelancer')
        clients = User.objects.filter(user_type='client')
        
        if freelancers.exists() and clients.exists():
            # Birkaç chat odası oluştur
            for i in range(3):
                freelancer = random.choice(freelancers)
                client = random.choice(clients)
                
                chat_room, created = ChatRoom.objects.get_or_create(
                    name=f"Proje Görüşmesi - {freelancer.first_name} & {client.first_name}",
                )
                if created:
                    chat_room.participants.add(freelancer, client)
                    self.stdout.write(f'Chat odası oluşturuldu: {chat_room.name}')
                    
                    # Örnek mesajlar
                    messages_data = [
                        (client, f"Merhaba {freelancer.first_name}, projem hakkında konuşabilir miyiz?"),
                        (freelancer, f"Tabii ki {client.first_name}! Projenizin detaylarını dinliyorum."),
                        (client, "E-ticaret sitesi için yardıma ihtiyacım var. Ne kadar sürer?"),
                        (freelancer, "Projenin kapsamına bağlı olarak 2-4 hafta arasında teslim edebilirim."),
                    ]
                    
                    for sender, content in messages_data:
                        Message.objects.create(
                            room=chat_room,
                            sender=sender,
                            content=content,
                            message_type='text'
                        )
        
        # Proje teklifleri oluştur
        offers_data = [
            {
                'title': 'E-ticaret Web Sitesi',
                'description': 'Modern bir e-ticaret sitesi yapabilir misiniz? WordPress veya özel kod fark etmez.',
                'budget': Decimal('15000.00'),
                'deadline_days': 30,
                'status': 'pending',
            },
            {
                'title': 'Mobil Uygulama Geliştirme',
                'description': 'iOS ve Android için fitness uygulaması geliştirmek istiyorum.',
                'budget': Decimal('25000.00'),
                'deadline_days': 60,
                'status': 'pending',
            },
        ]
        
        for offer_data in offers_data:
            # Rastgele bir freelancer ve client seç
            if freelancers.exists() and clients.exists():
                freelancer = random.choice(freelancers)
                client = random.choice(clients)
                
                # Chat room oluştur
                chat_room = ChatRoom.objects.create(
                    name=f"Teklif: {offer_data['title']}",
                )
                chat_room.participants.add(freelancer, client)
                
                # Teklif mesajı oluştur
                offer_message = Message.objects.create(
                    room=chat_room,
                    sender=client,
                    content=f"Proje Teklifi: {offer_data['description']}",
                    message_type='offer'
                )
                
                # Deadline hesapla
                from datetime import date, timedelta
                deadline = date.today() + timedelta(days=offer_data['deadline_days'])
                
                ProjectOffer.objects.create(
                    sender=client,
                    receiver=freelancer,
                    chat_room=chat_room,
                    message=offer_message,
                    title=offer_data['title'],
                    description=offer_data['description'],
                    budget=offer_data['budget'],
                    deadline=deadline,
                    status=offer_data['status'],
                )
                self.stdout.write(f'Proje teklifi oluşturuldu: {offer_data["title"]}')
        
        # Kullanıcı talepleri oluştur
        request_data = [
            {
                'full_name': 'Ali Veli',
                'email': 'ali.veli@test.com',
                'subject': 'Website Yenileme',
                'message': 'Mevcut websitemi yenilemek istiyorum. Modern bir tasarım gerekiyor. Bütçem 5000-10000 TL arası, 3 hafta içinde teslim alabilir miyiz?',
            },
            {
                'full_name': 'Selin Yurt',
                'email': 'selin.yurt@test.com',
                'subject': 'Logo Tasarımı',
                'message': 'Yeni şirketim için profesyonel logo tasarımı yaptırmak istiyorum. Bütçem 1000-2000 TL, 1 hafta içinde teslim alabilir miyiz?',
            },
        ]
        
        for req_data in request_data:
            UserRequest.objects.get_or_create(
                email=req_data['email'],
                defaults=req_data
            )
            self.stdout.write(f'Kullanıcı talebi oluşturuldu: {req_data["subject"]}')
        
        self.stdout.write(
            self.style.SUCCESS('Test verileri başarıyla oluşturuldu!')
        )
        self.stdout.write('Test kullanıcı giriş bilgileri:')
        self.stdout.write('Email: ahmet.yilmaz@test.com | Şifre: test123456 (Freelancer)')
        self.stdout.write('Email: zeynep.kaya@test.com | Şifre: test123456 (Freelancer)')
        self.stdout.write('Email: ayse.ozkan@test.com | Şifre: test123456 (Müşteri)')
