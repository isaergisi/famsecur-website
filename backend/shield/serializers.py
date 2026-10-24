import re

from rest_framework import serializers

from .classifier import ALL_CATEGORIES, CATEGORY_LABELS, normalize_domain
from .models import BlockEvent, Device, Family, Policy, ThreatSource, WhitelistEntry

DOMAIN_RE = re.compile(r"^(?=.{3,253}$)([a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z][a-z0-9-]{0,62}$")
MAC_RE = re.compile(r"^([0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}$")


def clean_domain(value: str) -> str:
    domain = normalize_domain(value)
    if domain.startswith("*."):
        domain = domain[2:]
    if not DOMAIN_RE.match(domain):
        raise serializers.ValidationError("Geçerli bir alan adı girin (ör. ornek.com).")
    return domain


class PolicySerializer(serializers.ModelSerializer):
    enabled_categories = serializers.ListField(child=serializers.ChoiceField(choices=ALL_CATEGORIES))
    category_labels = serializers.SerializerMethodField()

    class Meta:
        model = Policy
        fields = ["risk_threshold", "enforcement_mode", "enabled_categories", "retention_days", "updated_at", "category_labels"]
        read_only_fields = ["updated_at"]
        extra_kwargs = {
            "risk_threshold": {"error_messages": {
                "min_value": "Risk eşiği en az 30 olmalı; daha düşük değerler masum siteleri engeller.",
                "max_value": "Risk eşiği en fazla 100 olabilir.",
            }},
        }

    def get_category_labels(self, obj):
        return CATEGORY_LABELS

    def validate_enabled_categories(self, value):
        value = list(dict.fromkeys(value))
        # İş kuralı: oltalama ve zararlı yazılım koruması tüm ailelerde zorunludur.
        missing = [c for c in ("phishing", "malware") if c not in value]
        if missing:
            raise serializers.ValidationError(
                "Dolandırıcılık ve kötü amaçlı yazılım koruması kapatılamaz."
            )
        return value


class FamilySerializer(serializers.ModelSerializer):
    policy = PolicySerializer(read_only=True)
    device_count = serializers.IntegerField(source="devices.count", read_only=True)
    whitelist_count = serializers.IntegerField(source="whitelist.count", read_only=True)

    class Meta:
        model = Family
        fields = ["id", "name", "created_at", "policy", "device_count", "whitelist_count"]
        read_only_fields = ["id", "created_at"]


class DeviceSerializer(serializers.ModelSerializer):
    device_type_label = serializers.CharField(source="get_device_type_display", read_only=True)
    block_count = serializers.IntegerField(source="events.count", read_only=True)

    class Meta:
        model = Device
        fields = [
            "id", "name", "device_type", "device_type_label", "member_name",
            "mac_address", "is_protected", "created_at", "block_count",
        ]
        read_only_fields = ["id", "created_at"]

    def validate_name(self, value):
        family = self.context["family"]
        qs = family.devices.filter(name__iexact=value.strip())
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Bu adla kayıtlı bir cihazınız zaten var.")
        return value.strip()

    def validate_mac_address(self, value):
        if value and not MAC_RE.match(value):
            raise serializers.ValidationError("MAC adresi AA:BB:CC:DD:EE:FF biçiminde olmalı.")
        return value.upper().replace("-", ":")


class WhitelistEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = WhitelistEntry
        fields = ["id", "domain", "note", "created_at"]
        read_only_fields = ["id", "created_at"]

    def validate_domain(self, value):
        domain = clean_domain(value)
        family = self.context["family"]
        qs = family.whitelist.filter(domain=domain)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Bu alan adı zaten beyaz listede.")
        return domain


class BlockEventSerializer(serializers.ModelSerializer):
    device_name = serializers.CharField(source="device.name", read_only=True, default=None)
    category_label = serializers.CharField(source="get_category_display", read_only=True)

    class Meta:
        model = BlockEvent
        fields = [
            "id", "domain", "category", "category_label", "score", "reasons",
            "enforcement_mode", "device", "device_name", "created_at",
        ]
        read_only_fields = fields


class CheckDomainSerializer(serializers.Serializer):
    domain = serializers.CharField(max_length=2048)
    device = serializers.IntegerField(required=False, allow_null=True)

    def validate_domain(self, value):
        return clean_domain(value)

    def validate_device(self, value):
        if value is None:
            return None
        try:
            return self.context["family"].devices.get(pk=value)
        except Device.DoesNotExist:
            raise serializers.ValidationError("Seçilen cihaz bu aileye ait değil.")


class PublicAnalyzeSerializer(serializers.Serializer):
    domain = serializers.CharField(max_length=2048)

    def validate_domain(self, value):
        return clean_domain(value)


class ThreatSourceSerializer(serializers.ModelSerializer):
    category_label = serializers.CharField(source="get_category_display", read_only=True)
    domain_count = serializers.SerializerMethodField()

    class Meta:
        model = ThreatSource
        fields = [
            "id", "name", "category", "category_label", "description", "source_url",
            "domains", "domain_count", "is_active", "updated_at",
        ]
        read_only_fields = ["id", "updated_at"]

    def get_domain_count(self, obj):
        return len(obj.domain_list())

    def validate_domains(self, value):
        cleaned, invalid = [], []
        for line in value.splitlines():
            if not line.strip():
                continue
            try:
                cleaned.append(clean_domain(line))
            except serializers.ValidationError:
                invalid.append(line.strip())
        if invalid:
            raise serializers.ValidationError(f"Geçersiz alan adları: {', '.join(invalid[:5])}")
        return "\n".join(dict.fromkeys(cleaned))

    def to_representation(self, instance):
        data = super().to_representation(instance)
        user = self.context["request"].user
        if not (user.is_authenticated and user.is_admin):
            # Alan adı listesi yalnızca yöneticilere gösterilir.
            data.pop("domains")
        return data
