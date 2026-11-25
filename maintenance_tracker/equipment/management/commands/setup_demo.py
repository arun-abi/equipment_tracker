"""Creates the Engineer and Manager roles, two demo users and sample equipment.

Run once:  python manage.py setup_demo
"""
from datetime import timedelta

from django.contrib.auth.models import Group, Permission, User
from django.core.management.base import BaseCommand
from django.utils import timezone

from equipment.models import Equipment, FaultRecord, PMRecord


class Command(BaseCommand):
    help = "Create roles (Engineer, Manager), demo users and sample data."

    def handle(self, *args, **options):
        self.create_roles()
        self.create_users()
        self.create_sample_data()
        self.stdout.write(self.style.SUCCESS("Done."))

    def create_roles(self):
        engineer, _ = Group.objects.get_or_create(name="Engineer")
        manager, _ = Group.objects.get_or_create(name="Manager")
        models = ["equipment", "pmrecord", "faultrecord"]
        engineer.permissions.set(
            Permission.objects.filter(
                content_type__app_label="equipment",
                codename__regex=r"^(add|change|view)_(" + "|".join(models) + ")$",
            )
        )
        manager.permissions.set(
            Permission.objects.filter(
                content_type__app_label="equipment", codename__startswith="view_"
            )
        )

    def create_users(self):
        for username, group in [("engineer", "Engineer"), ("manager", "Manager")]:
            user, created = User.objects.get_or_create(username=username)
            if created:
                user.set_password("demo12345")
                user.save()
            user.groups.set([Group.objects.get(name=group)])
        self.stdout.write("Demo users: engineer / manager  (password: demo12345)")

    def create_sample_data(self):
        if Equipment.objects.exists():
            return
        today = timezone.localdate()
        samples = [
            ("TR-01", "Main Transformer 1", "transformer", "Block A, Ground, Transformer Yard", "500 kVA, 11/0.433 kV", 365, 400),
            ("DG-01", "DG Set 1", "dg_set", "Block A, Basement, DG Room", "750 kVA", 90, 50),
            ("UPS-01", "Server Room UPS", "ups", "Block B, 2nd Floor, UPS Room", "40 kVA", 90, 85),
            ("LIFT-03", "Passenger Lift 3", "lift", "Block A, Lift Lobby", "13 persons", 30, 20),
            ("PMP-02", "Fire Pump", "pump", "Block A, Basement, Pump Room", "30 kW", 30, 5),
        ]
        for tag, name, cat, loc, rating, period, days_ago in samples:
            eq = Equipment.objects.create(
                tag_no=tag, name=name, category=cat, location=loc, rating=rating,
                ppm_period_days=period, installation_date=today - timedelta(days=900),
            )
            PMRecord.objects.create(
                equipment=eq, date=today - timedelta(days=days_ago),
                work_done="Cleaning, tightening of terminals, insulation check.",
            )
        FaultRecord.objects.create(
            equipment=Equipment.objects.get(tag_no="DG-01"),
            date=today - timedelta(days=12),
            fault_diagnosed="Low battery voltage, engine failed to crank",
            action_taken="Replaced starter battery",
            fixed_by="Rajesh", downtime_hours=2, resolved=True,
        )
