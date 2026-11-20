"""Üç paket, engel listesi, onay kayıtları, iptal ve Aile Plus günlük özeti."""

from datetime import datetime, timedelta
from unittest import mock

from django.utils import timezone
from rest_framework import status

from shield.models import BlockEvent, ConsentRecord, DailyDomainStat, Family
from shield.summary import record_visit

from .test_api import REQUIRED_CONSENTS, BaseAPITest


class RegistrationConsentTests(BaseAPITest):
    def test_required_consents_are_enforced(self):
        response = self.client.post("/api/auth/register/", {
            "email": "a@example.com", "password": "Guclu.Sifre123", "first_name": "A", "plan": "tam",
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        for field in ("accept_contract", "accept_privacy_notice", "accept_trial_to_paid", "household_ack"):
            self.assertIn(field, response.data["errors"])

    def test_starter_plan_does_not_need_household_ack(self):
        response = self.register(plan="izleme", household_ack=False)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_plus_requires_explicit_consent_and_records_versions(self):
        response = self.register(plan="plus")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("plus_consent", response.data["errors"])
        response = self.register(plan="plus", plus_consent=True, billing_period="yillik")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        family = Family.objects.get(owner__email="veli@example.com")
        self.assertEqual(family.billing_period, Family.BillingPeriod.YEARLY)
        kinds = set(ConsentRecord.objects.filter(user=family.owner).values_list("kind", flat=True))
        self.assertIn(ConsentRecord.Kind.PLUS_SUMMARY, kinds)
        self.assertNotIn(ConsentRecord.Kind.MARKETING, kinds)  # önceden işaretli değil
        self.assertTrue(family.daily_summary_enabled)

    def test_plus_consent_is_ignored_for_other_plans(self):
        self.register(plan="tam", plus_consent=True)
        user = Family.objects.get(owner__email="veli@example.com").owner
        self.assertFalse(user.consents.filter(kind=ConsentRecord.Kind.PLUS_SUMMARY).exists())


class PackageRuleTests(BaseAPITest):
    def setup_family(self, plan, **extra):
        self.register(plan=plan, **extra)
        self.login_as()
        family = Family.objects.get(owner__email="veli@example.com")
        device = self.client.post("/api/devices/", {"name": "Tablet"}, format="json").data["id"]
        return family, device

    def check(self, domain, device=None):
        return self.client.post("/api/check/", {"domain": domain, "device": device}, format="json")

    def test_starter_records_risky_site_without_blocking_or_device(self):
        family, device = self.setup_family("izleme")
        response = self.check("casino777.xyz", device)
        self.assertEqual(response.data["decision"]["action"], "allow")
        event = BlockEvent.objects.get(family=family)
        self.assertEqual(event.action, BlockEvent.Action.OBSERVED)
        self.assertIsNone(event.device)

    def test_starter_blocks_manual_entries(self):
        family, device = self.setup_family("izleme")
        self.assertEqual(self.client.post("/api/blocklist/", {"domain": "ornek-oyun.com"}, format="json").status_code, 201)
        response = self.check("www.ornek-oyun.com", device)
        self.assertEqual(response.data["decision"]["action"], "block")
        self.assertEqual(response.data["decision"]["source"], "manual_list")
        event = BlockEvent.objects.get(family=family)
        self.assertEqual((event.action, event.category, event.device), (BlockEvent.Action.BLOCKED, "manual", None))

    def test_parent_plan_blocks_automatically_with_device(self):
        family, device = self.setup_family("tam")
        response = self.check("casino777.xyz", device)
        self.assertEqual(response.data["decision"]["action"], "block")
        self.assertEqual(BlockEvent.objects.get(family=family).device_id, device)

    def test_whitelist_beats_blocklist(self):
        self.setup_family("tam")
        self.client.post("/api/blocklist/", {"domain": "ornek.com"}, format="json")
        self.client.post("/api/whitelist/", {"domain": "sub.ornek.com"}, format="json")
        self.assertEqual(self.check("sub.ornek.com").data["decision"]["action"], "allow")
        self.assertEqual(self.check("diger.ornek.com").data["decision"]["action"], "block")
        conflict = self.client.post("/api/blocklist/", {"domain": "sub.ornek.com"}, format="json")
        self.assertEqual(conflict.status_code, 400)

    def test_ai_auto_block_only_outside_starter(self):
        self.setup_family("izleme")
        response = self.client.patch("/api/policy/", {"ai_auto_block": True}, format="json")
        self.assertEqual(response.status_code, 400)

    def test_ai_auto_block_uses_high_threshold(self):
        self.setup_family("tam")
        self.client.patch("/api/policy/", {"ai_auto_block": True}, format="json")
        high = {"risk": 92, "category": "gambling", "category_label": "Kumar / bahis", "warning": True, "analyzed_domain": "x.com"}
        low = dict(high, risk=70)
        with mock.patch("shield.services.ai_prediction", return_value=high):
            self.assertEqual(self.check("tamamenyeni-site.com").data["decision"]["source"], "ai")
        with mock.patch("shield.services.ai_prediction", return_value=low):
            self.assertEqual(self.check("baskayeni-site.com").data["decision"]["action"], "allow")


class SubscriptionAndConsentTests(BaseAPITest):
    def test_cancel_and_undo_from_panel(self):
        self.register()
        self.login_as()
        self.assertIsNotNone(self.client.post("/api/subscription/cancel/").data["cancel_requested_at"])
        self.assertIsNone(self.client.delete("/api/subscription/cancel/").data["cancel_requested_at"])

    def test_withdrawing_plus_consent_deletes_summary_data(self):
        self.register(plan="plus", plus_consent=True)
        self.login_as()
        family = Family.objects.get(owner__email="veli@example.com")
        self.assertTrue(record_visit(family, "www.youtube.com"))
        self.assertEqual(self.client.get("/api/daily-summary/").status_code, 200)
        self.client.post("/api/consents/", {"kind": "plus_ozet", "give": False}, format="json")
        self.assertFalse(DailyDomainStat.objects.filter(family=family).exists())
        self.assertFalse(record_visit(family, "www.youtube.com"))
        response = self.client.get("/api/daily-summary/")
        self.assertEqual((response.status_code, response.data["code"]), (403, "consent"))
        self.client.post("/api/consents/", {"kind": "plus_ozet", "give": True}, format="json")
        self.assertEqual(self.client.get("/api/daily-summary/").status_code, 200)

    def test_contract_records_cannot_be_withdrawn(self):
        self.register()
        self.login_as()
        response = self.client.post("/api/consents/", {"kind": "sozlesme", "give": False}, format="json")
        self.assertEqual(response.status_code, 400)

    def test_summary_is_plus_only(self):
        self.register(plan="tam")
        self.login_as()
        response = self.client.get("/api/daily-summary/")
        self.assertEqual((response.status_code, response.data["code"]), (403, "plan"))


class DailySummaryTests(BaseAPITest):
    def setUp(self):
        super().setUp()
        self.register(plan="plus", plus_consent=True)
        self.login_as()
        self.family = Family.objects.get(owner__email="veli@example.com")
        self.tablet = self.family.devices.create(name="Tablet")
        self.adult = self.family.devices.create(name="Babanın telefonu", in_daily_summary=False)

    def test_summary_groups_sites_skips_background_and_excluded_devices(self):
        tz = timezone.get_current_timezone()
        night = datetime(2026, 11, 19, 1, 30, tzinfo=tz)
        day = datetime(2026, 11, 19, 15, 0, tzinfo=tz)
        for name in ("i.instagram.com", "www.instagram.com", "scontent.cdninstagram.com", "fonts.gstatic.com"):
            record_visit(self.family, name, self.tablet, day)
        record_visit(self.family, "www.youtube.com", self.tablet, night)
        record_visit(self.family, "www.youtube.com", self.adult, day)
        summary = self.client.get("/api/daily-summary/?day=2026-11-19").data
        sites = {s["domain"]: s for s in summary["top_sites"]}
        self.assertEqual(set(sites), {"instagram.com", "youtube.com"})
        self.assertEqual(sites["instagram.com"]["count"], 2)
        self.assertEqual(sites["instagram.com"]["category_label"], "Sosyal medya")
        self.assertEqual(summary["night_total"], 1)
        self.assertEqual(summary["by_device"][0]["device"], "Tablet")

    def test_new_sites_and_retention(self):
        today = timezone.localdate()
        DailyDomainStat.objects.create(family=self.family, day=today - timedelta(days=1), domain="youtube.com", count=3)
        DailyDomainStat.objects.create(family=self.family, day=today, domain="youtube.com", count=1)
        DailyDomainStat.objects.create(family=self.family, day=today, domain="roblox.com", count=1)
        DailyDomainStat.objects.create(family=self.family, day=today - timedelta(days=40), domain="eski.com", count=1)
        summary = self.client.get("/api/daily-summary/").data
        self.assertEqual([s["domain"] for s in summary["new_sites"]], ["roblox.com"])
        self.assertFalse(DailyDomainStat.objects.filter(domain="eski.com").exists())
