# FamSecur Web

**Müdahale etmeden, Aileni koru.**

FamSecur'un tanıtım sitesi, ebeveyn paneli ve yönetim paneli. Proje aynı zamanda
*Web Tabanlı Teknolojiler* dersi dönem sonu projesidir: birbirinden ayrı bir
REST API (Django REST Framework) ve bu API'yi kullanan bir web istemcisinden
(React) oluşur.

FamSecur, ev ağında DNS/router seviyesinde çalışan, gizlilik odaklı bir aile
internet kalkanıdır. Kumar/bahis, yetişkin içerik, uyuşturucu, oltalama ve
zararlı yazılım alan adlarını engeller; çocuğun mesajlarını, ekranını veya
gezinme geçmişini toplamaz. Karar motoru ana proje deposundan
([isaergisi/FamSecur](https://github.com/isaergisi/FamSecur)) bu API'ye
uyarlanmıştır.

## Çözülen problem

Ebeveyn kontrol uygulamalarının çoğu çocuğun cihazına kurulur ve mesajlar,
ekran ve geçmiş gibi kişisel verileri toplar. FamSecur yalnızca istenen alan
adına bakar, yalnızca **engellenen** istekleri kaydeder ve her engelin nedenini
açıklar. Bu site ebeveynin:

- hesap açıp ailesinin cihazlarını tanımlamasını,
- koruma politikasını (risk eşiği, sessiz/uyarılı engel, kategoriler) belirlemesini,
- yanlış engelleri beyaz listeyle düzeltmesini,
- engel olaylarını gerekçeleriyle incelemesini,
- bir alan adının cihazında engellenip engellenmeyeceğini test etmesini

sağlar. Yöneticiler ise kullanıcıları, iletişim taleplerini, SSS içeriğini ve
tüm ailelerde geçerli tehdit istihbaratı kaynaklarını yönetir.

## Ödev şartlarının karşılanması

| Şart | Karşılandığı yer |
| --- | --- |
| Backend REST API | `backend/` — Django 5 + Django REST Framework |
| CRUD işlemleri | Cihaz, beyaz liste, SSS, iletişim talebi, tehdit kaynağı, kullanıcı (yönetici) için tam CRUD; politika ve aile için okuma/güncelleme; olaylar için okuma/silme |
| Veritabanı, kalıcı veri | SQLite (Django ORM, migration'lar `*/migrations/`) |
| HTTP metotları | `GET`, `POST`, `PUT`, `PATCH`, `DELETE` |
| HTTP durum kodları | 200, 201, 204, 400, 401, 403, 404, 405, 409, 429 |
| Anlamlı hata mesajları | Tüm hatalar `{"detail": "...", "errors": {alan: [mesaj]}}` biçiminde Türkçe döner (`config/exceptions.py`) |
| İş kuralları backend'de | Karar motoru, aile bazlı veri izolasyonu, politika kuralları, olay saklama süresi (`shield/services.py`, `shield/serializers.py`) |
| Kayıt ve giriş | `POST /api/auth/register/`, `POST /api/auth/login/` |
| Kimlik doğrulama ve yetkilendirme | JWT (access + refresh), rol bazlı yetki: `parent` / `admin` (`accounts/permissions.py`) |
| Frontend ayrı uygulama | `frontend/` — React 19 + Vite + React Router |
| Frontend okuma/ekleme/güncelleme/silme | Ebeveyn ve yönetim panelindeki tüm sayfalar |
| Hata ve başarı durumlarını gösterme | Alan bazlı form hataları, uyarı kutuları, bildirim (toast) mesajları |
| Oturum yönetimi | Anahtarlar `localStorage`'da; süresi dolan erişim anahtarı otomatik yenilenir, yenilenemezse oturum kapatılır (`src/api.js`) |
| En az 5 veri modeli | 9 model (aşağıda) |
| Basit CRUD'dan öte | Açıklanabilir risk puanlamalı alan adı karar motoru, 36.000+ resmî kumar alan adı havuzu, kendi eğittiğimiz yapay zeka risk modeli (%93 test doğruluğu) |
| Testler | 20 API testi (`backend/tests/test_api.py`) |

## Veri modelleri

| Model | Uygulama | Açıklama |
| --- | --- | --- |
| `User` | accounts | E-posta ile giriş yapan kullanıcı; `parent` veya `admin` rolü |
| `Family` | shield | Ebeveynin koruduğu ev (kullanıcıyla bire bir) |
| `Policy` | shield | Risk eşiği, engel biçimi, etkin kategoriler, olay saklama süresi |
| `Device` | shield | Ailenin cihazları; cihaz bazında koruma açılıp kapatılabilir |
| `WhitelistEntry` | shield | Ailenin izin verdiği alan adları (alt alan adları dahil) |
| `BlockEvent` | shield | Yalnızca engellenen istekler: alan adı, kategori, puan, gerekçe |
| `ThreatSource` | shield | Yöneticinin yönettiği tehdit istihbaratı kaynağı ve alan adları |
| `FAQ` | content | Sitedeki sıkça sorulan sorular |
| `ContactRequest` | content | Ziyaretçilerin demo/destek talepleri |

```mermaid
erDiagram
    User ||--o| Family : sahip
    Family ||--|| Policy : uygular
    Family ||--o{ Device : içerir
    Family ||--o{ WhitelistEntry : izin verir
    Family ||--o{ BlockEvent : kaydeder
    Device |o--o{ BlockEvent : kaynağı
```

## İş kuralları

- Her ebeveyn yalnızca kendi ailesinin verisini görebilir; başka ailenin kaydı `404` döner.
- Kayıt olan her kullanıcıya otomatik olarak bir aile ve varsayılan politika (eşik 70, sessiz engel, tüm kategoriler) oluşturulur.
- Risk eşiği 30-100 arasında olmalıdır; oltalama ve zararlı yazılım kategorileri kapatılamaz.
- `POST /api/check/` alan adını şu sırayla değerlendirir: cihaz koruması → beyaz liste → aktif tehdit kaynakları → resmî kumar havuzu → açıklanabilir sinyal puanlaması. Alan adı hiçbir listede yoksa yanıta ayrıca yapay zeka risk tahmini (`ai`) eklenir; bu tahmin kararı değiştirmez.
- İzin verilen istekler **hiçbir yerde kaydedilmez**; engellenenler `BlockEvent` olarak yazılır, saklama süresi dolanlar silinir.
- Olaylar elle oluşturulamaz (`POST /api/events/` → `405`); yalnızca karar motoru üretir.
- Aynı ailede aynı adlı iki cihaz veya aynı alan adı iki kez beyaz listede olamaz.
- Yönetici kendi hesabını silemez, rolünü düşüremez veya kapatamaz.
- Herkese açık uç noktalar hız sınırlıdır (demo analizi 30/dk, iletişim formu 5/saat).

## API uç noktaları

| Metot | Yol | Yetki | Açıklama |
| --- | --- | --- | --- |
| POST | `/api/auth/register/` | Herkes | Kayıt; kullanıcı + JWT döner |
| POST | `/api/auth/login/` | Herkes | Giriş; JWT döner |
| POST | `/api/auth/refresh/` | Herkes | Erişim anahtarını yeniler |
| GET, PATCH | `/api/auth/me/` | Giriş | Profil |
| POST | `/api/auth/change-password/` | Giriş | Şifre değiştirme |
| GET, PATCH | `/api/family/` | Ebeveyn | Aile bilgisi ve özet |
| GET, PUT, PATCH | `/api/policy/` | Ebeveyn | Koruma politikası |
| GET, POST, PUT, PATCH, DELETE | `/api/devices/` | Ebeveyn | Cihazlar |
| GET, POST, PUT, PATCH, DELETE | `/api/whitelist/` | Ebeveyn | Beyaz liste (`?search=`) |
| GET, DELETE | `/api/events/` | Ebeveyn | Engel olayları (`?category=&device=&search=&page=`) |
| GET | `/api/events/stats/` | Ebeveyn | Kategori, cihaz, gün bazlı istatistik |
| DELETE | `/api/events/clear/` | Ebeveyn | Tüm olayları siler |
| POST | `/api/check/` | Ebeveyn | Alan adını aile politikasıyla değerlendirir |
| POST | `/api/analyze/` | Herkes | Sitedeki canlı demo (kayıt tutmaz) |
| GET / POST, PUT, PATCH, DELETE | `/api/faqs/` | Herkes / Yönetici | SSS |
| POST / GET, PUT, PATCH, DELETE | `/api/contact-requests/` | Herkes / Yönetici | İletişim talepleri |
| GET / POST, PUT, PATCH, DELETE | `/api/threat-sources/` | Herkes / Yönetici | Tehdit kaynakları |
| GET, POST, PUT, PATCH, DELETE | `/api/admin/users/` | Yönetici | Kullanıcı yönetimi |
| GET | `/api/admin/stats/` | Yönetici | Platform istatistikleri |

## Yapay zeka risk modeli

Listeler ne kadar büyük olursa olsun her gün yeni kumar ve yetişkin içerik
siteleri açılıyor. Bu yüzden FamSecur'a, **hiçbir listede olmayan** bir alan
adının adına bakarak ne kadar riskli göründüğünü tahmin eden küçük bir makine
öğrenmesi modeli eklendi. Model ücretsizdir, tamamen yerelde (kendi
bilgisayarımızda) eğitilir ve çalışır; dışarıya hiçbir veri gönderilmez.

Ebeveyn panelindeki **Alan adı test et** sayfasında sonuç kartının altında
"Yapay zeka risk tahmini: %NN" olarak görünür. Tahmin %60 ve üzerindeyse
ebeveyne uyarı gösterilir. Model **engellemez**, yalnızca uyarır: kesin engel
kararını açıklanabilir karar motoru ve listeler verir. Böylece modelin olası
yanlışları çocuğun masum bir siteye girmesini engellemez.

### Nasıl çalışıyor?

1. **Veri.** Riskli örnekler: resmî kumar alan adı havuzu (Polonya Maliye
   Bakanlığı), The Block List Project kumar ve yetişkin içerik listeleri. Temiz
   örnekler: Cisco Umbrella'nın dünyada en çok sorgulanan 1 milyon alan adı ve
   Google Chrome'un (CrUX) **Türkiye'de en çok ziyaret edilen ≈470.000 sitesi**.
2. **Temizleme.** Her alan adı kayıtlı alan adına indirilir
   (`www.m.ornek.com` → `ornek.com`). Riskli listelerde geçen hiçbir alan adı
   "temiz" sayılmaz. `tumblr.com` gibi binlerce kullanıcı sayfası barındıran
   platformlar iki taraftan da çıkarılır.
3. **Türkçe riskli örnekler (zayıf etiketleme).** Kara listeler çoğunlukla
   yabancı sitelerden oluşur. Türkiye'de popüler siteler arasında ise henüz
   hiçbir listeye girmemiş yasa dışı bahis ve yetişkin siteleri var. Kural
   tabanlı karar motorumuzun adından açıkça engellediği bu ≈24.000 site temiz
   kümeden çıkarılır ve riskli örnek olarak eklenir. Model böylece
   `canlibahis`, `yenibahisadresi` gibi Türkçe adları öğrenir, ama kurala
   birebir bağlı kalmaz: kuralın bilmediği benzer adları da tanıyabilir.
4. **Örneklem.** 100.000 kumar, 100.000 yetişkin ve ≈520.000 temiz alan adı
   (toplam ≈720.000). Sınıflar eşit sayıda değil; bunu
   `class_weight="balanced"` ile dengeliyoruz (az örnekli sınıfın hatası daha
   "pahalı" sayılır).
5. **Ayrım.** Verinin %80'i eğitime, %20'si teste ayrılır. Test kümesini model
   eğitim sırasında hiç görmez (hold-out), bu yüzden ölçülen doğruluk modelin
   yeni alan adlarındaki başarısını gösterir.
6. **Özellikler.** Alan adı 2-5 harflik parçalara (karakter n-gram) bölünür:
   `bahis` → `ba`, `ah`, `bah`, `ahi`, … Bu parçalar *hashing* ile sabit
   boyutlu bir vektöre yerleştirilir ve **TF-IDF** ile ağırlıklandırılır
   (bir alan adında geçen ama genelde nadir olan parçalar daha önemli sayılır).
7. **Sınıflandırıcı.** Çok sınıflı **Lojistik Regresyon**: her alan adı için
   `clean` (temiz), `gambling` (kumar), `adult` (yetişkin) olasılıkları
   hesaplanır. Risk puanı = 1 − P(temiz).
8. **Kayıt.** Model `joblib` ile sıkıştırılarak
   `backend/ml/model/domain_risk.joblib` dosyasına (≈3 MB) kaydedilir;
   ölçümler `backend/ml/model/metrics.json` dosyasına yazılır.

### Sonuçlar (143.999 alan adlık test kümesi)

| Ölçüm | Değer |
| --- | --- |
| Doğruluk (temiz / kumar / yetişkin) | **%92,8** |
| Doğruluk (riskli / temiz) | **%93,0** |
| Riskli alan adlarını yakalama oranı | %90,5 |
| Temiz alan adlarını doğru bırakma oranı | %93,9 |
| Türkiye'de popüler temiz siteleri doğru bırakma oranı | %94,9 |
| ROC AUC (riskli / temiz) | 0,974 |

| Sınıf | Kesinlik (precision) | Duyarlılık (recall) |
| --- | --- | --- |
| Kumar | %92,7 | %94,0 |
| Yetişkin | %77,6 | %83,1 |
| Temiz | %96,1 | %94,5 |

### İlk model ile karşılaştırma

İlk model yalnızca Polonya kumar listesi, yetişkin listesi ve Umbrella ile
eğitilmişti. İki modeli **aynı test kümesinde** ölçtük:

| Ölçüm | İlk model | Yeni model |
| --- | --- | --- |
| Doğruluk (riskli / temiz) | %87,3 | **%93,0** |
| Riskli alan adlarını yakalama | %79,6 | **%90,5** |
| Temiz alan adlarını doğru bırakma | %90,2 | **%93,9** |
| Türkiye'de popüler temiz siteleri doğru bırakma | %86,2 | **%94,9** |
| 40 bilinen Türk sitesinde ortalama risk | %11,8 | **%4,0** |

Örnekler (risk tahmini, ilk → yeni): `sahibinden.com` %36 → %6,
`yemeksepeti.com` %55 → %2, `cumhuriyet.com.tr` %45 → %0,
`yenibahisadresi.net` %56 → %95, `canlimacizle-bahis.com` %81 → %92.

Not: İlk modelin daha önce ölçülen %92'lik doğruluğu kendi (daha kolay,
Türkçe örnek içermeyen) test kümesindeydi; burada iki model aynı ve daha zor
kümede yarışıyor. Test kümesindeki Türkçe riskli örneklerin etiketi kural
motorundan geldiği için bu dilimde ölçülen başarı biraz iyimser olabilir.

Model yalnızca alan adının harflerine bakar, sitenin içeriğini görmez. Bu
yüzden `better.com` gibi "bet" içeren masum adlarda veya `n11.com` gibi çok
kısa adlarda yanılabilir. Modeli engel yerine uyarı olarak
kullanmamızın nedeni budur.

### Modeli yeniden eğitmek

```bash
cd backend
pip install -r requirements.txt
python -m ml.train_risk_model --download   # verileri indirir (~85 MB) ve eğitir, ~2 dk
python manage.py test tests                # model testleri dahil
```

Ham veriler `backend/ml/data/` klasörüne iner ve git'e eklenmez. Eğitim
betiği sabit rastgelelik tohumu (`SEED = 42`) kullanır; aynı verilerle
çalıştırıldığında aynı sonucu verir. Model dosyası farklı bir scikit-learn
sürümüyle açılamazsa yukarıdaki komutla yeniden eğitmek yeterlidir; model
yüklenemezse site çalışmaya devam eder, yalnızca yapay zeka tahmini görünmez.

Dosyalar: `backend/ml/train_risk_model.py` (eğitim),
`backend/ml/features.py` (eğitim ve tahminde ortak ön işleme),
`backend/shield/ml_risk.py` (Django'da modeli yükleyip tahmin yapan yardımcı).

## Kurulum

Gereksinimler: Python 3.11+, Node.js 20+.

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo       # demo hesapları ve örnek veri
python manage.py runserver       # http://127.0.0.1:8000
```

Testler:

```bash
python manage.py test tests
```

### Frontend

```bash
cd frontend
npm install
npm run dev                      # http://localhost:5173
```

Geliştirmede Vite, `/api` isteklerini `http://127.0.0.1:8000` adresine yönlendirir.
API başka bir adresteyse `frontend/.env` dosyasında `VITE_API_URL` tanımlayın.

### Demo hesapları (`seed_demo` sonrası)

| Rol | E-posta | Şifre |
| --- | --- | --- |
| Yönetici | `admin@famsecur.com` | `Admin.12345` |
| Ebeveyn | `ebeveyn@famsecur.com` | `Ebeveyn.12345` |

### Üretim notları

`DJANGO_DEBUG=0`, `DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS` ve
`CORS_ALLOWED_ORIGINS` ortam değişkenlerini ayarlayın. Demo şifrelerini
kullanmayın.

## Proje yapısı

```
backend/
  config/      ayarlar, URL'ler, ortak hata biçimi
  accounts/    kullanıcı modeli, kayıt/giriş, rol izinleri, kullanıcı yönetimi
  shield/      aile, politika, cihaz, beyaz liste, olay, tehdit kaynağı, karar motoru
  content/     SSS, iletişim talepleri, seed_demo komutu
  ml/          yapay zeka risk modeli: eğitim betiği ve kayıtlı model
  tests/       API testleri
frontend/
  src/api.js            REST istemcisi (JWT, otomatik yenileme, hata yönetimi)
  src/auth.jsx          oturum durumu
  src/pages/public/     tanıtım sitesi, SSS, iletişim, giriş, kayıt
  src/pages/panel/      ebeveyn paneli
  src/pages/admin/      yönetim paneli
```
