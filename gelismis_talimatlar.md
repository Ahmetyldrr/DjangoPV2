TALİMAT.md — PyQt5 .exe Uygulama Dağıtım Sitesi (Django)
1) Amaç ve Kapsam

Bu proje, geliştirilen PyQt5 tabanlı .exe uygulamaların kullanıcıya sunulması, kategorilere göre listelenmesi, sürüm (test/kararlı) indirmelerinin yönetilmesi ve kullanıcı taleplerinin toplanması için kurumsal bir Django web sitesidir.
Öncelikler: Güvenlik → Doğruluk → Basitlik → Performans.

Çıktı Standardı (LLM/Copilot için)
Yanıtlarını şu sırada ver:

Kısa özet

Dosya/dizin ağacı

Tam dosya içerikleri (doğru dizinlerde tek bloklar)

Çalıştırma komutları

Testler

Notlar ve sonraki adımlar

“Varsayım yapma, emin değilsen sor. Var olmayan dosya/bağımlılık üretme. Her kullanılan paketi requirements.txt’ye ekle.”

2) Hedef Kullanıcı Akışları (User Stories) & Kabul Kriterleri

US-001 | Uygulama Kataloğu
Bir ziyaretçi olarak, anasayfadan kategorileri ve öne çıkan uygulamaları görürüm.
Kabul: Anasayfada “Kategoriler”, “Popüler/En yeni” blokları, her kartta isim, kısa açıklama, rozet (test/kararlı), kategori etiketi.

US-002 | Kategoriye Göre Listeleme
Bir kullanıcı olarak, bir kategoriyi tıkladığımda sadece o kategoriye ait uygulamaları görürüm.
Kabul: /kategoriler/<slug>/ sayfasında paginasyon, sıralama (tarih/indirme), arama (isim/etiket).

US-003 | Uygulama Detayı & Sürüm İndirme
Bir kullanıcı olarak, uygulama detayında amaç/kapsam/gereksinimler, sürüm listesi (test/kararlı), değişiklik günlüğü, dosya boyutu, checksum görür ve indiririm.
Kabul: /uygulamalar/<slug>/ sayfasında sürüm tabloları; indirme linki, indirme sayacı ve checksum doğrulama yönergesi.

US-004 | Talep/Form
Bir kullanıcı olarak, “Talepler” bölümünden yeni özellik/uygulama/talep bırakırım.
Kabul: /talepler/yeni/ formu; başarı mesajı; yönetici e-postasına bildirim (opsiyonel).

US-005 | Hakkında & İletişim
Bir ziyaretçi olarak, “Hakkında” sayfasında siteyi tanıtan içerik, “İletişim” bölümünde WhatsApp, e-posta ve diğer kanalları bulurum.
Kabul: Navbar’da “Hakkında”, “Uygulamalarımız”, “Kategoriler”, “Talepler”, “İletişim” linkleri; WhatsApp tıklanabilir.

3) Teknoloji ve Standartlar

Django (5.x), Python 3.12

Veritabanı: Dev’de SQLite kabul; Prod’da PostgreSQL

Statik/Medya: Prod’da Nginx servis eder; .exe dosyaları MEDIA_ROOT altında

Önbellek: Redis (prod), locmem (dev)

Günlükleme: logging.dictConfig; INFO prod, DEBUG dev

Zaman Dilimi / Dil: Europe/Istanbul, tr

Güvenlik: SECURE_SSL_REDIRECT, CSRF_COOKIE_SECURE, SESSION_COOKIE_SECURE, HSTS prod’da açık

4) Bilgi Mimarisi & Sayfalar

/ (Anasayfa) — Öne çıkan uygulamalar, kategoriler, arama kutusu

/uygulamalar/ — Tüm uygulamalar listesi (+ filtre/sıralama/arama)

/uygulamalar/<slug>/ — Uygulama detayı + sürümler + checksum + indirme

/kategoriler/ — Kategori grid’i

/kategoriler/<slug>/ — Kategoriye ait uygulamalar listesi

/talepler/yeni/ — Talep/istek formu

/hakkinda/ — Kurumsal tanıtım

/iletisim/ — WhatsApp, e-posta, diğer bilgiler

/indirme/<release_id>/ — Yetkilendirilmiş indirme uç noktası (Nginx korumalı)

/sitemap.xml, /robots.txt

