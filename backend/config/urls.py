from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from accounts.views import AdminUserViewSet, ChangePasswordView, LoginView, LogoutView, MeView, RegisterView
from content.views import ContactRequestViewSet, FAQViewSet
from shield.views import (
    AdminStatsView,
    BlockEventViewSet,
    CheckDomainView,
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
router.register("events", BlockEventViewSet, basename="event")
router.register("threat-sources", ThreatSourceViewSet, basename="threat-source")
router.register("faqs", FAQViewSet, basename="faq")
router.register("contact-requests", ContactRequestViewSet, basename="contact-request")
router.register("admin/users", AdminUserViewSet, basename="admin-user")

auth_urls = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("refresh/", TokenRefreshView.as_view(), name="token-refresh"),
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
    path("api/analyze/", PublicAnalyzeView.as_view(), name="analyze"),
    path("api/admin/stats/", AdminStatsView.as_view(), name="admin-stats"),
    path("api/", include(router.urls)),
]
