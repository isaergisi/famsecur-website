from datetime import timedelta

from django.db.models import Count
from django.db.models.functions import TruncDate
from django.utils import timezone
from rest_framework import generics, mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsAdminOrReadOnly, IsAdminRole

from .classifier import analyze_domain
from .models import BlockEvent, Device, Family, ThreatSource
from .serializers import (
    BlockEventSerializer,
    CheckDomainSerializer,
    DeviceSerializer,
    FamilySerializer,
    PolicySerializer,
    PublicAnalyzeSerializer,
    ThreatSourceSerializer,
    WhitelistEntrySerializer,
)
from .services import check_domain


def family_of(user) -> Family:
    try:
        return user.family
    except Family.DoesNotExist:
        # Ör. createsuperuser ile açılan hesaplar: aile ilk kullanımda oluşturulur.
        return Family.create_with_defaults(owner=user, name=f"{user.first_name or user.email} Ailesi")


class FamilyScopedMixin:
    """Her kullanıcı yalnızca kendi ailesinin verilerini görür ve değiştirir."""

    related_name: str

    @property
    def family(self) -> Family:
        return family_of(self.request.user)

    def get_queryset(self):
        return getattr(self.family, self.related_name).all()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        if self.request.user.is_authenticated:
            context["family"] = self.family
        return context

    def perform_create(self, serializer):
        serializer.save(family=self.family)


class FamilyView(generics.RetrieveUpdateAPIView):
    """GET/PATCH /api/family/"""

    serializer_class = FamilySerializer

    def get_object(self):
        return family_of(self.request.user)


class PolicyView(generics.RetrieveUpdateAPIView):
    """GET/PUT/PATCH /api/policy/"""

    serializer_class = PolicySerializer

    def get_object(self):
        return family_of(self.request.user).policy


class DeviceViewSet(FamilyScopedMixin, viewsets.ModelViewSet):
    serializer_class = DeviceSerializer
    related_name = "devices"


class WhitelistViewSet(FamilyScopedMixin, viewsets.ModelViewSet):
    serializer_class = WhitelistEntrySerializer
    related_name = "whitelist"

    def get_queryset(self):
        qs = super().get_queryset()
        search = self.request.query_params.get("search")
        return qs.filter(domain__icontains=search) if search else qs


class BlockEventViewSet(
    FamilyScopedMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """Olaylar yalnızca karar motoru tarafından üretilir; ebeveyn okuyabilir ve silebilir."""

    serializer_class = BlockEventSerializer
    related_name = "events"

    def get_queryset(self):
        qs = super().get_queryset().select_related("device")
        params = self.request.query_params
        if params.get("category"):
            qs = qs.filter(category=params["category"])
        if params.get("device"):
            qs = qs.filter(device_id=params["device"])
        if params.get("search"):
            qs = qs.filter(domain__icontains=params["search"])
        return qs

    @action(detail=False, methods=["delete"])
    def clear(self, request):
        deleted, _ = self.family.events.all().delete()
        return Response({"detail": f"{deleted} olay silindi.", "deleted": deleted})

    @action(detail=False, methods=["get"])
    def stats(self, request):
        events = self.family.events.all()
        since = timezone.now() - timedelta(days=7)
        by_day = (
            events.filter(created_at__gte=since)
            .annotate(day=TruncDate("created_at"))
            .values("day")
            .annotate(count=Count("id"))
            .order_by("day")
        )
        return Response({
            "total": events.count(),
            "last_7_days": events.filter(created_at__gte=since).count(),
            "by_category": list(events.values("category").annotate(count=Count("id")).order_by("-count")),
            "by_device": list(
                events.exclude(device=None).values("device__name").annotate(count=Count("id")).order_by("-count")[:5]
            ),
            "by_day": [{"day": row["day"].isoformat(), "count": row["count"]} for row in by_day],
            "top_domains": list(events.values("domain").annotate(count=Count("id")).order_by("-count")[:5]),
        })


class CheckDomainView(APIView):
    """POST /api/check/ — bir cihazdan gelen DNS sorgusunu aile politikasıyla değerlendirir."""

    def post(self, request):
        family = family_of(request.user)
        serializer = CheckDomainSerializer(data=request.data, context={"family": family})
        serializer.is_valid(raise_exception=True)
        result = check_domain(family, serializer.validated_data["domain"], serializer.validated_data.get("device"))
        event = result["event"]
        return Response(
            {
                "decision": result["decision"],
                "message": result["message"],
                "event": BlockEventSerializer(event).data if event else None,
            },
            status=status.HTTP_201_CREATED if event else status.HTTP_200_OK,
        )


class PublicAnalyzeView(APIView):
    """POST /api/analyze/ — tanıtım sitesindeki canlı demo. Hiçbir şey kaydetmez."""

    permission_classes = [permissions.AllowAny]
    throttle_scope = "public_analyze"

    def post(self, request):
        serializer = PublicAnalyzeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        decision = analyze_domain(
            serializer.validated_data["domain"], blocked_domains=ThreatSource.active_domain_map()
        )
        return Response(decision.to_dict())


class ThreatSourceViewSet(viewsets.ModelViewSet):
    serializer_class = ThreatSourceSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        qs = ThreatSource.objects.all()
        user = self.request.user
        if not (user.is_authenticated and user.is_admin):
            qs = qs.filter(is_active=True)
        return qs


class AdminStatsView(APIView):
    """GET /api/admin/stats/ — yönetici paneli özet sayıları."""

    permission_classes = [IsAdminRole]

    def get(self, request):
        from accounts.models import User
        from content.models import ContactRequest

        since = timezone.now() - timedelta(days=7)
        return Response({
            "users": User.objects.count(),
            "parents": User.objects.filter(role=User.Role.PARENT).count(),
            "families": Family.objects.count(),
            "devices": Device.objects.count(),
            "block_events": BlockEvent.objects.count(),
            "block_events_7d": BlockEvent.objects.filter(created_at__gte=since).count(),
            "open_contact_requests": ContactRequest.objects.exclude(status=ContactRequest.Status.RESOLVED).count(),
            "threat_sources": ThreatSource.objects.filter(is_active=True).count(),
            "events_by_category": list(
                BlockEvent.objects.values("category").annotate(count=Count("id")).order_by("-count")
            ),
        })
