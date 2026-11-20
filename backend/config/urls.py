from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from rest_framework.routers import DefaultRouter

from accounts.views import (
    AdminUserViewSet,
    ChangePasswordView,
    LoginView,
    LogoutView,
    MeView,
    RefreshView,
    RegisterView,
)
from content.views import ContactRequestViewSet, FAQViewSet
from shield.views import (
    AdminStatsView,
    BlockedDomainsView,
    ParentBlockedDomainsView,
    BlockEventViewSet,
    BlockListViewSet,
    CheckDomainView,
    ConsentView,
    DailySummaryView,
    SubscriptionCancelView,
    DeviceViewSet,
    FamilyView,
    PolicyView,
    PublicAnalyzeView,
    ThreatSourceViewSet,
    WhitelistViewSet,
)

router = DefaultRouter()
router.register("devices", DeviceViewSet, basename="device")
router.register("whitelist", WhitelistViewSet, basename="whitelist")
router.register("blocklist", BlockListViewSet, basename="blocklist")
router.register("events", BlockEventViewSet, basename="event")
router.register("threat-sources", ThreatSourceViewSet, basename="threat-source")
router.register("faqs", FAQViewSet, basename="faq")
router.register("contact-requests", ContactRequestViewSet, basename="contact-request")
router.register("admin/users", AdminUserViewSet, basename="admin-user")

auth_urls = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("refresh/", RefreshView.as_view(), name="token-refresh"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("me/", MeView.as_view(), name="me"),
    path("change-password/", ChangePasswordView.as_view(), name="change-password"),
]

urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("api/auth/", include(auth_urls)),
    path("api/family/", FamilyView.as_view(), name="family"),
    path("api/policy/", PolicyView.as_view(), name="policy"),
    path("api/check/", CheckDomainView.as_view(), name="check-domain"),
    path("api/consents/", ConsentView.as_view(), name="consents"),
    path("api/subscription/cancel/", SubscriptionCancelView.as_view(), name="subscription-cancel"),
    path("api/daily-summary/", DailySummaryView.as_view(), name="daily-summary"),
    path("api/analyze/", PublicAnalyzeView.as_view(), name="analyze"),
    path("api/admin/stats/", AdminStatsView.as_view(), name="admin-stats"),
    path("api/admin/blocked-domains/", BlockedDomainsView.as_view(), name="blocked-domains"),
    path("api/blocked-domains/", ParentBlockedDomainsView.as_view(), name="parent-blocked-domains"),
    path("api/", include(router.urls)),
    # API belgesi: koddan otomatik üretilen OpenAPI şeması ve arayüzleri
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]