Navbar (Profesyonel)
Logo | Uygulamalarımız | Kategoriler | Talepler | Hakkında | İletişim | (Arama)

5) Dizin Yapısı (Hedef)
project_root/
  manage.py
  pyproject.toml
  requirements.txt
  .env.example
  compose.yml
  docker/
    web/Dockerfile
    nginx/nginx.conf
  config/
    settings/
      __init__.py
      base.py
      dev.py
      prod.py
    urls.py
    wsgi.py
    asgi.py
  apps/
    catalog/          # Uygulamalar & Kategoriler
    releases/         # Sürümler, indirme, checksum, sayaç
    requestsapp/      # Talepler/taleplerin yönetimi
    pages/            # Hakkında, İletişim, Anasayfa
  templates/
    base.html
  static/
  media/              # .exe dosyaları (prod: Nginx korumalı)
  tests/

6) Veri Modeli (Önerilen)

catalog.models

Category(name, slug, description, is_active)

Application(title, slug, short_description, description, category->Category, tags, is_active, created_at)

description: “Proje amaç, kapsam, gereklilikler” için rich-text/Markdown destekli alan

thumbnail (opsiyonel)

releases.models

Release(application->Application, version, channel [test|stable], file (FileField), file_size, sha256, changelog, is_active, published_at, download_count)

DownloadLog(release->Release, ip, user_agent, created_at)

Indirme uç noktası download_count’ı artırmalı ve loglamalı.

requestsapp.models

UserRequest(full_name, email, subject, message, attachment (ops), status [new|in_progress|closed], created_at)

pages

Statik sayfalar: Hakkında, İletişim içerikleri için basit view/template.

7) Görünümler (Views) & URL’ler

catalog

Listeler: ApplicationListView (tüm + arama/filtre/sıralama), CategoryListView, CategoryDetailView

Detay: ApplicationDetailView (slug)

releases

ReleaseDownloadView → Nginx X-Accel-Redirect / imzalı URL / zaman kısıtlı token ile dosya sunumu

checksum/changelog detaylarının şablona geçirilmesi

requestsapp

UserRequestCreateView (Form + başarı sayfası)

pages

HomeView, AboutView, ContactView

URL Düzeni

/uygulamalar/                -> ApplicationList
/uygulamalar/<slug>/         -> ApplicationDetail
/kategoriler/                -> CategoryList
/kategoriler/<slug>/         -> CategoryDetail
/talepler/yeni/              -> UserRequestCreate
/indirme/<release_id>/       -> ReleaseDownload
/hakkinda/                   -> About
/iletisim/                   -> Contact

8) Şablonlar (Templates) & Navbar

base.html: responsive navbar (Bootstrap/Tailwind), footer (telif, KVKK/Gizlilik)

Listeler: kart grid, rozetler (TEST/KARARLI), paginasyon

Detay:

Uygulama: Amaç/Kapsam/Gereklilikler (markdown render)

Sürüm listesi: version, channel, tarih, boyut, SHA256, “İndir” butonu

“Sorun bildir / Talep ilet” butonu (form sayfasına)

“Hakkında” ve “İletişim” sayfaları: WhatsApp tıkla-ara bağlantısı, sosyal linkler

9) İndirme Güvenliği ve Dosya Sunumu

.exe dosyaları MEDIA_ROOT altında, doğrudan public URL ile servis ETME.

Prod’da Nginx ile:

İndirme endpoint’i Django’da yetkilendirme + log → response header ile X-Accel-Redirect (internal location)

Linkler zaman kısıtlı token içerir (örn. itsdangerous veya imzalı URL)

Checksum (SHA256) zorunlu; sayfada kopyalanabilir biçimde göster.

(Opsiyonel) Virüs tarama iş akışı veya CI’da imza kontrolü.

10) Yönetim Paneli ve İçerik Yönetimi

Django Admin: Category/Application/Release/UserRequest için listeler, arama, filtre

Release ekleme sırasında:

file_size otomatik hesapla

sha256 otomatik üret

channel seçimi (test/kararlı)

published_at otomatik

“Öne çıkan” ve “Popüler” uygulamalar için boolean/hesaplanmış alanlar

11) Arama, Filtre, Sıralama

Arama: uygulama adı, kısa açıklama, etiketler

Filtre: kategori, kanal (test/kararlı)

Sıralama: en yeni, en çok indirilen, alfabetik

