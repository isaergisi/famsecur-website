from django.core.cache import cache
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User
from content.models import FAQ, ContactRequest
from shield.models import BlockEvent, Family, ThreatSource


class BaseAPITest(APITestCase):
    def setUp(self):
        cache.clear()

    def register(self, email="veli@example.com", password="Guclu.Sifre123", **extra):
        payload = {"email": email, "password": password, "first_name": "Veli", **extra}
        return self.client.post("/api/auth/register/", payload, format="json")

    def login_as(self, email="veli@example.com", password="Guclu.Sifre123"):
        response = self.client.post("/api/auth/login/", {"email": email, "password": password}, format="json")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")
        return response


class AuthTests(BaseAPITest):
    def test_register_creates_family_with_default_policy(self):
        response = self.register(family_name="Test Ailesi")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("access", response.data)
        family = Family.objects.get(owner__email="veli@example.com")
        self.assertEqual(family.name, "Test Ailesi")
        self.assertEqual(family.policy.risk_threshold, 70)

    def test_duplicate_email_and_weak_password_are_rejected(self):
        self.register()
        response = self.register()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data["errors"])
        response = self.register(email="baska@example.com", password="123")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_wrong_password_returns_401_with_message(self):
        self.register()
        response = self.client.post("/api/auth/login/", {"email": "veli@example.com", "password": "yanlis"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("hatalı", response.data["detail"])

    def test_protected_endpoint_requires_token(self):
        self.assertEqual(self.client.get("/api/devices/").status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_and_refresh(self):
        self.register()
        login = self.login_as()
        self.assertEqual(self.client.get("/api/auth/me/").data["email"], "veli@example.com")
        response = self.client.post("/api/auth/refresh/", {"refresh": login.data["refresh"]}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class FamilyResourceTests(BaseAPITest):
    def setUp(self):
        super().setUp()
        self.register()
        self.login_as()

    def test_device_crud(self):
        response = self.client.post("/api/devices/", {"name": "Tablet", "device_type": "tablet"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        device_id = response.data["id"]
        self.assertEqual(len(self.client.get("/api/devices/").data["results"]), 1)
        response = self.client.patch(f"/api/devices/{device_id}/", {"is_protected": False}, format="json")
        self.assertFalse(response.data["is_protected"])
        response = self.client.put(f"/api/devices/{device_id}/", {"name": "Tablet 2", "device_type": "tablet"}, format="json")
        self.assertEqual(response.data["name"], "Tablet 2")
        self.assertEqual(self.client.delete(f"/api/devices/{device_id}/").status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(self.client.get(f"/api/devices/{device_id}/").status_code, status.HTTP_404_NOT_FOUND)

    def test_duplicate_device_name_and_bad_mac(self):
        self.client.post("/api/devices/", {"name": "Tablet"}, format="json")
        response = self.client.post("/api/devices/", {"name": "tablet"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response = self.client.post("/api/devices/", {"name": "PC", "mac_address": "xx"}, format="json")
        self.assertIn("mac_address", response.data["errors"])

    def test_users_cannot_see_other_families_data(self):
        device_id = self.client.post("/api/devices/", {"name": "Tablet"}, format="json").data["id"]
        self.client.credentials()
        self.register(email="diger@example.com")
        self.login_as(email="diger@example.com")
        self.assertEqual(self.client.get(f"/api/devices/{device_id}/").status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(self.client.delete(f"/api/devices/{device_id}/").status_code, status.HTTP_404_NOT_FOUND)

    def test_policy_business_rules(self):
        response = self.client.patch("/api/policy/", {"risk_threshold": 10}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response = self.client.patch("/api/policy/", {"enabled_categories": ["gambling"]}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response = self.client.patch(
            "/api/policy/",
            {"risk_threshold": 85, "enforcement_mode": "warning", "enabled_categories": ["adult", "phishing", "malware"]},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["enforcement_mode"], "warning")

    def test_whitelist_normalizes_domain_and_rejects_duplicates(self):
        response = self.client.post("/api/whitelist/", {"domain": "https://Better.com/path"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["domain"], "better.com")
        response = self.client.post("/api/whitelist/", {"domain": "better.com"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response = self.client.post("/api/whitelist/", {"domain": "not a domain"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_check_blocks_logs_event_and_respects_whitelist(self):
        device_id = self.client.post("/api/devices/", {"name": "Tablet"}, format="json").data["id"]
        response = self.client.post("/api/check/", {"domain": "bet2x.com", "device": device_id}, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["decision"]["action"], "block")
        self.assertEqual(response.data["event"]["device_name"], "Tablet")

        response = self.client.post("/api/check/", {"domain": "google.com"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["decision"]["action"], "allow")
        self.assertEqual(BlockEvent.objects.count(), 1)  # izin verilenler kaydedilmez

        self.client.post("/api/whitelist/", {"domain": "better.com"}, format="json")
        response = self.client.post("/api/check/", {"domain": "www.better.com"}, format="json")
        self.assertEqual(response.data["decision"]["action"], "allow")

    def test_unprotected_device_is_not_filtered(self):
        device_id = self.client.post("/api/devices/", {"name": "TV", "is_protected": False}, format="json").data["id"]
        response = self.client.post("/api/check/", {"domain": "bet2x.com", "device": device_id}, format="json")
        self.assertEqual(response.data["decision"]["action"], "allow")

    def test_events_list_stats_delete_and_clear(self):
        for domain in ("bet2x.com", "casino777.xyz", "pornhub.com"):
            self.client.post("/api/check/", {"domain": domain}, format="json")
        events = self.client.get("/api/events/").data["results"]
        self.assertEqual(len(events), 3)
        self.assertEqual(self.client.get("/api/events/?category=gambling").data["count"], 2)
        self.assertEqual(self.client.get("/api/events/stats/").data["total"], 3)
        self.assertEqual(self.client.delete(f"/api/events/{events[0]['id']}/").status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(self.client.delete("/api/events/clear/").data["deleted"], 2)
        # Olaylar elle oluşturulamaz
        self.assertEqual(self.client.post("/api/events/", {}, format="json").status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class PublicAndAdminTests(BaseAPITest):
    def setUp(self):
        super().setUp()
        self.admin = User.objects.create_user("admin@example.com", "Guclu.Sifre123", role=User.Role.ADMIN)
        self.register()

    def test_public_analyze_and_faq(self):
        FAQ.objects.create(question="Yayında", answer="a")
        FAQ.objects.create(question="Taslak", answer="b", is_published=False)
        response = self.client.post("/api/analyze/", {"domain": "casino777.xyz"}, format="json")
        self.assertEqual(response.data["action"], "block")
        self.assertEqual(len(self.client.get("/api/faqs/").data), 1)
        self.assertEqual(self.client.post("/api/faqs/", {"question": "x", "answer": "y"}).status_code, 401)

    def test_contact_request_public_create_admin_manage(self):
        response = self.client.post(
            "/api/contact-requests/",
            {"name": "Ziyaretçi", "email": "z@example.com", "topic": "demo", "message": "Demo istiyorum lütfen", "status": "resolved"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["status"], "new")
        self.assertEqual(self.client.get("/api/contact-requests/").status_code, 401)

        self.login_as()
        self.assertEqual(self.client.get("/api/contact-requests/").status_code, 403)

        self.login_as("admin@example.com")
        request_id = ContactRequest.objects.get().id
        response = self.client.patch(f"/api/contact-requests/{request_id}/", {"status": "resolved"}, format="json")
        self.assertEqual(response.data["status"], "resolved")
        self.assertEqual(self.client.delete(f"/api/contact-requests/{request_id}/").status_code, 204)

    def test_admin_user_management(self):
        self.login_as()
        self.assertEqual(self.client.get("/api/admin/users/").status_code, 403)
        self.login_as("admin@example.com")
        self.assertEqual(self.client.get("/api/admin/users/").data["count"], 2)
        response = self.client.post(
            "/api/admin/users/", {"email": "yeni@example.com", "password": "Guclu.Sifre123", "first_name": "Yeni"}, format="json"
        )
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Family.objects.filter(owner__email="yeni@example.com").exists())
        user_id = response.data["id"]
        self.assertEqual(self.client.patch(f"/api/admin/users/{user_id}/", {"is_active": False}, format="json").status_code, 200)
        self.assertEqual(self.client.delete(f"/api/admin/users/{user_id}/").status_code, 204)
        self.assertEqual(self.client.delete(f"/api/admin/users/{self.admin.id}/").status_code, 400)
        self.assertEqual(self.client.get("/api/admin/stats/").data["users"], 2)

    def test_threat_source_blocks_listed_domain(self):
        self.login_as("admin@example.com")
        response = self.client.post(
            "/api/threat-sources/",
            {"name": "Test", "category": "phishing", "domains": "kotu-site.com\nHTTPS://Diger.net"},
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["domain_count"], 2)
        self.client.credentials()
        self.assertNotIn("domains", self.client.get("/api/threat-sources/").data["results"][0])
        response = self.client.post("/api/analyze/", {"domain": "giris.kotu-site.com"}, format="json")
        self.assertEqual(response.data["action"], "block")
        self.assertEqual(response.data["category"], "phishing")
        self.assertEqual(ThreatSource.objects.count(), 1)
