1) Amaç

PyQt5 tabanlı .exe uygulamalarımı tanıtan ve kategoriye göre listeleme, uygulama detayı, sürüm (.exe) indirme, kullanıcı talep formu, “Hakkında” ve “İletişim (WhatsApp)” sayfaları bulunan basit bir Django sitesinin yerelde çalışır hâle getirilmesi.

Bu aşamada dosya indirme doğrudan Django üzerinden yapılacaktır (yalnızca geliştirme içindir). Üretimde Nginx/internal route gibi yöntemlere geçilecektir.

2) Çıktı Biçimi (LLM/Copilot yanıt standardı)

Yanıtlarını şu sırayla ver:

Kısa özet

Dizin ağacı

Tam dosya içerikleri (her dosya için doğru yol ve tek kod bloğu)

Çalıştırma komutları

Asgari testler (isteğe bağlı)

Sonraki adımlar (notlar)

Varsayım yapma; kullandığın paketi requirements.txt’ye ekle; ürettiğin her dosyanın yolunu açık yaz.

3) Teknolojiler ve Asgari Bağımlılıklar

Python 3.12

Django 5.x

SQLite (varsayılan)

Şablonlar için Bootstrap veya Tailwind (CDN kullanabilirsiniz)

Markdown (uygulama açıklaması için) — opsiyonel

requirements.txt (asgari)

Django>=5.0,<6.0
markdown

4) Dizin Yapısı (hedef)
project_root/
  manage.py
  requirements.txt
  .env.example               # (opsiyonel; basit aşamada gerekmez)
  config/
    __init__.py
    settings.py              # tek dosya (dev odaklı)
    urls.py
    wsgi.py
    asgi.py
  apps/
    catalog/                 # Kategoriler & Uygulamalar (listeler/detay)
      __init__.py
      admin.py
      apps.py
      models.py
      urls.py
      views.py
      forms.py               # (gerekirse)
      templates/
        catalog/
          application_list.html
          application_detail.html
          category_list.html
          category_detail.html
    releases/                # Sürümler (.exe), indirme, sayaç
      __init__.py
      admin.py
      apps.py
      models.py
      urls.py
      views.py
      templates/
        releases/
          release_table.html     # parçalı template
    requestsapp/              # Talep formu
      __init__.py
      admin.py
      apps.py
      models.py
      urls.py
      views.py
      forms.py
      templates/
        requestsapp/
          request_create.html
          request_success.html
    pages/                    # Anasayfa, Hakkında, İletişim
      __init__.py
      apps.py
      urls.py
      views.py
      templates/
        pages/
          home.html
          about.html
          contact.html
  templates/
    base.html                 # navbar/footer
  static/                     # css/js/img (geliştirme)
  media/                      # .exe dosyaları (geliştirme)

5) Modeller (asgari alanlarla)

apps/catalog/models.py

Category(name, slug, description, is_active=True)

Application( title, slug, short_description, description_markdown, category -> Category, tags (CharField, virgülle), is_active=True, created_at )

description_markdown: “amaç/kapsam/gereklilikler” içeriği

(ops.) thumbnail

apps/releases/models.py

Release( application -> Application, version, channel (choices: test|stable), file (FileField), file_size (BigInteger), sha256 (CharField), changelog_markdown, is_active=True, published_at, download_count (Integer) )

apps/requestsapp/models.py

UserRequest(full_name, email, subject, message, created_at)

Not: Bu aşamada file_size ve sha256 değerleri formda girilebilir veya basit sinyallerle hesaplanabilir (opsiyonel).

6) URL Tasarımı

Kök config/urls.py şu uygulamaları dahil etmelidir:

/                -> pages: HomeView
/hakkinda/       -> pages: AboutView
/iletisim/       -> pages: ContactView (WhatsApp link)
/uygulamalar/    -> catalog: ApplicationListView
/uygulamalar/<slug>/      -> catalog: ApplicationDetailView
/kategoriler/    -> catalog: CategoryListView
/kategoriler/<slug>/      -> catalog: CategoryDetailView
/talepler/yeni/  -> requestsapp: UserRequestCreateView
/talepler/basarili/ -> requestsapp: success
/indirme/<int:id>/ -> releases: ReleaseDownloadView (geliştirmede direkt FileResponse)

7) Görünümler (Views) — minimalist

catalog/views.py

ApplicationListView: arama (q), kategori filtresi (category), kanal filtresi (opsiyonel), paginasyon

ApplicationDetailView: uygulama + ilgili Release’leri tablo olarak include eder

CategoryListView: tüm kategoriler

CategoryDetailView: ilgili kategoriye ait uygulamalar (paginasyon)

releases/views.py

ReleaseDownloadView(id): İlgili Release.file için geliştirmede:

FileResponse(open(file_path,"rb")) ile servis et

release.download_count += 1 kaydet