Uygulama listelerinde paginasyon (örn. 12/24/48)

12) İletişim/WhatsApp ve Talep Toplama

/iletisim/: WhatsApp (tıkla-yaz), e-posta, diğer kanallar

/talepler/yeni/: Ad, e-posta, konu, ayrıntı; reCAPTCHA (opsiyonel), KVKK onay kutusu

Gönderim sonrası teşekkür mesajı; (opsiyonel) yöneticilere e-posta

13) SEO, Erişilebilirlik, i18n

Başlık/description meta etiketleri, Open Graph

Her img için alt metin, ARIA etiketleri

Site haritası ve robots dosyası

Çok dilliliğe hazır yapı (TR temel; EN opsiyonel)

14) Günlükleme, İzleme, Hata Sayfaları

logging yapılandırması: konsol + dosya (prod)

404/500 özel şablonlar (templates/404.html, 500.html)

(Opsiyonel) Sentry entegrasyonu (SENTRY_DSN)

15) Dağıtım (Docker + Nginx + Gunicorn)

Docker Compose servisleri: web (Gunicorn), db (Postgres), nginx, (ops.) redis

Sağlık kontrolü: /healthz basit view

Yayın akışı: migrate → collectstatic → yeniden başlatma

Ortam değişkenleri: .env.example sağlayın (sırlar yok)

16) Geliştirme Komutları
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 0.0.0.0:8000


Docker:

docker compose up --build -d
docker compose logs -f web

17) Gereksinimler ve Paketler

requirements.txt (örnek)

Django>=5.0,<6.0
psycopg2-binary
python-dotenv
django-filter
django-crispy-forms
markdown
whitenoise
gunicorn


(İhtiyaca göre: django-storages, redis, celery, itsdangerous/imzalı URL)

18) Test ve Kalite

pytest + pytest-django; kapsama ≥ %80

ruff + black; isort sırası

(Ops.) mypy tip kontrol

CI: Lint + Test geçmeden merge yok

19) Güvenlik Politikaları

.exe indirirken imzalı link ve log zorunlu

CSRF tüm formlarda açık

SECURE_*` bayrakları prod’da aktif

API anahtarı/sır asla repo’da değil; ENV den okunur

Kullanıcı verileri için KVKK/Gizlilik metni

20) Definition of Done (DoD) — Kontrol Listesi

 Anasayfa, Kategori, Uygulama listesi & detay, İndirme, Talep formu, Hakkında & İletişim çalışıyor

 .exe indirmeleri Nginx internal + imzalı link ile servis ediliyor, indirme sayacı artıyor

 Sürüm tablolarında version/channel/tarih/size/SHA256/changelog görünüyor

 Admin’den içerik ve sürümler yönetilebiliyor

 Arama/filtre/sıralama çalışıyor; paginasyon var

 pytest geçiyor; kapsama ≥ %80

 ruff ve black temiz

 .env.example mevcut; sır yok

 Docker Compose ile web, db, nginx ayağa kalkıyor

21) Copilot/LLM’ye Örnek İstek (Prompt)

“Yukarıdaki TALİMAT.md’ye uygun olarak proje iskeletini ve aşağıdaki bileşenleri üret:

catalog app: Category, Application modelleri; list/detay view’lar; URL’ler; şablonlar.

releases app: Release, DownloadLog; indirme endpoint’i (Nginx X-Accel-Redirect ile iç yol); checksum otomasyonu; admin kayıtları.

requestsapp app: UserRequest modeli; ‘talep’ formu; başarı sayfası; admin.

Navbar içeren base.html; Anasayfa, Hakkında, İletişim sayfaları.

requirements.txt, config/settings/base|dev|prod.py, urls.py, docker/nginx.conf, compose.yml.

Pytest testleri: modeller, view list/detay, indirme sayaç artışı ve log.
Çıktıyı: 1) Dizin ağacı 2) Tam dosyalar 3) Komutlar 4) Testler şeklinde ver.”

22) Gelecek Geliştirmeler (Opsiyonel)

Kullanıcı hesapları ve lisanslama/erişim seviyesi

Sürüm “kararlıya yükselt” akışı, indirme kotası

İstatistik panosu (en çok indirilenler, kanala göre dağılım)

CDN/Objekt depolama (S3, GCS)

Otomatik antivirüs taraması (CI/CD entegrasyonlu)