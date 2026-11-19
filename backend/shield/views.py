from datetime import timedelta

from django.db.models import Count
from django.db.models.functions import TruncDate
from django.utils import timezone
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view, inline_serializer
from rest_framework import generics, mixins, permissions, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsAdminOrReadOnly, IsAdminRole
from config.schema import AUTH_ERRORS, E400, E404, E429

from .classifier import CATEGORY_LABELS, OFFICIAL_SOURCE_NAME, analyze_domain, official_gambling_domains
from .fetchers import refresh_source, uses_file_feed
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
from .services import ai_prediction, check_domain


def decision_fields() -> dict:
    return {
        "domain": serializers.CharField(),
        "action": serializers.ChoiceField(choices=["allow", "block"]),
        "category": serializers.CharField(allow_null=True),
        "category_label": serializers.CharField(allow_null=True),
        "score": serializers.IntegerField(help_text="0-100 risk puanı"),
        "reasons": serializers.ListField(child=serializers.CharField(), help_text="Kararın gerekçeleri"),
        "source": serializers.ChoiceField(
            choices=["threat_list", "official_list", "signals", "whitelist", "none", "device_off"],
            help_text="Kararın dayanağı: tehdit listesi, resmî kumar sicili, alan adı işaretleri, beyaz liste",
        ),
    }


AI_FIELD_HELP = "Yapay zekâ risk tahmini (yalnızca listelerde olmayan alan adları için)"
DECISION = inline_serializer("Karar", decision_fields())
DEMO_DECISION = inline_serializer("DemoKarari", {
    **decision_fields(), "ai": serializers.DictField(allow_null=True, help_text=AI_FIELD_HELP),
})
OpenApiResponse_CHECK = inline_serializer("DegerlendirmeYaniti", {
    "decision": DECISION,
    "message": serializers.CharField(),
    "ai": serializers.DictField(allow_null=True, help_text=AI_FIELD_HELP),
    "event": BlockEventSerializer(allow_null=True),
})


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
        if getattr(self, "swagger_fake_view", False):
            # API belgesi üretilirken oturum yoktur; yalnızca modelin türü gerekir.
            return self.get_serializer_class().Meta.model.objects.none()
        return getattr(self.family, self.related_name).all()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        if self.request.user.is_authenticated:
            context["family"] = self.family
        return context

    def perform_create(self, serializer):
        serializer.save(family=self.family)


@extend_schema_view(
    get=extend_schema(summary="Ailemi getir", description="Aile bilgisi ve özet sayılar."),
    put=extend_schema(summary="Aile bilgisini güncelle", responses={200: FamilySerializer, 400: E400, **AUTH_ERRORS}),
    patch=extend_schema(summary="Aile bilgisini kısmen güncelle", responses={200: FamilySerializer, 400: E400, **AUTH_ERRORS}),
)
@extend_schema(tags=["Aile ve politika"])
class FamilyView(generics.RetrieveUpdateAPIView):
    """GET/PATCH /api/family/"""

    serializer_class = FamilySerializer

    def get_object(self):
        return family_of(self.request.user)


@extend_schema_view(
    get=extend_schema(summary="Koruma politikasını getir"),
    put=extend_schema(summary="Koruma politikasını güncelle", description="Risk eşiği 30-100 arasında olmalı; oltalama ve zararlı yazılım kategorileri kapatılamaz.", responses={200: PolicySerializer, 400: E400, **AUTH_ERRORS}),
    patch=extend_schema(summary="Koruma politikasını kısmen güncelle", description="Risk eşiği 30-100 arasında olmalı; oltalama ve zararlı yazılım kategorileri kapatılamaz.", responses={200: PolicySerializer, 400: E400, **AUTH_ERRORS}),
)
@extend_schema(tags=["Aile ve politika"])
class PolicyView(generics.RetrieveUpdateAPIView):
    """GET/PUT/PATCH /api/policy/"""

    serializer_class = PolicySerializer

    def get_object(self):
        return family_of(self.request.user).policy