Basit hata kontrolleri (aktif değilse 404)

requestsapp/views.py

UserRequestCreateView: full_name, email, subject, message alanları; başarıda /talepler/basarili/

pages/views.py

HomeView: öne çıkan uygulamalar (son eklenenler) + kategori grid

AboutView: statik içerik (site tanıtımı)

ContactView: WhatsApp linki (https://wa.me/<numara>) + mailto

8) Şablonlar (Templates)

templates/base.html

Üst navbar: Logo | Uygulamalarımız | Kategoriler | Talepler | Hakkında | İletişim | (Arama)

Mobil uyumlu (Bootstrap CDN veya Tailwind CDN)

catalog/

application_list.html: kart grid + arama + kategori filtresi

application_detail.html: başlık, kısa açıklama; amaç/kapsam/gereklilikler için Markdown render; “Sürümler” tablosunu {% include "releases/release_table.html" %} ile göster

category_list.html: kategori grid

category_detail.html: ilgili uygulama listesi

releases/

release_table.html: version | channel (TEST/KARARLI rozet) | tarih | boyut | SHA256 | İndir

requestsapp/

request_create.html: form + KVKK onay (metin olarak) — geliştirmede basit tutulabilir

request_success.html: teşekkür mesajı

pages/

home.html: son uygulamalar, kategori grid, yönlendirme butonları

about.html, contact.html: basit metinler (WhatsApp linki tıklanabilir)

9) Ayarlar (config/settings.py) — geliştirmeye uygun

DEBUG=True

LANGUAGE_CODE="tr"

TIME_ZONE="Europe/Istanbul"

INSTALLED_APPS: catalog, releases, requestsapp, pages

STATIC_URL="/static/", STATICFILES_DIRS=["BASE_DIR / 'static'"]

MEDIA_URL="/media/", MEDIA_ROOT=BASE_DIR / 'media'

TEMPLATES[0]["DIRS"]=["BASE_DIR / 'templates'"]

Geliştirmede dosya servis etmek için urlpatterns’a static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) ekle

10) Admin

Category, Application, Release, UserRequest admin kayıtları

Release admin formunda:

download_count read-only

(ops.) kayıt sırasında file_size otomatik hesap (basit Python ile)

11) Çalıştırma Komutları (yerel)
# Sanal ortam (opsiyonel ama önerilir)
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

pip install -r requirements.txt

# Django projesi (eğer yoksa)
django-admin startproject config .
python manage.py startapp catalog apps/catalog
python manage.py startapp releases apps/releases
python manage.py startapp requestsapp apps/requestsapp
python manage.py startapp pages apps/pages

python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser  # (opsiyonel)
python manage.py runserver 0.0.0.0:8000


Yerel test için media/ klasörüne küçük bir .exe veya örnek dosya koyup admin’den Release kaydı oluşturun.

12) Asgari Testler (isteğe bağlı ama önerilir)

apps/catalog/tests/test_views.py

ApplicationListView 200 döner, paginasyon çalışır

ApplicationDetailView doğru slug ile 200, yanlış slug ile 404

apps/releases/tests/test_download.py

ReleaseDownloadView indirme sayacını +1 arttırır

apps/requestsapp/tests/test_form.py

Talep formu valid → success template

Komut:

python manage.py test

13) Tanıtım İçerikleri (doldurulacak)

Hakkında: Kısa şirket/proje tanıtımı

İletişim: WhatsApp numarası, e-posta

Application.description_markdown: her uygulama için “amaç/kapsam/gereklilikler”

Release.changelog_markdown: değişiklikler; channel: test veya stable

14) Sınırlamalar (bu aşamada)

Dosya indirme doğrudan Django ile yapılır; sadece yerel geliştirme için uygundur.

Güvenlik, imzalı URL, kota/izin yönetimi, virüs taraması sonraki aşamaya bırakılmıştır.

15) Sonraki Adımlar (ileride)

Üretime hazırlık: Nginx + internal download route, imzalı URL

Docker Compose, Postgres, statik dosyalar için whitenoise/Nginx

Rol/izin, indirme istatistikleri, basit raporlar

Çok dillilik (EN)

Basit CI (lint+test)

16) Copilot/LLM’ye Örnek İstek

“Bu TALİMAT.md’ye göre:

catalog, releases, requestsapp, pages uygulamalarını oluştur.

Modelleri yukarıdaki alanlarla yaz, admin’e kaydet.

Görünümler ve URL’leri tanımla.

base.html navbar ve basit sayfa şablonlarını ekle.

ApplicationDetail sayfasında Release tablosunu include et.

Gerekli ayarları config/settings.py’ye ekle.

requirements.txt yaz.

Bana: 1) dizin ağacı 2) tam dosya içerikleri 3) çalıştırma komutları 4) (varsa) kısa testler şeklinde çıktı ver.”