from django.contrib.auth import password_validation
from django.db import transaction
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from shield.models import Family

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

    class Meta:
        model = User
        fields = ["email", "password", "first_name", "last_name", "family_name"]
        extra_kwargs = {"first_name": {"required": True, "allow_blank": False}}

    def validate_email(self, value):
        value = value.lower()
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Bu e-posta adresiyle zaten bir hesap var.")
        return value

    def validate(self, attrs):
        candidate = User(email=attrs["email"], first_name=attrs.get("first_name", ""))
        password_validation.validate_password(attrs["password"], candidate)
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        family_name = validated_data.pop("family_name", "") or f"{validated_data['first_name']} Ailesi"
        user = User.objects.create_user(**validated_data)
        # Her ebeveyn kendi ailesiyle ve varsayılan koruma politikasıyla başlar.
        Family.create_with_defaults(owner=user, name=family_name)
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

    def get_device_count(self, obj):
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