@extend_schema_view(
    list=extend_schema(summary="Cihaz listele"),
    create=extend_schema(summary="Cihaz ekle", responses={201: DeviceSerializer, 400: E400, **AUTH_ERRORS}),
    retrieve=extend_schema(summary="Cihaz ayrıntısı", responses={200: DeviceSerializer, 404: E404, **AUTH_ERRORS}),
    update=extend_schema(summary="Cihaz güncelle", responses={200: DeviceSerializer, 400: E400, 404: E404, **AUTH_ERRORS}),
    partial_update=extend_schema(summary="Cihaz kısmen güncelle", responses={200: DeviceSerializer, 400: E400, 404: E404, **AUTH_ERRORS}),
    destroy=extend_schema(summary="Cihaz sil", responses={204: None, 404: E404, **AUTH_ERRORS}),
)
@extend_schema(tags=["Cihazlar"])
class DeviceViewSet(FamilyScopedMixin, viewsets.ModelViewSet):
    serializer_class = DeviceSerializer
    related_name = "devices"


@extend_schema_view(
    list=extend_schema(summary="Beyaz liste kaydı listele", parameters=[OpenApiParameter("search", str, description="Alan adında arama")]),
    create=extend_schema(summary="Beyaz liste kaydı ekle", responses={201: WhitelistEntrySerializer, 400: E400, **AUTH_ERRORS}),
    retrieve=extend_schema(summary="Beyaz liste kaydı ayrıntısı", responses={200: WhitelistEntrySerializer, 404: E404, **AUTH_ERRORS}),
    update=extend_schema(summary="Beyaz liste kaydı güncelle", responses={200: WhitelistEntrySerializer, 400: E400, 404: E404, **AUTH_ERRORS}),
    partial_update=extend_schema(summary="Beyaz liste kaydı kısmen güncelle", responses={200: WhitelistEntrySerializer, 400: E400, 404: E404, **AUTH_ERRORS}),
    destroy=extend_schema(summary="Beyaz liste kaydı sil", responses={204: None, 404: E404, **AUTH_ERRORS}),
)
@extend_schema(tags=["Beyaz liste"])
class WhitelistViewSet(FamilyScopedMixin, viewsets.ModelViewSet):
    serializer_class = WhitelistEntrySerializer
    related_name = "whitelist"

    def get_queryset(self):
        qs = super().get_queryset()
        search = self.request.query_params.get("search")
        return qs.filter(domain__icontains=search) if search else qs


@extend_schema_view(
    list=extend_schema(
        summary="Engel olaylarını listele",
        parameters=[
            OpenApiParameter("category", str, description="Kategori (ör. gambling, adult, phishing)"),
            OpenApiParameter("device", int, description="Cihaz kimliği"),
            OpenApiParameter("search", str, description="Alan adında arama"),
        ],
    ),
    retrieve=extend_schema(summary="Engel olayı ayrıntısı", responses={200: BlockEventSerializer, 404: E404, **AUTH_ERRORS}),
    destroy=extend_schema(summary="Engel olayını sil", responses={204: None, 404: E404, **AUTH_ERRORS}),
    clear=extend_schema(
        summary="Tüm engel olaylarını sil",
        request=None,
        responses={200: inline_serializer("TemizlemeYaniti", {"detail": serializers.CharField(), "deleted": serializers.IntegerField()})},
    ),
    stats=extend_schema(
        summary="Engel istatistikleri",
        description="Kategori, cihaz ve gün bazında sayılar, en çok engellenen alan adları ve haftalık özet.",
        responses={200: inline_serializer("OlayIstatistikleri", {
            "total": serializers.IntegerField(),
            "last_7_days": serializers.IntegerField(),
            "by_category": serializers.ListField(child=serializers.DictField()),
            "by_device": serializers.ListField(child=serializers.DictField()),
            "by_day": serializers.ListField(child=serializers.DictField()),
            "top_domains": serializers.ListField(child=serializers.DictField()),
            "weekly": serializers.DictField(),
        })},
    ),
)
@extend_schema(tags=["Engel olayları"])
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
            "weekly": self._weekly_summary(events),
        })

    @staticmethod
    def _weekly_summary(events):
        """Son 7 günün özeti: gün gün engel sayısı (boş günler 0), önceki haftayla kıyas, öne çıkan kategori/cihaz."""
        today = timezone.localdate()
        start = today - timedelta(days=6)
        week = events.filter(created_at__date__gte=start)
        previous = events.filter(created_at__date__gte=start - timedelta(days=7), created_at__date__lt=start)
        counts = {
            row["day"]: row["count"]
            for row in week.annotate(day=TruncDate("created_at")).values("day").annotate(count=Count("id"))
        }
        top_category = week.values("category").annotate(count=Count("id")).order_by("-count").first()
        top_device = (
            week.exclude(device=None).values("device__name").annotate(count=Count("id")).order_by("-count").first()
        )
        return {
            "start": start.isoformat(),
            "end": today.isoformat(),
            "total": week.count(),
            "previous_total": previous.count(),
            "days": [
                {"day": (start + timedelta(days=i)).isoformat(), "count": counts.get(start + timedelta(days=i), 0)}
                for i in range(7)
            ],
            "top_category": top_category,
            "top_device": {"name": top_device["device__name"], "count": top_device["count"]} if top_device else None,
        }


