from django.contrib import admin

from .models import BlockEntry, BlockEvent, ConsentRecord, DailyDomainStat, Device, Family, Policy, ThreatSource, WhitelistEntry

admin.site.register([Family, Policy, Device, WhitelistEntry, BlockEntry, ThreatSource, DailyDomainStat])


@admin.register(ConsentRecord)
class ConsentRecordAdmin(admin.ModelAdmin):
    list_display = ["user", "kind", "version", "accepted_at", "withdrawn_at"]
    list_filter = ["kind", "version"]


@admin.register(BlockEvent)
class BlockEventAdmin(admin.ModelAdmin):
    list_display = ["domain", "category", "action", "score", "family", "device", "created_at"]
    list_filter = ["category", "action"]
