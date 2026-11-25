from datetime import timedelta

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone


class Equipment(models.Model):
    CATEGORY_CHOICES = [
        ("transformer", "Transformer"),
        ("ht_lt_panel", "HT / LT Panel"),
        ("dg_set", "DG Set"),
        ("ups", "UPS"),
        ("battery", "Battery Bank"),
        ("apfc", "APFC Panel"),
        ("mcc", "MCC Panel"),
        ("db", "Distribution Board"),
        ("busduct", "Bus Duct"),
        ("earthing", "Earthing Pit"),
        ("lift", "Lift"),
        ("pump", "Pump / Motor"),
        ("ahu", "AHU"),
        ("chiller", "Chiller"),
        ("fire_alarm", "Fire Alarm Panel"),
        ("emergency_light", "Emergency Lighting"),
        ("lightning", "Lightning Arrestor"),
        ("other", "Other"),
    ]

    STATUS_CHOICES = [
        ("running", "Running"),
        ("standby", "Standby"),
        ("under_repair", "Under repair"),
        ("out_of_service", "Out of service"),
    ]

    PPM_CHOICES = [
        (30, "Monthly"),
        (90, "Quarterly"),
        (180, "Half-yearly"),
        (365, "Yearly"),
    ]

    tag_no = models.CharField("Tag / ID", max_length=50, unique=True)
    name = models.CharField(max_length=120)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES)
    location = models.CharField(
        max_length=150, help_text="Block, floor, room. Example: Block A, Basement, Pump Room"
    )
    make = models.CharField(max_length=80, blank=True)
    model_no = models.CharField("Model", max_length=80, blank=True)
    serial_no = models.CharField("Serial number", max_length=80, blank=True)
    rating = models.CharField(
        max_length=80, blank=True, help_text="Example: 500 kVA, 11/0.433 kV"
    )
    installation_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="running")

    ppm_period_days = models.PositiveIntegerField(
        "PPM period", choices=PPM_CHOICES, default=90
    )
    last_pm_date = models.DateField(
        "Last PM date",
        null=True,
        blank=True,
        help_text="Updates automatically when you add a PM record.",
    )
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["tag_no"]
        verbose_name_plural = "equipment"

    def __str__(self):
        return f"{self.tag_no} - {self.name}"

    def get_absolute_url(self):
        return reverse("equipment_detail", args=[self.pk])

    # ---- PM due-date logic -------------------------------------------------
    @property
    def next_pm_due(self):
        """Last PM date + PPM period. If never serviced, use the installation date."""
        base = self.last_pm_date or self.installation_date
        if base is None:
            return None
        return base + timedelta(days=self.ppm_period_days)

    @property
    def days_to_due(self):
        due = self.next_pm_due
        if due is None:
            return None
        return (due - timezone.localdate()).days

    @property
    def pm_status(self):
        """Returns 'overdue', 'due_soon', 'ok' or 'unknown'."""
        days = self.days_to_due
        if days is None:
            return "unknown"
        if days < 0:
            return "overdue"
        if days <= getattr(settings, "PM_DUE_SOON_DAYS", 14):
            return "due_soon"
        return "ok"

    @property
    def last_fault(self):
        return self.faults.order_by("-date", "-id").first()

    def refresh_last_pm_date(self):
        latest = self.pm_records.order_by("-date").first()
        self.last_pm_date = latest.date if latest else None
        self.save(update_fields=["last_pm_date"])


class PMRecord(models.Model):
    equipment = models.ForeignKey(
        Equipment, on_delete=models.CASCADE, related_name="pm_records"
    )
    date = models.DateField(default=timezone.localdate)
    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL
    )
    work_done = models.TextField(help_text="Cleaning, tightening, readings, tests...")
    remarks = models.TextField(blank=True)

    class Meta:
        ordering = ["-date", "-id"]
        verbose_name = "PM record"

    def __str__(self):
        return f"PM {self.equipment.tag_no} on {self.date}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.equipment.refresh_last_pm_date()

    def delete(self, *args, **kwargs):
        equipment = self.equipment
        super().delete(*args, **kwargs)
        equipment.refresh_last_pm_date()


class FaultRecord(models.Model):
    equipment = models.ForeignKey(
        Equipment, on_delete=models.CASCADE, related_name="faults"
    )
    date = models.DateField(default=timezone.localdate)
    fault_diagnosed = models.CharField(max_length=250)
    action_taken = models.TextField(blank=True)
    fixed_by = models.CharField(max_length=100, blank=True)
    downtime_hours = models.DecimalField(
        max_digits=6, decimal_places=1, null=True, blank=True
    )
    resolved = models.BooleanField(default=True)

    class Meta:
        ordering = ["-date", "-id"]
        verbose_name = "fault record"

    def __str__(self):
        return f"Fault {self.equipment.tag_no} on {self.date}"
