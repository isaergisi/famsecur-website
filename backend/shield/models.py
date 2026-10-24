from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from .classifier import ALL_CATEGORIES, CATEGORY_LABELS

CATEGORY_CHOICES = [(key, label) for key, label in CATEGORY_LABELS.items()]


def default_categories():
    return list(ALL_CATEGORIES)


class Family(models.Model):
    """Bir ebeveyn hesabının koruduğu ev. Cihazlar, politika ve olaylar aileye bağlıdır."""

    owner = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="family")
    name = models.CharField("aile adı", max_length=80)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "aile"
        verbose_name_plural = "aileler"

    def __str__(self) -> str:
        return self.name

    @classmethod
    def create_with_defaults(cls, owner, name):
        family = cls.objects.create(owner=owner, name=name)
        Policy.objects.create(family=family)
        return family


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
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        constraints = [models.UniqueConstraint(fields=["family", "name"], name="unique_device_name_per_family")]

    def __str__(self) -> str:
        return self.name


class WhitelistEntry(models.Model):
    """Ebeveynin yanlış engelleri düzeltmek için izin verdiği alan adı (alt alan adları dahil)."""

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


class BlockEvent(models.Model):
    """Gizlilik ilkesi gereği yalnızca ENGELLENEN istekler kaydedilir; izin verilen trafik tutulmaz."""

    family = models.ForeignKey(Family, on_delete=models.CASCADE, related_name="events")
    device = models.ForeignKey(Device, on_delete=models.SET_NULL, null=True, blank=True, related_name="events")
    domain = models.CharField(max_length=253)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
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
    domains = models.TextField("alan adları (satır başına bir)", blank=True)
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "tehdit kaynağı"
        verbose_name_plural = "tehdit kaynakları"

    def __str__(self) -> str:
        return self.name

    def domain_list(self) -> list[str]:
        return [line.strip().lower() for line in self.domains.splitlines() if line.strip()]

    @classmethod
    def active_domain_map(cls) -> dict[str, str]:
        mapping: dict[str, str] = {}
        for source in cls.objects.filter(is_active=True):
            for domain in source.domain_list():
                mapping.setdefault(domain, source.category)
        return mapping
