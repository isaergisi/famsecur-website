from django.contrib import admin

from .models import BlockEvent, Device, Family, Policy, ThreatSource, WhitelistEntry

admin.site.register([Family, Policy, Device, WhitelistEntry, ThreatSource])


@admin.register(BlockEvent)
class BlockEventAdmin(admin.ModelAdmin):
    list_display = ["domain", "category", "score", "family", "device", "created_at"]
    list_filter = ["category"]
