from rest_framework import permissions, viewsets
from rest_framework.throttling import ScopedRateThrottle

from accounts.permissions import IsAdminOrReadOnly, IsAdminRole

from .models import FAQ, ContactRequest
from .serializers import ContactRequestSerializer, FAQSerializer, PublicContactRequestSerializer


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
