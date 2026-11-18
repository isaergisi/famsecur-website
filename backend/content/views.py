from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import permissions, viewsets
from rest_framework.throttling import ScopedRateThrottle

from accounts.permissions import IsAdminOrReadOnly, IsAdminRole
from config.schema import AUTH_ERRORS, E400, E404, E429

from .models import FAQ, ContactRequest
from .serializers import ContactRequestSerializer, FAQSerializer, PublicContactRequestSerializer


@extend_schema_view(
    list=extend_schema(summary="SSS listele", description="Herkes yayındaki soruları görür; ekleme, güncelleme ve silme yalnızca yöneticidir.", auth=[]),
    create=extend_schema(summary="SSS ekle", responses={201: FAQSerializer, 400: E400, **AUTH_ERRORS}),
    retrieve=extend_schema(summary="SSS ayrıntısı", auth=[], responses={200: FAQSerializer, 404: E404, **AUTH_ERRORS}),
    update=extend_schema(summary="SSS güncelle", responses={200: FAQSerializer, 400: E400, 404: E404, **AUTH_ERRORS}),
    partial_update=extend_schema(summary="SSS kısmen güncelle", responses={200: FAQSerializer, 400: E400, 404: E404, **AUTH_ERRORS}),
    destroy=extend_schema(summary="SSS sil", responses={204: None, 404: E404, **AUTH_ERRORS}),
)
@extend_schema(tags=["SSS"])
class FAQViewSet(viewsets.ModelViewSet):
    """Herkes yayındaki soruları okur; yönetici tüm soruları yönetir."""

    serializer_class = FAQSerializer
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = None

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and user.is_admin:
            return FAQ.objects.all()
        return FAQ.objects.filter(is_published=True)


@extend_schema_view(
    list=extend_schema(summary="İletişim talebi listele", parameters=[OpenApiParameter("status", str, description="Duruma göre filtre")]),
    create=extend_schema(summary="İletişim talebi gönder", description="Ziyaretçi formu; giriş gerekmez, saatte 5 istekle sınırlıdır.", auth=[], request=PublicContactRequestSerializer, responses={201: PublicContactRequestSerializer, 400: E400, 429: E429}),
    retrieve=extend_schema(summary="İletişim talebi ayrıntısı", responses={200: ContactRequestSerializer, 404: E404, **AUTH_ERRORS}),
    update=extend_schema(summary="İletişim talebi güncelle", responses={200: ContactRequestSerializer, 400: E400, 404: E404, **AUTH_ERRORS}),
    partial_update=extend_schema(summary="İletişim talebi kısmen güncelle", responses={200: ContactRequestSerializer, 400: E400, 404: E404, **AUTH_ERRORS}),
    destroy=extend_schema(summary="İletişim talebi sil", responses={204: None, 404: E404, **AUTH_ERRORS}),
)
@extend_schema(tags=["İletişim talepleri"])
class ContactRequestViewSet(viewsets.ModelViewSet):
    """Ziyaretçi talep gönderir (POST); listeleme, güncelleme ve silme yalnızca yöneticinindir."""

    queryset = ContactRequest.objects.all()

    def get_permissions(self):
        if self.action == "create":
            return [permissions.AllowAny()]
        return [IsAdminRole()]

    def get_throttles(self):
        if self.action == "create":
            self.throttle_scope = "contact"
            return [ScopedRateThrottle()]
        return super().get_throttles()

    def get_serializer_class(self):
        if self.action == "create":
            return PublicContactRequestSerializer
        return ContactRequestSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        status_filter = self.request.query_params.get("status")
        return qs.filter(status=status_filter) if status_filter else qs
