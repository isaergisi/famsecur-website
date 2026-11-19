# FamSecur Web

**Müdahale etmeden aileni koru.**

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
| Backend REST API | `backend/` — Django 5.2/6 + Django REST Framework |
| CRUD işlemleri | Cihaz, beyaz liste, SSS, iletişim talebi, tehdit kaynağı, kullanıcı (yönetici) için tam CRUD; politika ve aile için okuma/güncelleme; olaylar için okuma/silme |
| Veritabanı, kalıcı veri | SQLite (Django ORM, migration'lar `*/migrations/`) |
| HTTP metotları | `GET`, `POST`, `PUT`, `PATCH`, `DELETE` |
| HTTP durum kodları | 200, 201, 204, 400, 401, 403, 404, 405, 409, 429, 502 |
| Anlamlı hata mesajları | Tüm hatalar `{"detail": "...", "errors": {alan: [mesaj]}}` biçiminde Türkçe döner (`config/exceptions.py`) |
| İş kuralları backend'de | Karar motoru, aile bazlı veri izolasyonu, politika kuralları, olay saklama süresi (`shield/services.py`, `shield/serializers.py`) |
| Kayıt ve giriş | `POST /api/auth/register/`, `POST /api/auth/login/` |
| Kimlik doğrulama ve yetkilendirme | JWT (access + refresh), rol bazlı yetki: `parent` / `admin` (`accounts/permissions.py`) |
| Frontend ayrı uygulama | `frontend/` — React 19 + Vite + React Router |
| Frontend okuma/ekleme/güncelleme/silme | Ebeveyn ve yönetim panelindeki tüm sayfalar |
| Hata ve başarı durumlarını gösterme | Alan bazlı form hataları, uyarı kutuları, bildirim (toast) mesajları |
| Oturum yönetimi | Anahtarlar `localStorage`'da; süresi dolan erişim anahtarı otomatik yenilenir, yenilenemezse oturum kapatılır (`src/api.js`) |
| En az 5 veri modeli | 9 model (aşağıda) |
| Basit CRUD'dan öte | Açıklanabilir risk puanlamalı alan adı karar motoru, 60.000+ alan adlık, kaynağından güncellenen resmî kumar havuzu, kendi eğittiğimiz yapay zekâ risk modeli (uyarı eşiğinde %92,6 test doğruluğu) |
| API dokümantasyonu | Swagger arayüzü `http://127.0.0.1:8000/api/docs/` (koddan otomatik üretilir, JWT ile denenebilir) |
| Testler | 28 API testi (`backend/tests/test_api.py`) |

## Veri modelleri

| Model | Uygulama | Açıklama |
| --- | --- | --- |
| `User` | accounts | E-posta ile giriş yapan kullanıcı; `parent` veya `admin` rolü |
| `Family` | shield | Ebeveynin koruduğu ev (kullanıcıyla bire bir) |
| `Policy` | shield | Risk eşiği, engel biçimi, etkin kategoriler, olay saklama süresi |
| `Device` | shield | Ailenin cihazları; cihaz bazında koruma açılıp kapatılabilir |
| `WhitelistEntry` | shield | Ailenin izin verdiği alan adları (alt alan adları dâhil) |
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
- `POST /api/check/` alan adını şu sırayla değerlendirir: cihaz koruması → beyaz liste → aktif tehdit kaynakları → resmî kumar havuzu → açıklanabilir sinyal puanlaması. Alan adı hiçbir listede yoksa yanıta ayrıca yapay zekâ risk tahmini (`ai`) eklenir; bu tahmin kararı değiştirmez.
- İzin verilen istekler **hiçbir yerde kaydedilmez**; engellenenler `BlockEvent` olarak yazılır, saklama süresi dolanlar silinir.
- Olaylar elle oluşturulamaz (`POST /api/events/` → `405`); yalnızca karar motoru üretir.
- Aynı ailede aynı adlı iki cihaz veya aynı alan adı iki kez beyaz listede olamaz.
- Yönetici kendi hesabını silemez, rolünü düşüremez veya kapatamaz.
- Herkese açık uç noktalar hız sınırlıdır (demo analizi 30/dk, iletişim formu 5/saat).

## API uç noktaları

Tüm uç noktaların Türkçe açıklamalı, tarayıcıdan denenebilir belgesi backend
çalışırken şu adreslerdedir:

| Adres | Ne işe yarar |
| --- | --- |
| `http://127.0.0.1:8000/api/docs/` | **Swagger**: uç noktaları listeler, *Try it out* ile doğrudan denenir |
| `http://127.0.0.1:8000/api/redoc/` | ReDoc: okunması kolay belge görünümü |
| `http://127.0.0.1:8000/api/schema/` | OpenAPI 3 şeması (Postman'e içe aktarılabilir) |

Kilitli uç noktaları denemek için: `POST /api/auth/login/` ile demo hesabıyla
giriş yapın, yanıttaki `access` değerini kopyalayıp sağ üstteki **Authorize**
düğmesine yapıştırın. Belge `drf-spectacular` ile koddan otomatik üretilir;
internet bağlantısı olmadan da açılır.


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
| GET, POST, PATCH, DELETE | `/api/admin/users/` | Yönetici | Kullanıcı yönetimi (var olan hesapta yalnızca aktif/pasif) |
| GET | `/api/admin/stats/` | Yönetici | Platform istatistikleri |
| GET | `/api/admin/blocked-domains/` | Yönetici | Listelerdeki engelli alan adları (`?search=&category=&source=&page=`, sayfa başına 50) |

## Yapay zekâ risk modeli

Listeler ne kadar büyük olursa olsun her gün yeni kumar ve yetişkin içerik
siteleri açılıyor. Bu yüzden FamSecur'a, **hiçbir listede olmayan** bir alan
adının adına bakarak ne kadar riskli göründüğünü tahmin eden küçük bir makine
öğrenmesi modeli eklendi. Model ücretsizdir, tamamen yerelde (kendi
bilgisayarımızda) eğitilir ve çalışır; dışarıya hiçbir veri gönderilmez.

Ebeveyn panelindeki **Alan adı test et** sayfasında sonuç kartının altında
"Yapay zekâ risk tahmini: %NN" olarak görünür. Tahmin %60 ve üzerindeyse
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
4. **Örneklem.** 100.000 kumar, 100.000 yetişkin ve ≈524.000 temiz alan adı
   (toplam ≈724.000). Sınıflar eşit sayıda değil; bunu
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

### Sonuçlar (144.850 alan adlık test kümesi)

Model eğitimde hiç görmediği alan adlarıyla ölçülür. Sitede uyarı, risk tahmini
**%60 ve üzerindeyse** gösterilir; bu yüzden asıl ölçüm o eşikte yapılır
(`metrics.json` → `at_warning_threshold`).

| Ölçüm (uyarı eşiği %60) | Değer |
| --- | --- |
| Doğruluk (riskli / temiz) | **%92,6** |
| Riskli alan adlarını yakalama oranı (recall) | %90,0 |
| Uyarıların gerçekten riskli çıkma oranı (precision) | %84,3 |
| Temiz sitelerde yanlış alarm oranı | %6,4 |
| Türkiye'de popüler temiz sitelerde yanlış alarm oranı | %5,4 |
| ROC AUC (riskli / temiz) | 0,972 |

| Sınıf | Kesinlik (precision) | Duyarlılık (recall) |
| --- | --- | --- |
| Kumar | %89,5 | %94,1 |
| Yetişkin | %71,0 | %84,7 |
| Temiz | %96,4 | %92,0 |

Örnek tahminler: `yenibahisadresi.net` %100, `canlimacizle-bahis.com` %97
(uyarı); `sahibinden.com` %10, `yemeksepeti.com` %1, `eba.gov.tr` %0 (uyarı yok).

Not: Test kümesindeki Türkçe riskli örneklerin etiketi kural motorundan geldiği
için bu dilimde ölçülen başarı biraz iyimser olabilir. Temiz listeler (Cisco
Umbrella) günlük değiştiği için model her yeniden eğitildiğinde sonuçlar küçük
farklar gösterebilir; sitedeki sayılar `metrics.json` dosyasıyla aynı tutulur.

Model yalnızca alan adının harflerine bakar, sitenin içeriğini görmez. Bu
yüzden `better.com` gibi "bet" içeren masum adlarda veya `n11.com` gibi çok
kısa adlarda yanılabilir. Modeli engel yerine uyarı olarak
kullanmamızın nedeni budur.

### Modeli yeniden eğitmek

```bash
cd backend
pip install -r requirements.txt
python -m ml.train_risk_model --download   # verileri indirir (~85 MB) ve eğitir, ~2 dk
python manage.py test tests                # model testleri dâhil
```

Ham veriler `backend/ml/data/` klasörüne iner ve git'e eklenmez. Eğitim
betiği sabit rastgelelik tohumu (`SEED = 42`) kullanır; aynı verilerle
çalıştırıldığında aynı sonucu verir. Model dosyası farklı bir scikit-learn
sürümüyle açılamazsa yukarıdaki komutla yeniden eğitmek yeterlidir; model
yüklenemezse site çalışmaya devam eder, yalnızca yapay zekâ tahmini görünmez.

Dosyalar: `backend/ml/train_risk_model.py` (eğitim),
`backend/ml/features.py` (eğitim ve tahminde ortak ön işleme),
`backend/shield/ml_risk.py` (Django'da modeli yükleyip tahmin yapan yardımcı).

## Kurulum

Gereksinimler: Python 3.11+, Node.js 20+.

Proje iki ayrı parçadan oluşur ve **iki ayrı terminal** gerekir: biri backend
(Python/Django), diğeri frontend (Node/React) için. `python` ve `pip`
komutları yalnızca `backend` klasöründe, `npm` komutları yalnızca `frontend`
klasöründe çalıştırılır. `backend` klasöründe `npm` çalıştırmayın; orada
`package.json` yoktur ve hata alırsınız.

### Windows'ta adım adım

Aşağıdaki komutlar PowerShell içindir (VS Code terminali de varsayılan olarak
PowerShell'dir). Önce proje klasörüne girin, ör. `cd C:\Users\Ad\famsecur-website`.

**1. terminal: backend**

```powershell
cd backend
py -m venv .venv                     # "py" yoksa: python -m venv .venv
.venv\Scripts\Activate.ps1           # satır başında (.venv) görünmeli
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo           # demo hesapları ve örnek veri
python manage.py runserver           # http://127.0.0.1:8000 — bu terminali açık bırakın
```

`Activate.ps1` için "betik çalıştırma bu sistemde devre dışı" hatası alırsanız
bir kez şunu çalıştırıp tekrar deneyin:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Komut İstemi (cmd) kullanıyorsanız etkinleştirme komutu `.venv\Scripts\activate.bat` olur.

**2. terminal: frontend** (yeni bir terminal açın, proje klasörüne girin)

```powershell
cd frontend
npm install                          # yalnızca ilk seferde
npm run dev                          # http://localhost:5173
```

Tarayıcıda `http://localhost:5173` adresini açın ve aşağıdaki demo hesaplarından
biriyle giriş yapın.

**Sonraki açılışlarda** yalnızca şunlar yeterlidir:

- 1. terminal: `cd backend`, `.venv\Scripts\Activate.ps1`, `python manage.py runserver`
- 2. terminal: `cd frontend`, `npm run dev`

### macOS / Linux

Backend (1. terminal):

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo       # demo hesapları ve örnek veri
python manage.py runserver       # http://127.0.0.1:8000
```

Testler:

```bash
python manage.py test tests
```

Frontend (2. terminal):

```bash
cd frontend
npm install
npm run dev                      # http://localhost:5173
```

Geliştirmede Vite, `/api` isteklerini `http://127.0.0.1:8000` adresine yönlendirir.
API başka bir adresteyse `frontend/.env` dosyasında `VITE_API_URL` tanımlayın.

### Örnek aileler ve iletişim talepleri (isteğe bağlı)

Panelleri dolu göstermek için 10 örnek aile (cihazları ve engel olaylarıyla)
ve 3 iletişim talebi ekler. Tekrar çalıştırmak güvenlidir.

```bash
python manage.py seed_families
```

Örnek ebeveynlerin hepsinin şifresi `Aile.12345` (ör. `mehmet.demir@ornek.com`).

### Tehdit kaynaklarını otomatik güncellemek (internet gerekir)

Üç kaynak adresinden otomatik güncellenir:

| Kaynak | İçerik |
| --- | --- |
| Resmî Kumar Alan Adı Havuzu | Polonya Maliye Bakanlığı yasa dışı kumar sicili (`/api/Register`, XML) |
| USOM Zararlı Bağlantılar | Siber Güvenlik Başkanlığı'nın herkese açık API'si; son 30 gün, kritiklik 1-4 |
| UT1 Kara Listeleri | Toulouse Capitole Üniversitesi; kumar, uyuşturucu, oltalama, zararlı yazılım (kayıt bazlı kategori). Yetişkin listesi milyonlarca kayıt olduğu için alınmaz |

**Her gün otomatik:** Sunucu çalışırken arka planda saatte bir uyanan bir görev
(`shield/scheduler.py`), son başarılı güncellemesinin üzerinden 24 saat geçen
kaynakları yeniler (başarısız olursa 6 saat sonra yeniden dener) ve saklama
süresi dolan engel olaylarını siler. `runserver` ile kendiliğinden başlar;
gunicorn gibi başka bir sunucuda `FAMSECUR_AUTO_UPDATE=1`, kapatmak için
`FAMSECUR_AUTO_UPDATE=0` ortam değişkenini kullanın.

**İstendiğinde:** Yönetim panelinde Tehdit kaynakları sayfasındaki
**Şimdi güncelle** düğmesiyle ya da hepsini birden komutla:

```bash
python manage.py refresh_sources
```

Kaynak düzenleme ekranındaki "Kaynak adresinden otomatik güncelle" işaretli her
kaynak güncellenir. USOM adresleri API'den, UT1 adresleri kategori arşivlerinden (tar.gz), diğer adresler düz metin liste
(satır başına bir alan adı / hosts biçimi) veya XML sicil olarak okunur. Çekme
başarısız olursa eski liste korunur ve hata panelde görünür. Resmî havuz hiç
güncellenmediyse repodaki sürümlenmiş dosya kullanılır.

Tehdit kaynaklarında her satıra kayda özel kategori de yazılabilir
(`ornek-bahis.com gambling`); Engellenen alan adları sayfasındaki kategori
filtresi bu sayede tüm listelerde çalışır.

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
  ml/          yapay zekâ risk modeli: eğitim betiği ve kayıtlı model
  tests/       API testleri
frontend/
  src/api.js            REST istemcisi (JWT, otomatik yenileme, hata yönetimi)
  src/auth.jsx          oturum durumu
  src/pages/public/     tanıtım sitesi, SSS, iletişim, giriş, kayıt
  src/pages/panel/      ebeveyn paneli
  src/pages/admin/      yönetim paneli
```
