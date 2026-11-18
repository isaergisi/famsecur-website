"""FamSecur web API ayarları.

Gizli değerler ortam değişkenlerinden okunur; geliştirme için güvenli olmayan
varsayılanlar yalnızca DEBUG açıkken kullanılır.
"""

import os
from datetime import timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DEBUG = os.environ.get("DJANGO_DEBUG", "1") == "1"
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY") or (
    "dev-only-insecure-key-change-me-in-production-0123456789" if DEBUG else None
)
if not SECRET_KEY:
    raise RuntimeError("DJANGO_SECRET_KEY ortam değişkeni üretimde zorunludur.")

ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "corsheaders",
    "drf_spectacular",
    "drf_spectacular_sidecar",
    "accounts",
    "shield",
    "content",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.environ.get("DJANGO_DB_PATH", BASE_DIR / "db.sqlite3"),
    }
}

AUTH_USER_MODEL = "accounts.User"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "tr"
TIME_ZONE = "Europe/Istanbul"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "EXCEPTION_HANDLER": "config.exceptions.api_exception_handler",
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_THROTTLE_CLASSES": ["rest_framework.throttling.ScopedRateThrottle"],
    "DEFAULT_THROTTLE_RATES": {
        "public_analyze": "30/minute",
        "contact": "5/hour",
        "auth": "20/minute",
    },
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "UPDATE_LAST_LOGIN": True,
}

SPECTACULAR_SETTINGS = {
    "TITLE": "FamSecur API",
    "DESCRIPTION": (
        "FamSecur ebeveyn koruma sisteminin REST API belgesi.\n\n"
        "**Nasıl denenir?**\n"
        "1. `POST /api/auth/login/` uç noktasını açın, *Try it out* ile demo hesabıyla giriş yapın "
        "(ebeveyn: `ebeveyn@famsecur.com` / `Ebeveyn.12345`, yönetici: `admin@famsecur.com` / `Admin.12345`).\n"
        "2. Yanıttaki `access` değerini kopyalayın.\n"
        "3. Sağ üstteki **Authorize** düğmesine basıp yapıştırın. Artık kilitli uç noktaları deneyebilirsiniz.\n\n"
        "Tüm hatalar `{\"detail\": \"...\", \"errors\": {alan: [mesaj]}}` biçiminde Türkçe döner."
    ),
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": True,
    "SWAGGER_UI_DIST": "SIDECAR",
    "SWAGGER_UI_FAVICON_HREF": "SIDECAR",
    "REDOC_DIST": "SIDECAR",
    "SWAGGER_UI_SETTINGS": {"persistAuthorization": True, "displayRequestDuration": True, "filter": True},
    "TAGS": [
        {"name": "Kimlik doğrulama", "description": "Kayıt, giriş, oturum yenileme ve profil."},
        {"name": "Aile ve politika", "description": "Ebeveynin ailesi ve koruma politikası."},
        {"name": "Cihazlar", "description": "Ailenin cihazları (CRUD)."},
        {"name": "Beyaz liste", "description": "Ailenin her zaman izin verdiği alan adları (CRUD)."},
        {"name": "Engel olayları", "description": "Karar motorunun engellediği istekler: okuma, silme, istatistik."},
        {"name": "Karar motoru", "description": "Alan adını değerlendirme (ebeveyn) ve sitedeki canlı demo (herkese açık)."},
        {"name": "Tehdit kaynakları", "description": "Tüm ailelerde geçerli engel listeleri; yönetimi yöneticidedir."},
        {"name": "SSS", "description": "Sıkça sorulan sorular; yönetimi yöneticidedir."},
        {"name": "İletişim talepleri", "description": "Ziyaretçi talep gönderir, yönetici yönetir."},
        {"name": "Yönetim", "description": "Yalnızca yönetici: kullanıcı yönetimi ve platform istatistikleri."},
    ],
}

CORS_ALLOWED_ORIGINS = os.environ.get(
    "CORS_ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
).split(",")
