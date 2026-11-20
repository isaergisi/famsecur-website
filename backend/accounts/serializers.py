from django.contrib.auth import password_validation
from django.db import transaction
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from shield.models import ConsentRecord, Family

# Sözleşme ve aydınlatma metinlerinin sürümü. Metinler değiştiğinde güncellenir; her onay bu sürümle saklanır.
LEGAL_VERSION = "2026-11-20"

from .models import User


class UserSerializer(serializers.ModelSerializer):
    family_id = serializers.IntegerField(source="family.id", read_only=True, default=None)

    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name", "role", "is_active", "date_joined", "family_id"]
        read_only_fields = ["id", "email", "role", "is_active", "date_joined", "family_id"]


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={"input_type": "password"})
    family_name = serializers.CharField(max_length=80, required=False, allow_blank=True)
    plan = serializers.ChoiceField(choices=Family.Plan.choices, required=False, default=Family.Plan.FULL)
    billing_period = serializers.ChoiceField(
        choices=Family.BillingPeriod.choices, required=False, default=Family.BillingPeriod.MONTHLY
    )
    # Onaylar: hiçbiri önceden işaretli gelmez; zorunlu olanlar işaretlenmeden hesap açılmaz.
    accept_contract = serializers.BooleanField(required=False, default=False)
    accept_privacy_notice = serializers.BooleanField(required=False, default=False)
    accept_trial_to_paid = serializers.BooleanField(required=False, default=False)
    household_ack = serializers.BooleanField(required=False, default=False)
    plus_consent = serializers.BooleanField(required=False, default=False)
    marketing_consent = serializers.BooleanField(required=False, default=False)

    CONSENT_FIELDS = {
        "accept_contract": ConsentRecord.Kind.CONTRACT,
        "accept_privacy_notice": ConsentRecord.Kind.PRIVACY_NOTICE,
        "accept_trial_to_paid": ConsentRecord.Kind.TRIAL_TO_PAID,
        "household_ack": ConsentRecord.Kind.HOUSEHOLD,
        "plus_consent": ConsentRecord.Kind.PLUS_SUMMARY,
        "marketing_consent": ConsentRecord.Kind.MARKETING,
    }

    class Meta:
        model = User
        fields = [
            "email", "password", "first_name", "last_name", "family_name", "plan", "billing_period",
            "accept_contract", "accept_privacy_notice", "accept_trial_to_paid", "household_ack",
            "plus_consent", "marketing_consent",
        ]
        extra_kwargs = {"first_name": {"required": True, "allow_blank": False}}

    def validate_email(self, value):
        value = value.lower()
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Bu e-posta adresiyle zaten bir hesap var.")
        return value

    def validate(self, attrs):
        candidate = User(email=attrs["email"], first_name=attrs.get("first_name", ""))
        password_validation.validate_password(attrs["password"], candidate)
        errors = {}
        if not attrs.get("accept_contract"):
            errors["accept_contract"] = "Ön bilgilendirme formunu ve mesafeli satış sözleşmesini onaylamanız gerekir."
        if not attrs.get("accept_privacy_notice"):
            errors["accept_privacy_notice"] = "KVKK aydınlatma metnini okuduğunuzu onaylamanız gerekir."
        if not attrs.get("accept_trial_to_paid"):
            errors["accept_trial_to_paid"] = "Deneme sonunda ücretli aboneliğin başlamasını onaylamanız gerekir."
        plan = attrs.get("plan", Family.Plan.FULL)
        if plan != Family.Plan.MONITOR and not attrs.get("household_ack"):
            errors["household_ack"] = "Bu pakette cihaz bazında kayıt tutulduğu için hane bireylerini bilgilendirdiğinizi onaylamanız gerekir."
        if plan == Family.Plan.PLUS and not attrs.get("plus_consent"):
            errors["plus_consent"] = "Aile Plus günlük özeti için açık rızanız gerekir. Rıza vermek istemezseniz Ebeveyn paketini seçebilirsiniz."
        if errors:
            raise serializers.ValidationError(errors)
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        family_name = validated_data.pop("family_name", "") or f"{validated_data['first_name']} Ailesi"
        plan = validated_data.pop("plan", Family.Plan.FULL)
        billing_period = validated_data.pop("billing_period", Family.BillingPeriod.MONTHLY)
        given = {field: validated_data.pop(field, False) for field in self.CONSENT_FIELDS}
        user = User.objects.create_user(**validated_data)
        # Her ebeveyn kendi ailesiyle, seçtiği paketle ve varsayılan koruma politikasıyla başlar.
        Family.create_with_defaults(owner=user, name=family_name, plan=plan, billing_period=billing_period)
        ConsentRecord.objects.bulk_create([
            ConsentRecord(user=user, kind=kind, version=LEGAL_VERSION)
            for field, kind in self.CONSENT_FIELDS.items()
            if given[field] and (kind != ConsentRecord.Kind.PLUS_SUMMARY or plan == Family.Plan.PLUS)
        ])
        return user


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    def validate_current_password(self, value):
        if not self.context["request"].user.check_password(value):
            raise serializers.ValidationError("Mevcut şifre hatalı.")
        return value

    def validate_new_password(self, value):
        password_validation.validate_password(value, self.context["request"].user)
        return value


class LoginSerializer(TokenObtainPairSerializer):
    default_error_messages = {
        "no_active_account": "E-posta veya şifre hatalı ya da hesap devre dışı.",
    }

    def validate(self, attrs):
        data = super().validate(attrs)
        data["user"] = UserSerializer(self.user).data
        return data


class AdminUserSerializer(serializers.ModelSerializer):
    """Yönetici panelinde kullanıcı yönetimi."""

    password = serializers.CharField(write_only=True, required=False)
    family_name = serializers.CharField(source="family.name", read_only=True, default=None)
    device_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id", "email", "first_name", "last_name", "role", "is_active",
            "date_joined", "last_login", "password", "family_name", "device_count",
        ]
        read_only_fields = ["id", "date_joined", "last_login"]

    def get_device_count(self, obj) -> int:
        family = getattr(obj, "family", None)
        return family.devices.count() if family else 0

    def validate_email(self, value):
        value = value.lower()
        qs = User.objects.filter(email=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Bu e-posta adresiyle zaten bir hesap var.")
        return value

    def validate(self, attrs):
        if self.instance:
            # Yönetici var olan bir hesapta yalnızca aktiflik durumunu değiştirebilir;
            # e-posta, ad, rol ve şifre kullanıcının kendisine aittir.
            locked = sorted(set(self.initial_data) - {"is_active"})
            if locked:
                raise serializers.ValidationError(
                    {key: ["Yönetici bu alanı değiştiremez; yalnızca hesabın aktiflik durumu değiştirilebilir."] for key in locked}
                )
        if not self.instance and not attrs.get("password"):
            raise serializers.ValidationError({"password": ["Yeni kullanıcı için şifre zorunludur."]})
        if attrs.get("password"):
            password_validation.validate_password(attrs["password"])
        request = self.context["request"]
        if self.instance and self.instance == request.user:
            if attrs.get("role", self.instance.role) != User.Role.ADMIN or attrs.get("is_active") is False:
                raise serializers.ValidationError("Kendi yönetici yetkinizi kaldıramaz veya hesabınızı kapatamazsınız.")
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User.objects.create_user(password=password, **validated_data)
        Family.create_with_defaults(owner=user, name=f"{user.first_name or user.email} Ailesi")
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        for key, value in validated_data.items():
            setattr(instance, key, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance
