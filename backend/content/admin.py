from django.contrib import admin

from .models import FAQ, ContactRequest


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ["question", "order", "is_published"]


@admin.register(ContactRequest)
class ContactRequestAdmin(admin.ModelAdmin):
    list_display = ["name", "email", "topic", "status", "created_at"]
    list_filter = ["status", "topic"]
