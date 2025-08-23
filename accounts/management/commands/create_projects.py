from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.models import FreelancerProfile
from apps.careers.models import FreelancerProject, ProjectCategory
from decimal import Decimal
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Örnek projeler oluşturur'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Örnek projeler oluşturuluyor...'))
        
        # Kategoriler oluştur/al
        categories = {}
        category_data = [
            ('Web Geliştirme', 'Web sitesi ve web uygulaması geliştirme', 'fas fa-code'),
            ('Mobil Uygulama', 'iOS ve Android uygulama geliştirme', 'fas fa-mobile-alt'),
            ('Grafik Tasarım', 'Logo, poster, web tasarımı', 'fas fa-paint-brush'),
            ('Yazılım Geliştirme', 'Masaüstü yazılım ve sistem geliştirme', 'fas fa-laptop-code'),
            ('Dijital Pazarlama', 'SEO, sosyal medya, reklam yönetimi', 'fas fa-chart-line'),
            ('İçerik Yazımı', 'Blog, makale, metin yazımı', 'fas fa-pen'),
        ]
        
        for name, desc, icon in category_data:
            category, created = ProjectCategory.objects.get_or_create(
                name=name,
                defaults={'description': desc, 'icon': icon}
            )
            categories[name] = category
            if created:
                self.stdout.write(f'Kategori oluşturuldu: {name}')
        
        # Freelancerları al
        freelancers = User.objects.filter(user_type='freelancer')
        
        if not freelancers.exists():
            self.stdout.write(self.style.ERROR('Hiç freelancer bulunamadı. Önce test verilerini oluşturun.'))
            return
        
        # Örnek projeler
        projects_data = [
            {
                'title': 'Modern E-ticaret Web Sitesi',
                'description': '''React ve Node.js kullanarak modern bir e-ticaret platformu geliştirdim. 
                
Özellikler:
• Responsive tasarım
• Ödeme sistemi entegrasyonu  
• Admin paneli
• Ürün yönetimi
• Sipariş takibi
• SEO optimizasyonu

Teknolojiler: React, Node.js, MongoDB, Stripe API, Bootstrap''',
                'category': 'Web Geliştirme',
                'technologies': 'React, Node.js, MongoDB, Express, Stripe, Bootstrap',
                'requirements': 'Modern tarayıcı desteği, mobil uyumluluk, hızlı yükleme',
                'deliverables': 'Kaynak kodlar, dokumentasyon, kurulum rehberi, 3 aylık destek',
                'estimated_duration': '6-8 hafta',
                'budget_range': '10000_25000',
                'demo_url': 'https://demo-ecommerce.vercel.app',
                'github_url': 'https://github.com/freelancer/ecommerce-project',
                'status': 'completed',
                'is_featured': True,
            },
            {
                'title': 'iOS Fitness Tracking Uygulaması',
                'description': '''SwiftUI kullanarak geliştirilmiş kapsamlı fitness takip uygulaması.

Özellikler:
• Antrenman planları
• Kalori takibi
• İlerleme grafikleri
• Sosyal paylaşım
• Apple Health entegrasyonu
• Push notifications

Apple Store'da yayınlandı ve 4.8 puan aldı.''',
                'category': 'Mobil Uygulama',
                'technologies': 'Swift, SwiftUI, Core Data, HealthKit, CloudKit',
                'requirements': 'iOS 14+, iPhone 8 ve üzeri',
                'deliverables': 'App Store yayını, kaynak kod, kullanım kılavuzu',
                'estimated_duration': '10-12 hafta',
                'budget_range': '25000_50000',
                'demo_url': 'https://apps.apple.com/tr/app/fitness-tracker',
                'status': 'completed',
                'is_featured': True,
            },
            {
                'title': 'Kurumsal Logo ve Kimlik Tasarımı',
                'description': '''Teknoloji şirketi için eksiksiz kurumsal kimlik paketi tasarladım.

İçerik:
• Ana logo ve varyasyonları
• Kartvizit tasarımı
• Antetli kağıt
• E-imza şablonu
• Sosyal medya görselleri
• Marka kullanım kılavuzu

Modern, minimal ve profesyonel bir görünüm.''',
                'category': 'Grafik Tasarım',
                'technologies': 'Adobe Illustrator, Photoshop, InDesign, Figma',
                'requirements': 'Vektör formatlar, yüksek çözünürlük',
                'deliverables': 'Logo dosyaları (AI, EPS, PNG, SVG), brand guide, mockup görseller',
                'estimated_duration': '2-3 hafta',
                'budget_range': '5000_10000',
                'status': 'completed',
                'is_featured': False,
            },
            {
                'title': 'Django Blog Platformu',
                'description': '''Django framework kullanarak geliştirilmiş çok kullanıcılı blog platformu.

Özellikler:
• Kullanıcı kayıt/giriş sistemi
• WYSIWYG editör
• Kategori ve etiket sistemi
• Yorum sistemi
• SEO dostu URL'ler
• Admin paneli
• Email bildirimleri

PostgreSQL veritabanı, Redis cache kullanımı.''',
                'category': 'Web Geliştirme',
                'technologies': 'Django, PostgreSQL, Redis, Bootstrap, CKEditor',
                'requirements': 'Python 3.8+, PostgreSQL, Redis',
                'deliverables': 'Kaynak kod, veritabanı, deployment guide, admin eğitimi',
                'estimated_duration': '4-5 hafta',
                'budget_range': '5000_10000',
                'github_url': 'https://github.com/freelancer/django-blog',
                'status': 'published',
                'is_featured': False,
            },
            {
                'title': 'React Native Rezervasyon Uygulaması',
                'description': '''Restoran rezervasyon sistemi için cross-platform mobil uygulama.

Özellikler:
• Restoran arama ve filtreleme
• Masa rezervasyonu
• Menü görüntüleme
• Puanlama ve yorum
• Push notifications
• Harita entegrasyonu
• Ödeme sistemi

Hem iOS hem Android için geliştirildi.''',
                'category': 'Mobil Uygulama',
                'technologies': 'React Native, Firebase, Google Maps API, Stripe',
                'requirements': 'iOS 12+, Android 7+',
                'deliverables': 'APK/IPA dosyaları, kaynak kod, Firebase config',
                'estimated_duration': '8-10 hafta',
                'budget_range': '10000_25000',
                'status': 'published',
                'is_featured': True,
            },
            {
                'title': 'Python Veri Analizi Scripti',
                'description': '''E-ticaret verilerini analiz eden Python scriptleri paketi.

Özellikler:
• Satış trendleri analizi
• Müşteri segmentasyonu
• Ürün performans raporları
• Tahminleme modelleri
• Görselleştirme grafikleri
• Otomatik rapor oluşturma

Pandas, NumPy, Matplotlib kullanımı.''',
                'category': 'Yazılım Geliştirme',
                'technologies': 'Python, Pandas, NumPy, Matplotlib, Seaborn, Jupyter',
                'requirements': 'Python 3.8+, CSV/Excel veri dosyaları',
                'deliverables': 'Python scriptleri, Jupyter notebook, sample data, dokumentasyon',
                'estimated_duration': '2-3 hafta',
                'budget_range': '1000_5000',
                'github_url': 'https://github.com/freelancer/data-analysis',
                'status': 'completed',
                'is_featured': False,
            },
            {
                'title': 'WordPress E-ticaret Teması',
                'description': '''WooCommerce uyumlu, özelleştirilebilir e-ticaret teması.

Özellikler:
• Responsive tasarım
• WooCommerce tam desteği
• Ürün showcase
• Blog sayfaları
• Contact formları
• SEO optimizasyonu
• Customizer ayarları

ThemeForest'te satışa sunuldu.''',
                'category': 'Web Geliştirme',
                'technologies': 'WordPress, WooCommerce, PHP, SCSS, JavaScript',
                'requirements': 'WordPress 5.0+, WooCommerce 4.0+',
                'deliverables': 'Tema dosyaları, child theme, dokumentasyon, demo content',
                'estimated_duration': '6-7 hafta',
                'budget_range': '10000_25000',
                'demo_url': 'https://demo.themeforest.net/ecommerce-theme',
                'status': 'published',
                'is_featured': True,
            },
            {
                'title': 'Sosyal Medya Tasarım Paketi',
                'description': '''Instagram ve Facebook için hazır tasarım şablonları paketi.

İçerik:
• 50 adet Instagram post şablonu
• 20 adet story şablonu
• Facebook cover tasarımları
• Highlight ikonları
• Animasyonlu templateler
• PSD kaynak dosyaları

Moda, lifestyle ve business kategorileri.''',
                'category': 'Grafik Tasarım',
                'technologies': 'Photoshop, Illustrator, After Effects, Canva',
                'requirements': 'Adobe Creative Suite, Canva Pro',
                'deliverables': 'PSD dosyaları, PNG exportlar, Canva templateler, kullanım rehberi',
                'estimated_duration': '3-4 hafta',
                'budget_range': '5000_10000',
                'status': 'completed',
                'is_featured': False,
            },
        ]
        
        # Her freelancer için rastgele projeler oluştur
        for freelancer in freelancers:
            try:
                freelancer_profile = FreelancerProfile.objects.get(user=freelancer)
            except FreelancerProfile.DoesNotExist:
                self.stdout.write(f'Freelancer profile bulunamadı: {freelancer.get_full_name()}')
                continue
            
            # Her freelancer için 2-4 proje oluştur
            project_count = random.randint(2, 4)
            selected_projects = random.sample(projects_data, min(project_count, len(projects_data)))
            
            for project_data in selected_projects:
                # Proje başlığını freelancer'a göre özelleştir
                title = f"{project_data['title']} - {freelancer.first_name} Edition"
                
                category = categories.get(project_data['category'])
                
                # Proje oluştur
                project, created = FreelancerProject.objects.get_or_create(
                    title=title,
                    defaults={
                        'freelancer': freelancer_profile,  # Bu accounts.FreelancerProfile'ı kullanacak
                        'category': category,
                        'description': project_data['description'],
                        'technologies': project_data['technologies'],
                        'requirements': project_data['requirements'],
                        'deliverables': project_data['deliverables'],
                        'estimated_duration': project_data['estimated_duration'],
                        'budget_range': project_data['budget_range'],
                        'demo_url': project_data.get('demo_url', ''),
                        'github_url': project_data.get('github_url', ''),
                        'status': project_data['status'],
                        'is_featured': project_data['is_featured'],
                        'views': random.randint(50, 500),
                        'offers_count': random.randint(0, 15),
                    }
                )
                
                if created:
                    self.stdout.write(f'Proje oluşturuldu: {title}')
        
        self.stdout.write(
            self.style.SUCCESS('Örnek projeler başarıyla oluşturuldu!')
        )
        self.stdout.write('Projeleri görmek için /kariyer/freelancerlar/ sayfasını ziyaret edin.')
