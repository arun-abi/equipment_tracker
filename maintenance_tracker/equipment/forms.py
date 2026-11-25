from django import forms
from django.contrib.auth.models import Group, User
from django.contrib.auth.forms import UserCreationForm
from .models import Equipment, FaultRecord, PMRecord

class SignUpForm(UserCreationForm):
    """Sign-up form. New users start as view-only (Manager group)."""

    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "first_name", "email", "password1", "password2"]

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            group, _ = Group.objects.get_or_create(name="Manager")
            user.groups.add(group)
        return user

class DateInput(forms.DateInput):
    input_type = "date"

    def __init__(self, **kwargs):
        kwargs.setdefault("format", "%Y-%m-%d")
        super().__init__(**kwargs)


class EquipmentForm(forms.ModelForm):
    class Meta:
        model = Equipment
        fields = [
            "tag_no", "name", "category", "location", "make", "model_no",
            "serial_no", "rating", "installation_date", "status",
            "ppm_period_days", "notes",
        ]
        widgets = {
            "installation_date": DateInput(),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }


class PMRecordForm(forms.ModelForm):
    class Meta:
        model = PMRecord
        fields = ["date", "work_done", "remarks"]
        widgets = {
            "date": DateInput(),
            "work_done": forms.Textarea(attrs={"rows": 4}),
            "remarks": forms.Textarea(attrs={"rows": 3}),
        }


class FaultRecordForm(forms.ModelForm):
    class Meta:
        model = FaultRecord
        fields = [
            "date", "fault_diagnosed", "action_taken", "fixed_by",
            "downtime_hours", "resolved",
        ]
        widgets = {
            "date": DateInput(),
            "action_taken": forms.Textarea(attrs={"rows": 4}),
        }
