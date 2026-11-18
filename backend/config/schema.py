"""API dokümantasyonu (Swagger / OpenAPI) için ortak tanımlar.

Belge drf-spectacular ile koddan otomatik üretilir:
- /api/schema/  OpenAPI 3 şeması (YAML)
- /api/docs/    Swagger arayüzü (uç noktaları tarayıcıdan denemek için)
- /api/redoc/   ReDoc arayüzü (okunması kolay belge)
"""

from drf_spectacular.utils import OpenApiResponse, inline_serializer
from rest_framework import serializers

ErrorSerializer = inline_serializer(
    name="Hata",
    fields={
        "detail": serializers.CharField(help_text="Kullanıcıya gösterilecek Türkçe hata mesajı."),
        "errors": serializers.DictField(
            child=serializers.ListField(child=serializers.CharField()),
            help_text="Alan bazlı hatalar, ör. {\"email\": [\"Bu alan zorunlu.\"]}",
        ),
    },
)


def error(description):
    return OpenApiResponse(ErrorSerializer, description=description)


E400 = error("Geçersiz veri; alan bazlı hatalar `errors` içinde döner.")
E401 = error("Oturum anahtarı yok, süresi dolmuş veya geçersiz.")
E403 = error("Bu işlem için yetkiniz yok (ör. yalnızca yönetici).")
E404 = error("Kayıt bulunamadı veya başka bir aileye ait.")
E429 = error("Çok fazla istek gönderildi; biraz sonra tekrar deneyin.")

# Kimlik doğrulama gerektiren uç noktaların ortak hata yanıtları.
AUTH_ERRORS = {401: E401, 403: E403}
