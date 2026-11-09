from rest_framework import serializers

from .models import FAQ, ContactRequest


class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = ["id", "question", "answer", "order", "is_published", "created_at"]
        read_only_fields = ["id", "created_at"]


class ContactRequestSerializer(serializers.ModelSerializer):
    topic_label = serializers.CharField(source="get_topic_display", read_only=True)
    status_label = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = ContactRequest
        fields = [
            "id", "name", "email", "topic", "topic_label", "message", "status",
            "status_label", "admin_note", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_message(self, value):
        if len(value.strip()) < 10:
            raise serializers.ValidationError("Mesajınız en az 10 karakter olmalı.")
        return value.strip()


class PublicContactRequestSerializer(ContactRequestSerializer):
    """Ziyaretçi talep oluştururken durum ve not alanlarını belirleyemez."""

    class Meta(ContactRequestSerializer.Meta):
        read_only_fields = ["id", "status", "admin_note", "created_at", "updated_at"]
