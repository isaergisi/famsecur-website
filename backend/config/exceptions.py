"""Tüm API hatalarını tek, anlaşılır bir biçimde döndürür.

Yanıt biçimi:
    {"detail": "İnsan tarafından okunabilir özet", "errors": {"alan": ["mesaj"]}}
"""

from django.db import IntegrityError
from django.http import Http404
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import exception_handler

STATUS_MESSAGES = {
    400: "Gönderilen veriler geçersiz.",
    401: "Bu işlem için giriş yapmalısınız.",
    403: "Bu işlem için yetkiniz yok.",
    404: "İstenen kayıt bulunamadı.",
    405: "Bu HTTP metodu bu adreste desteklenmiyor.",
    409: "Kayıt mevcut verilerle çakışıyor.",
    429: "Çok fazla istek gönderildi. Lütfen biraz sonra tekrar deneyin.",
}


def api_exception_handler(exc, context):
    if isinstance(exc, IntegrityError):
        return Response(
            {"detail": "Bu kayıt zaten mevcut veya başka bir kayıtla çakışıyor.", "errors": {}},
            status=status.HTTP_409_CONFLICT,
        )

    response = exception_handler(exc, context)
    if response is None:
        return None

    data = response.data
    if isinstance(exc, ValidationError):
        errors = data if isinstance(data, dict) else {"non_field_errors": data}
        first = next(iter(errors.values()), None)
        if isinstance(first, list) and first:
            first = first[0]
        detail = str(first) if first and len(errors) == 1 else STATUS_MESSAGES[400]
        response.data = {"detail": detail, "errors": errors}
        return response

    if isinstance(exc, Http404):
        detail = STATUS_MESSAGES[404]
    elif isinstance(data, dict) and "detail" in data:
        detail = str(data["detail"])
    else:
        detail = STATUS_MESSAGES.get(response.status_code, "Beklenmeyen bir hata oluştu.")
    response.data = {"detail": detail, "errors": {}}
    return response
