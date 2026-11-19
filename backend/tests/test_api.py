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
        self.assertEqual(family.plan, Family.Plan.FULL)

    def test_register_stores_selected_plan_and_rejects_unknown(self):
        self.assertEqual(self.register(plan="izleme").status_code, status.HTTP_201_CREATED)
        self.assertEqual(Family.objects.get(owner__email="veli@example.com").plan, Family.Plan.MONITOR)
        response = self.register(email="baska@example.com", plan="altin")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("plan", response.data["errors"])

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
        stats = self.client.get("/api/events/stats/").data
        self.assertEqual(stats["total"], 3)
        weekly = stats["weekly"]
        self.assertEqual(weekly["total"], 3)
        self.assertEqual(weekly["previous_total"], 0)
        self.assertEqual(len(weekly["days"]), 7)
        self.assertEqual(weekly["days"][-1]["count"], 3)
        self.assertEqual(weekly["top_category"], {"category": "gambling", "count": 2})
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
        self.assertEqual(response.data["source"], "signals")
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
        self.assertFalse(User.objects.get(pk=user_id).is_active)
        # Yönetici e-posta, şifre veya rol değiştiremez; PUT kapalı.
        for field, value in [("email", "baska@example.com"), ("password", "Baska.Sifre123"), ("role", "admin")]:
            response = self.client.patch(f"/api/admin/users/{user_id}/", {field: value}, format="json")
            self.assertEqual(response.status_code, 400, field)
            self.assertIn(field, response.data["errors"])
        self.assertTrue(User.objects.get(pk=user_id).check_password("Guclu.Sifre123"))
        self.assertEqual(self.client.put(f"/api/admin/users/{user_id}/", {"is_active": True}, format="json").status_code, 405)
        self.assertEqual(self.client.delete(f"/api/admin/users/{user_id}/").status_code, 204)
        self.assertEqual(self.client.delete(f"/api/admin/users/{self.admin.id}/").status_code, 400)
        self.assertEqual(self.client.get("/api/admin/stats/").data["users"], 2)

    def test_admin_blocked_domains_list_search_and_pages(self):
        self.login_as()
        self.assertEqual(self.client.get("/api/admin/blocked-domains/").status_code, 403)
        # Ebeveyn aynı listeyi salt okunur görür; kaynakları değiştiremez veya güncelleyemez
        self.assertEqual(self.client.get("/api/blocked-domains/").status_code, 200)
        self.assertEqual(self.client.post("/api/blocked-domains/", {}).status_code, 405)
        sources = self.client.get("/api/threat-sources/").data["results"]
        self.assertTrue(sources)
        self.assertNotIn("last_fetch_error", sources[0])
        self.assertEqual(self.client.patch(f"/api/threat-sources/{sources[0]['id']}/", {"is_active": False}, format="json").status_code, 403)
        self.assertEqual(self.client.post(f"/api/threat-sources/{sources[0]['id']}/refresh/").status_code, 403)
        self.client.credentials()
        self.assertEqual(self.client.get("/api/blocked-domains/").status_code, 401)
        self.login_as()
        self.login_as("admin@example.com")
        ThreatSource.objects.create(name="Test USOM", category="phishing", domains="sahte-banka-giris.com")
        data = self.client.get("/api/admin/blocked-domains/").data
        self.assertGreater(data["count"], 36000)
        self.assertEqual(len(data["results"]), 50)
        self.assertIn("Test USOM", [s["name"] for s in data["sources"]])
        data = self.client.get("/api/admin/blocked-domains/", {"search": "sahte-banka"}).data
        self.assertEqual(data["count"], 1)
        self.assertEqual(data["results"][0], {
            "domain": "sahte-banka-giris.com", "category": "phishing",
            "category_label": data["results"][0]["category_label"], "source": "Test USOM",
        })
        data = self.client.get("/api/admin/blocked-domains/", {"category": "phishing", "source": "Test USOM"}).data
        self.assertEqual(data["count"], 1)
        self.assertEqual(self.client.get("/api/admin/blocked-domains/", {"page": 2}).status_code, 200)

    def test_blocked_domains_category_is_per_record_across_sources(self):
        self.login_as("admin@example.com")
        response = self.client.post("/api/threat-sources/", {
            "name": "Karma liste", "category": "phishing",
            "domains": "sahte-banka.com\nkacak-bahis-giris.com gambling",
        }, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(self.client.post("/api/threat-sources/", {
            "name": "Hatalı", "category": "phishing", "domains": "ornek.com uydurma",
        }, format="json").status_code, 400)
        # "Kumar" filtresi tüm listelerdeki kumar kayıtlarını getirir.
        data = self.client.get("/api/admin/blocked-domains/", {"category": "gambling", "search": "kacak-bahis"}).data
        self.assertEqual([(r["domain"], r["source"]) for r in data["results"]], [("kacak-bahis-giris.com", "Karma liste")])
        data = self.client.get("/api/admin/blocked-domains/", {"category": "phishing", "source": "Karma liste"}).data
        self.assertEqual([r["domain"] for r in data["results"]], ["sahte-banka.com"])
        # Karar motoru da kayda özel kategoriyi kullanır.
        result = self.client.post("/api/analyze/", {"domain": "kacak-bahis-giris.com"}, format="json").data
        self.assertEqual(result["category"], "gambling")

    def test_refresh_sources_from_url(self):
        import io
        import json
        from unittest import mock

        from django.core.management import call_command

        usom = {"pageCount": 1, "models": [
            {"url": "https://giris.sahte-edevlet.com/login", "desc": "PH", "criticality_level": 2},
            {"url": "zararli-indir.net", "desc": "MD", "criticality_level": 1},
            {"url": "dusuk-kritik.com", "desc": "PH", "criticality_level": 9},
        ]}
        register = "<Rejestr><PozycjaRejestru><AdresDomeny>yeni-kasyno.pl</AdresDomeny></PozycjaRejestru></Rejestr>"

        def fake_get(url, timeout):
            return json.dumps(usom).encode() if "siberguvenlik" in url else register.encode()

        phishing = ThreatSource.objects.create(
            name="USOM Zararlı Bağlantılar", category="phishing", domains="eski-kayit.com",
            source_url="https://www.usom.gov.tr/adres", auto_update=True,
        )
        official = ThreatSource.objects.create(
            name="Resmî Kumar Alan Adı Havuzu", category="gambling",
            source_url="https://hazard.mf.gov.pl/api/Register", auto_update=True,
        )
        manual = ThreatSource.objects.create(name="Elle", category="malware", domains="elle.com", source_url="https://x.example")
        with mock.patch("shield.fetchers._get", fake_get):
            call_command("refresh_sources", stdout=io.StringIO())
        phishing.refresh_from_db(); official.refresh_from_db(); manual.refresh_from_db()
        # USOM: yalnızca kaynağın kategorisi ve kritiklik 1-4; eski kayıtlar korunur
        self.assertEqual(phishing.domain_list(), ["eski-kayit.com", "giris.sahte-edevlet.com"])
        self.assertEqual(phishing.last_fetch_count, 1)
        self.assertIsNotNone(phishing.last_fetched_at)
        self.assertEqual(official.domain_list(), ["yeni-kasyno.pl"])
        self.assertEqual(manual.domain_list(), ["elle.com"])  # otomatik güncelleme kapalı

        # Panel düğmesi: başarısız çekmede eski liste korunur, hata kaydedilir
        self.login_as("admin@example.com")
        # Zaman aşımında bir kez yeniden dener
        calls = []

        def flaky(url, timeout):
            calls.append(url)
            if len(calls) == 1:
                raise TimeoutError("The read operation timed out")
            return register.encode()

        with mock.patch("shield.fetchers._download", flaky), mock.patch("shield.fetchers.RETRY_DELAY", 0):
            self.assertEqual(self.client.post(f"/api/threat-sources/{official.id}/refresh/").status_code, 200)
        self.assertEqual(len(calls), 2)
        with mock.patch("shield.fetchers._get", side_effect=OSError("bağlantı yok")):
            response = self.client.post(f"/api/threat-sources/{official.id}/refresh/")
        self.assertEqual(response.status_code, 502)
        official.refresh_from_db()
        self.assertEqual(official.domain_list(), ["yeni-kasyno.pl"])
        self.assertIn("bağlantı yok", official.last_fetch_error)
        with mock.patch("shield.fetchers._get", return_value=b"<!DOCTYPE html><html><body>Rejestr</body></html>"):
            response = self.client.post(f"/api/threat-sources/{official.id}/refresh/")
        self.assertEqual(response.status_code, 502)
        self.assertIn("web sayfası", response.data["detail"])
        with mock.patch("shield.fetchers._get", fake_get):
            response = self.client.post(f"/api/threat-sources/{official.id}/refresh/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["last_fetch_error"], "")
        # Resmî havuz adresinden güncellenince dosya yerine bu liste gösterilir
        self.assertEqual(self.client.get("/api/admin/blocked-domains/", {"source": "Resmî Kumar Alan Adı Havuzu"}).data["count"], 1)
        self.login_as()
        self.assertEqual(self.client.post(f"/api/threat-sources/{official.id}/refresh/").status_code, 403)

    def test_refresh_ut1(self):
        import io
        import tarfile
        from unittest import mock

        from shield.fetchers import refresh_source

        def tarball(name, domains):
            buffer = io.BytesIO()
            with tarfile.open(fileobj=buffer, mode="w:gz") as archive:
                data = "\n".join(domains).encode()
                info = tarfile.TarInfo(f"{name}/domains")
                info.size = len(data)
                archive.addfile(info, io.BytesIO(data))
            return buffer.getvalue()

        archives = {
            "gambling": ["kacak-kumar.example"], "drogue": ["ot-satis.example"],
            "phishing": ["sahte-banka.example"], "malware": ["virus-indir.example", "kacak-kumar.example"],
        }

        def fake_get(url, timeout):
            return tarball(url.rsplit("/", 1)[1].split(".")[0], archives[url.rsplit("/", 1)[1].split(".")[0]])

        ut1 = ThreatSource.objects.create(name="UT1", category="gambling", source_url="https://dsi.ut-capitole.fr/blacklists/")
        with mock.patch("shield.fetchers._get", fake_get):
            self.assertEqual(refresh_source(ut1), 4)
        self.assertEqual(dict(ut1.domain_entries()), {
            "kacak-kumar.example": "gambling", "ot-satis.example": "drugs",
            "sahte-banka.example": "phishing", "virus-indir.example": "malware",
        })
        from urllib.error import HTTPError

        # Hata mesajı denenen adresi gösterir
        with mock.patch("shield.fetchers._download", side_effect=HTTPError("https://x.example/l.txt", 410, "Gone", {}, None)):
            with self.assertRaises(HTTPError):
                refresh_source(ThreatSource.objects.create(name="X", category="malware", source_url="https://x.example/l.txt"))
        self.assertIn("Denenen adres: https://x.example/l.txt", ThreatSource.objects.get(name="X").last_fetch_error)
        # Karar motoru kayıt bazlı kategoriyi kullanır (önbellek de yenilenir)
        self.assertEqual(self.client.post("/api/analyze/", {"domain": "ot-satis.example"}, format="json").data["category"], "drugs")

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
        self.assertEqual(response.data["source"], "threat_list")
        self.assertTrue(ThreatSource.objects.filter(name="Test").exists())


class AiRiskTests(BaseAPITest):
    """Eğitilmiş yapay zekâ modeli: yalnızca listede olmayan alan adlarına uyarı verir."""

    def setUp(self):
        super().setUp()
        self.register()
        self.login_as()

    def test_unknown_risky_domain_gets_ai_warning_but_is_not_blocked(self):
        response = self.client.post("/api/check/", {"domain": "hotgirlsvideo.com"}, format="json")
        self.assertEqual(response.data["decision"]["action"], "allow")  # model engellemez
        self.assertGreaterEqual(response.data["ai"]["risk"], 60)
        self.assertTrue(response.data["ai"]["warning"])
        self.assertEqual(response.data["ai"]["category"], "adult")

    def test_clean_domain_gets_low_ai_risk(self):
        response = self.client.post("/api/check/", {"domain": "https://www.google.com/search"}, format="json")
        self.assertLess(response.data["ai"]["risk"], 30)
        self.assertFalse(response.data["ai"]["warning"])

    def test_listed_or_whitelisted_domains_skip_ai(self):
        response = self.client.post("/api/check/", {"domain": "0-romancasino.com"}, format="json")
        self.assertEqual(response.data["decision"]["action"], "block")
        self.assertIsNone(response.data["ai"])
        self.client.post("/api/whitelist/", {"domain": "hotgirlsvideo.com"}, format="json")
        response = self.client.post("/api/check/", {"domain": "hotgirlsvideo.com"}, format="json")
        self.assertIsNone(response.data["ai"])
        self.assertEqual(response.data["decision"]["source"], "whitelist")

    def test_public_demo_includes_ai_prediction_for_unlisted_domains(self):
        self.client.credentials()
        data = self.client.post("/api/analyze/", {"domain": "hotgirlsvideo.com"}, format="json").data
        self.assertEqual(data["action"], "allow")
        self.assertEqual(data["source"], "none")
        self.assertTrue(data["ai"]["warning"])
        data = self.client.post("/api/analyze/", {"domain": "0-romancasino.com"}, format="json").data
        self.assertEqual(data["action"], "block")
        self.assertEqual(data["source"], "official_list")
        self.assertIsNone(data["ai"])


class DailyTaskTests(BaseAPITest):
    """Günlük bakım: 24 saati geçen kaynaklar yenilenir, süresi dolan olaylar silinir."""

    def test_refreshes_only_due_sources_and_prunes_old_events(self):
        from datetime import timedelta
        from unittest import mock

        from django.utils import timezone

        from shield import scheduler

        now = timezone.now()
        ThreatSource.objects.all().delete()  # migration'ın eklediği kaynaklar bu testi etkilemesin
        due = ThreatSource.objects.create(name="Eski", category="phishing", source_url="https://ornek.com/a.txt",
                                          auto_update=True, last_fetched_at=now - timedelta(hours=25))
        ThreatSource.objects.create(name="Taze", category="phishing", source_url="https://ornek.com/b.txt",
                                    auto_update=True, last_fetched_at=now - timedelta(hours=2))
        ThreatSource.objects.create(name="Elle", category="phishing", domains="x.com")
        with mock.patch("shield.fetchers.refresh_source", return_value=1) as refresh:
            self.assertEqual(scheduler.refresh_due_sources(now), ["Eski"])
        refresh.assert_called_once_with(due)

        self.register()
        family = Family.objects.get(owner__email="veli@example.com")
        old = BlockEvent.objects.create(family=family, domain="a.com", category="gambling", score=90,
                                        reasons=[], enforcement_mode="silent")
        BlockEvent.objects.filter(pk=old.pk).update(created_at=now - timedelta(days=family.policy.retention_days + 1))
        BlockEvent.objects.create(family=family, domain="b.com", category="gambling", score=90,
                                  reasons=[], enforcement_mode="silent")
        self.assertEqual(scheduler.prune_all_families(), 1)
        self.assertEqual(family.events.count(), 1)

    def test_scheduler_does_not_start_in_tests_or_when_disabled(self):
        from unittest import mock

        from shield import scheduler

        self.assertFalse(scheduler.should_start())
        with mock.patch.dict("os.environ", {"FAMSECUR_AUTO_UPDATE": "1"}):
            self.assertTrue(scheduler.should_start())
        with mock.patch.dict("os.environ", {"FAMSECUR_AUTO_UPDATE": "0"}):
            self.assertFalse(scheduler.should_start())


class ApiDocsTests(APITestCase):
    def test_schema_and_docs_pages_are_public(self):
        schema = self.client.get("/api/schema/")
        self.assertEqual(schema.status_code, 200)
        body = schema.content.decode()
        self.assertIn("FamSecur API", body)
        self.assertIn("/api/devices/", body)
        self.assertIn("jwtAuth", body)
        for url in ("/api/docs/", "/api/redoc/"):
            self.assertEqual(self.client.get(url).status_code, 200, url)
