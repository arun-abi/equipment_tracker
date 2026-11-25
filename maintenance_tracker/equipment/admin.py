from django.contrib import admin

from .models import Equipment, FaultRecord, PMRecord


class PMRecordInline(admin.TabularInline):
    model = PMRecord
    extra = 0


class FaultRecordInline(admin.TabularInline):
    model = FaultRecord
    extra = 0


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = (
        "tag_no", "name", "category", "location", "status",
        "ppm_period_days", "last_pm_date", "next_pm_due",
    )
    list_filter = ("category", "status", "ppm_period_days")
    search_fields = ("tag_no", "name", "location", "serial_no")
    readonly_fields = ("last_pm_date",)
    inlines = [PMRecordInline, FaultRecordInline]


@admin.register(PMRecord)
class PMRecordAdmin(admin.ModelAdmin):
    list_display = ("equipment", "date", "performed_by")
    list_filter = ("date",)


@admin.register(FaultRecord)
class FaultRecordAdmin(admin.ModelAdmin):
    list_display = ("equipment", "date", "fault_diagnosed", "resolved")
    list_filter = ("resolved", "date")