@extend_schema(
    tags=["Karar motoru"],
    summary="Alan adını aile politikasıyla değerlendir",
    description=(
        "Sıra: cihaz koruması → beyaz liste → tehdit kaynakları → resmî kumar havuzu → sinyal puanlaması. "
        "Engellenirse olay kaydedilir ve **201**, izin verilirse hiçbir şey kaydedilmez ve **200** döner. "
        "Alan adı hiçbir listede yoksa `ai` alanında yapay zekâ risk tahmini de gelir (kararı değiştirmez)."
    ),
    request=CheckDomainSerializer,
    responses={
        200: OpenApiResponse_CHECK,
        201: OpenApiResponse_CHECK,
        400: E400,
        **AUTH_ERRORS,
    },
)
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
                "ai": result["ai"],
                "event": BlockEventSerializer(event).data if event else None,
            },
            status=status.HTTP_201_CREATED if event else status.HTTP_200_OK,
        )


@extend_schema(
    tags=["Karar motoru"],
    summary="Canlı demo: alan adını analiz et",
    description="Tanıtım sitesindeki demo. Giriş gerekmez, hiçbir şey kaydedilmez. Dakikada 30 istekle sınırlıdır. Alan adı hiçbir listede yoksa `ai` alanında yapay zekâ risk tahmini de gelir.",
    auth=[],
    request=PublicAnalyzeSerializer,
    responses={200: DEMO_DECISION, 400: E400, 429: E429},
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
        return Response({**decision.to_dict(), "ai": ai_prediction(None, decision)})


@extend_schema_view(
    list=extend_schema(summary="Tehdit kaynağı listele", description="Herkes aktif kaynakları görür; yönetici tümünü görür. Ekleme, güncelleme ve silme yalnızca yöneticidir."),
    create=extend_schema(summary="Tehdit kaynağı ekle", responses={201: ThreatSourceSerializer, 400: E400, **AUTH_ERRORS}),
    retrieve=extend_schema(summary="Tehdit kaynağı ayrıntısı", responses={200: ThreatSourceSerializer, 404: E404, **AUTH_ERRORS}),
    update=extend_schema(summary="Tehdit kaynağı güncelle", responses={200: ThreatSourceSerializer, 400: E400, 404: E404, **AUTH_ERRORS}),
    partial_update=extend_schema(summary="Tehdit kaynağı kısmen güncelle", responses={200: ThreatSourceSerializer, 400: E400, 404: E404, **AUTH_ERRORS}),
    destroy=extend_schema(summary="Tehdit kaynağı sil", responses={204: None, 404: E404, **AUTH_ERRORS}),
)
@extend_schema(tags=["Tehdit kaynakları"])
class ThreatSourceViewSet(viewsets.ModelViewSet):
    serializer_class = ThreatSourceSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_serializer_context(self):
        return {**super().get_serializer_context(), "view_action": self.action}

    @extend_schema(
        summary="Kaynağı adresinden şimdi güncelle",
        description="Kaynak adresinden (USOM API, UT1 arşivleri, düz metin liste veya XML sicil) alan adlarını çeker. "
                    "Başarısız olursa eski liste korunur ve 502 döner.",
        request=None,
        responses={200: ThreatSourceSerializer, 502: E400, **AUTH_ERRORS},
    )
    @action(detail=True, methods=["post"])
    def refresh(self, request, pk=None):
        source = self.get_object()
        try:
            count = refresh_source(source)
        except Exception:
            return Response(
                {"detail": f"Kaynak güncellenemedi, eski liste korundu. {source.last_fetch_error}", "errors": {}},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        data = self.get_serializer(source).data
        data["detail"] = f"{count} alan adı alındı."
        return Response(data)

    def get_queryset(self):
        qs = ThreatSource.objects.all()
        user = self.request.user
        if not (user.is_authenticated and user.is_admin):
            qs = qs.filter(is_active=True)
        return qs


@extend_schema(
    tags=["Yönetim"],
    summary="Platform istatistikleri",
    responses={200: inline_serializer("PlatformIstatistikleri", {
        "users": serializers.IntegerField(),
        "parents": serializers.IntegerField(),
        "families": serializers.IntegerField(),
        "devices": serializers.IntegerField(),
        "block_events": serializers.IntegerField(),
        "block_events_7d": serializers.IntegerField(),
        "open_contact_requests": serializers.IntegerField(),
        "threat_sources": serializers.IntegerField(),
        "events_by_category": serializers.ListField(child=serializers.DictField()),
    }), **AUTH_ERRORS},
)
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


class BlockedDomainPagination(PageNumberPagination):
    page_size = 50


@extend_schema(
    tags=["Yönetim"],
    summary="Engellenen alan adları",
    description=(
        "Karar motorunun doğrudan engellediği tüm liste kayıtları: resmî kumar alan adı havuzu ve aktif "
        "tehdit kaynakları. `?search=` alan adında arar, `?category=` ve `?source=` (kaynak adı) filtreler. "
        "Sayfa başına 50 kayıt."
    ),
    parameters=[
        OpenApiParameter("search", str, description="Alan adında arama"),
        OpenApiParameter("category", str, description="Kategori (ör. gambling, phishing)"),
        OpenApiParameter("source", str, description="Kaynak adı"),
        OpenApiParameter("page", int, description="Sayfa numarası"),
    ],
    responses={200: inline_serializer("EngellenenAlanAdlari", {
        "count": serializers.IntegerField(),
        "next": serializers.CharField(allow_null=True),
        "previous": serializers.CharField(allow_null=True),
        "page_size": serializers.IntegerField(),
        "sources": serializers.ListField(child=serializers.DictField()),
        "results": serializers.ListField(child=serializers.DictField()),
    }), **AUTH_ERRORS},
)
class BlockedDomainsView(APIView):
    """GET /api/admin/blocked-domains/ — listelerdeki tüm engelli alan adları, aranabilir ve sayfalı."""

    permission_classes = [IsAdminRole]

    @staticmethod
    def _rows():
        rows = []
        official = ThreatSource.objects.filter(name=OFFICIAL_SOURCE_NAME).first()
        if official is None or uses_file_feed(official):
            rows = [(d, "gambling", OFFICIAL_SOURCE_NAME) for d in sorted(official_gambling_domains())]
        for source in ThreatSource.objects.filter(is_active=True):
            rows.extend((d, category, source.name) for d, category in source.domain_entries())
        return rows

    def get(self, request):
        rows = self._rows()
        sources = {}
        for _, category, name in rows:
            sources[name] = sources.get(name, 0) + 1

        params = request.query_params
        search = params.get("search", "").strip().lower()
        if search:
            rows = [r for r in rows if search in r[0]]
        if params.get("category"):
            rows = [r for r in rows if r[1] == params["category"]]
        if params.get("source"):
            rows = [r for r in rows if r[2] == params["source"]]

        paginator = BlockedDomainPagination()
        page = paginator.paginate_queryset(rows, request, view=self)
        response = paginator.get_paginated_response([
            {"domain": d, "category": c, "category_label": CATEGORY_LABELS.get(c, c), "source": s}
            for d, c, s in page
        ])
        response.data["page_size"] = paginator.page_size
        response.data["sources"] = [{"name": n, "count": c} for n, c in sorted(sources.items())]
        return response


@extend_schema(
    tags=["Aile ve politika"],
    summary="Engellenen alan adları (salt okunur)",
    description="Yönetim panelindeki listenin ebeveynler için salt okunur hâli; aynı arama, filtre ve sayfalama.",
)
class ParentBlockedDomainsView(BlockedDomainsView):
    """GET /api/blocked-domains/ — giriş yapmış her kullanıcı görebilir, yalnızca okuma."""

    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get", "head", "options"]
