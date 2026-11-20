from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from .classifier import ALL_CATEGORIES, CATEGORY_LABELS

CATEGORY_CHOICES = [(key, label) for key, label in CATEGORY_LABELS.items()]
# Olaylarda kategoriye ek olarak ailenin kendi engel listesi de görünebilir.
MANUAL_CATEGORY = "manual"
EVENT_CATEGORY_CHOICES = CATEGORY_CHOICES + [(MANUAL_CATEGORY, "Engel listeniz")]


def default_categories():
    return list(ALL_CATEGORIES)


class Family(models.Model):
    """Bir ebeveyn hesabının koruduğu ev. Cihazlar, politika ve olaylar aileye bağlıdır."""

    class Plan(models.TextChoices):
        # Kimlikler (izleme/tam) eski kayıtlarla uyum için korunur; görünen adlar değişti.
        MONITOR = "izleme", "Başlangıç"
        FULL = "tam", "Ebeveyn"
        PLUS = "plus", "Aile Plus"

    class BillingPeriod(models.TextChoices):
        MONTHLY = "aylik", "Aylık"
        YEARLY = "yillik", "Yıllık"

    owner = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="family")
    name = models.CharField("aile adı", max_length=80)
    plan = models.CharField("paket", max_length=10, choices=Plan.choices, default=Plan.FULL)
    billing_period = models.CharField(
        "ödeme dönemi", max_length=10, choices=BillingPeriod.choices, default=BillingPeriod.MONTHLY
    )
    # İptal talebi: hizmet ödenmiş dönemin sonuna kadar sürer, sonraki dönem için ücret alınmaz.
    cancel_requested_at = models.DateTimeField("iptal talebi", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "aile"
        verbose_name_plural = "aileler"

    def __str__(self) -> str:
        return self.name

    @classmethod
    def create_with_defaults(cls, owner, name, plan=Plan.FULL, billing_period=BillingPeriod.MONTHLY):
        family = cls.objects.create(owner=owner, name=name, plan=plan, billing_period=billing_period)
        Policy.objects.create(family=family)
        return family

    # Paket kuralları tek yerde: karar motoru, API ve panel bunları kullanır.
    @property
    def auto_blocks(self) -> bool:
        """Başlangıç paketinde otomatik engel yoktur; yalnızca ailenin engel listesi uygulanır."""
        return self.plan != self.Plan.MONITOR

    @property
    def shows_devices(self) -> bool:
        """Başlangıç paketinde isteğin hangi cihazdan geldiği kaydedilmez."""
        return self.plan != self.Plan.MONITOR

    @property
    def daily_summary_enabled(self) -> bool:
        """Günlük özet yalnızca Aile Plus'ta ve açık rıza geri alınmamışsa çalışır."""
        if self.plan != self.Plan.PLUS:
            return False
        return ConsentRecord.objects.filter(
            user_id=self.owner_id, kind=ConsentRecord.Kind.PLUS_SUMMARY, withdrawn_at__isnull=True
        ).exists()


class Policy(models.Model):
    """Ailenin koruma politikası: hangi kategoriler, hangi eşikte, nasıl engellenir."""

    class Mode(models.TextChoices):
        SILENT = "silent", "Sessiz engel"
        WARNING = "warning", "Uyarı sayfası"

    family = models.OneToOneField(Family, on_delete=models.CASCADE, related_name="policy")
    risk_threshold = models.PositiveSmallIntegerField(
        "risk eşiği", default=70, validators=[MinValueValidator(30), MaxValueValidator(100)]
    )
    enforcement_mode = models.CharField(max_length=10, choices=Mode.choices, default=Mode.SILENT)
    enabled_categories = models.JSONField(default=default_categories)
    retention_days = models.PositiveSmallIntegerField(
        "olay saklama süresi (gün)", default=30, validators=[MinValueValidator(1), MaxValueValidator(365)]
    )
    # Hiçbir listede olmayan ama yapay zekâ risk puanı çok yüksek olan siteleri de engeller (Ebeveyn ve Aile Plus).
    ai_auto_block = models.BooleanField("yapay zekâ ile otomatik engel", default=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "politika"
        verbose_name_plural = "politikalar"

    def __str__(self) -> str:
        return f"{self.family} politikası"


class Device(models.Model):
    class DeviceType(models.TextChoices):
        PHONE = "phone", "Telefon"
        TABLET = "tablet", "Tablet"
        COMPUTER = "computer", "Bilgisayar"
        CONSOLE = "console", "Oyun konsolu"
        TV = "tv", "Akıllı TV"
        OTHER = "other", "Diğer"

    family = models.ForeignKey(Family, on_delete=models.CASCADE, related_name="devices")
    name = models.CharField("cihaz adı", max_length=60)
    device_type = models.CharField(max_length=10, choices=DeviceType.choices, default=DeviceType.PHONE)
    member_name = models.CharField("kullanan aile üyesi", max_length=60, blank=True)
    mac_address = models.CharField(max_length=17, blank=True)
    is_protected = models.BooleanField("koruma açık", default=True)
    # Aile Plus günlük özetine dahil mi? 18 yaşından büyük biri kullanıyorsa onun bilgisi olmadan açılmamalı.
    in_daily_summary = models.BooleanField("günlük özete dahil", default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        constraints = [models.UniqueConstraint(fields=["family", "name"], name="unique_device_name_per_family")]

    def __str__(self) -> str:
        return self.name


class WhitelistEntry(models.Model):
    """Ebeveynin yanlış engelleri düzeltmek için izin verdiği alan adı (alt alan adları dâhil)."""

    family = models.ForeignKey(Family, on_delete=models.CASCADE, related_name="whitelist")
    domain = models.CharField(max_length=253)
    note = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["domain"]
        verbose_name = "beyaz liste kaydı"
        verbose_name_plural = "beyaz liste"
        constraints = [models.UniqueConstraint(fields=["family", "domain"], name="unique_whitelist_domain_per_family")]

    def __str__(self) -> str:
        return self.domain


class BlockEntry(models.Model):
    """Ebeveynin elle engellediği alan adı (alt alan adları dâhil). Her pakette kullanılabilir."""

    family = models.ForeignKey(Family, on_delete=models.CASCADE, related_name="blocklist")
    domain = models.CharField(max_length=253)
    note = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["domain"]
        verbose_name = "engel listesi kaydı"
        verbose_name_plural = "engel listesi"
        constraints = [models.UniqueConstraint(fields=["family", "domain"], name="unique_blocklist_domain_per_family")]

    def __str__(self) -> str:
        return self.domain


class BlockEvent(models.Model):
    """Yalnızca riskli bulunan istekler kaydedilir: engellenenler ve Başlangıç paketinde engellenmeden görülenler."""

    class Action(models.TextChoices):
        BLOCKED = "blocked", "Engellendi"
        OBSERVED = "observed", "Engellenmedi, kaydedildi"

    family = models.ForeignKey(Family, on_delete=models.CASCADE, related_name="events")
    device = models.ForeignKey(Device, on_delete=models.SET_NULL, null=True, blank=True, related_name="events")
    domain = models.CharField(max_length=253)
    category = models.CharField(max_length=20, choices=EVENT_CATEGORY_CHOICES)
    action = models.CharField(max_length=10, choices=Action.choices, default=Action.BLOCKED)
    score = models.PositiveSmallIntegerField()
    reasons = models.JSONField(default=list)
    enforcement_mode = models.CharField(max_length=10, choices=Policy.Mode.choices)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "engel olayı"
        verbose_name_plural = "engel olayları"

    def __str__(self) -> str:
        return f"{self.domain} ({self.category})"


class ThreatSource(models.Model):
    """Yöneticinin yönettiği tehdit istihbaratı kaynağı (ör. USOM) ve ek engel alan adları."""

    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.TextField(blank=True)
    source_url = models.URLField(blank=True)
    # Satır başına bir alan adı; isteğe bağlı olarak kayda özel kategori: "ornek-bahis.com gambling"
    domains = models.TextField("alan adları (satır başına bir)", blank=True)
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)
    # Kaynak adresinden otomatik güncelleme (python manage.py refresh_sources veya paneldeki düğme)
    auto_update = models.BooleanField("adresten otomatik güncelle", default=False)
    last_fetched_at = models.DateTimeField("son başarılı güncelleme", null=True, blank=True)
    last_fetch_count = models.PositiveIntegerField("son güncellemede gelen alan adı", null=True, blank=True)
    last_fetch_error = models.TextField("son güncelleme hatası", blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "tehdit kaynağı"
        verbose_name_plural = "tehdit kaynakları"

    def __str__(self) -> str:
        return self.name

    def domain_entries(self) -> list[tuple[str, str]]:
        """(alan adı, kategori) çiftleri. Satırda kategori yazmıyorsa kaynağın kategorisi geçerlidir."""
        entries = []
        for line in self.domains.splitlines():
            parts = line.strip().lower().split()
            if not parts:
                continue
            category = parts[1] if len(parts) > 1 and parts[1] in CATEGORY_LABELS else self.category
            entries.append((parts[0], category))
        return entries

    def domain_list(self) -> list[str]:
        return [domain for domain, _ in self.domain_entries()]

    _map_cache: tuple = (None, {})

    @classmethod
    def active_domain_map(cls) -> dict[str, str]:
        """Aktif kaynaklardaki alan adı → kategori. Yüz binlerce kayıt olabileceği için kaynaklar
        değişmedikçe (sayı veya son güncelleme zamanı) önbellekten döner."""
        active = cls.objects.filter(is_active=True)
        key = tuple(active.order_by("id").values_list("id", "updated_at"))
        cached_key, cached_map = cls._map_cache
        if cached_key == key:
            return cached_map
        mapping: dict[str, str] = {}
        for source in active:
            for domain, category in source.domain_entries():
                mapping.setdefault(domain, category)
        cls._map_cache = (key, mapping)
        return mapping


class ConsentRecord(models.Model):
    """Kayıtta ve sonrasında verilen onayların kanıtı: hangi metin, hangi sürüm, ne zaman.

    IP adresi gibi ek veriler bilinçli olarak tutulmaz (veri en aza indirme).
    """

    class Kind(models.TextChoices):
        CONTRACT = "sozlesme", "Ön bilgilendirme formu ve mesafeli satış sözleşmesi"
        PRIVACY_NOTICE = "aydinlatma", "KVKK aydınlatma metninin okunması"
        TRIAL_TO_PAID = "deneme_ucretli", "Deneme sonunda ücretli aboneliğin başlaması"
        HOUSEHOLD = "hane", "Hane bireylerinin bilgilendirildiği beyanı"
        PLUS_SUMMARY = "plus_ozet", "Aile Plus günlük özet açık rızası"
        MARKETING = "ticari_ileti", "Kampanya ve duyuru iletileri"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="consents")
    kind = models.CharField(max_length=20, choices=Kind.choices)
    version = models.CharField("metin sürümü", max_length=20)
    accepted_at = models.DateTimeField(auto_now_add=True)
    withdrawn_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-accepted_at"]
        verbose_name = "onay kaydı"
        verbose_name_plural = "onay kayıtları"

    def __str__(self) -> str:
        return f"{self.user} · {self.get_kind_display()}"


class DailyDomainStat(models.Model):
    """Aile Plus günlük özeti: gün, cihaz ve site başına sorgu sayısı.

    Ham DNS kaydı tutulmaz; yalnızca kayıtlı alan adı (ör. instagram.com) bazında sayı saklanır.
    """

    family = models.ForeignKey(Family, on_delete=models.CASCADE, related_name="daily_stats")
    device = models.ForeignKey(Device, on_delete=models.CASCADE, null=True, blank=True, related_name="daily_stats")
    day = models.DateField(db_index=True)
    domain = models.CharField(max_length=253)
    count = models.PositiveIntegerField(default=0)
    night_count = models.PositiveIntegerField("00.00-06.00 arası", default=0)

    class Meta:
        ordering = ["-day", "-count"]
        verbose_name = "günlük site sayısı"
        verbose_name_plural = "günlük site sayıları"
        constraints = [
            models.UniqueConstraint(fields=["family", "device", "day", "domain"], name="unique_daily_stat"),
        ]
