from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from .forms import EquipmentForm, FaultRecordForm, PMRecordForm, SignUpForm
from .models import Equipment, FaultRecord


def signup(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(
                request,
                "Account created. You have view-only access until an admin "
                "makes you an Engineer.",
            )
            return redirect("dashboard")
    else:
        form = SignUpForm()
    return render(request, "registration/signup.html", {"form": form})


@login_required
def dashboard(request):
    all_equipment = list(Equipment.objects.all())
    overdue = [e for e in all_equipment if e.pm_status == "overdue"]
    due_soon = [e for e in all_equipment if e.pm_status == "due_soon"]
    overdue.sort(key=lambda e: e.days_to_due)
    due_soon.sort(key=lambda e: e.days_to_due)
    context = {
        "total": len(all_equipment),
        "overdue": overdue,
        "due_soon": due_soon,
        "under_repair": [e for e in all_equipment if e.status == "under_repair"],
        "recent_faults": FaultRecord.objects.select_related("equipment")[:5],
    }
    return render(request, "equipment/dashboard.html", context)


class EquipmentListView(LoginRequiredMixin, ListView):
    model = Equipment
    template_name = "equipment/equipment_list.html"
    context_object_name = "items"

    def get_queryset(self):
        qs = Equipment.objects.all()
        q = self.request.GET.get("q", "").strip()
        category = self.request.GET.get("category", "")
        status = self.request.GET.get("status", "")
        if q:
            from django.db.models import Q
            qs = qs.filter(
                Q(tag_no__icontains=q) | Q(name__icontains=q)
                | Q(location__icontains=q) | Q(serial_no__icontains=q)
            )
        if category:
            qs = qs.filter(category=category)
        if status:
            qs = qs.filter(status=status)
        items = list(qs)
        pm = self.request.GET.get("pm", "")
        if pm:
            items = [e for e in items if e.pm_status == pm]
        return items

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["categories"] = Equipment.CATEGORY_CHOICES
        ctx["statuses"] = Equipment.STATUS_CHOICES
        ctx["filters"] = self.request.GET
        return ctx


class EquipmentDetailView(LoginRequiredMixin, DetailView):
    model = Equipment
    template_name = "equipment/equipment_detail.html"
    context_object_name = "item"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["pm_records"] = self.object.pm_records.select_related("performed_by")
        ctx["faults"] = self.object.faults.all()
        return ctx


class EquipmentCreateView(PermissionRequiredMixin, CreateView):
    model = Equipment
    form_class = EquipmentForm
    template_name = "equipment/form.html"
    permission_required = "equipment.add_equipment"
    extra_context = {"title": "Add equipment"}


class EquipmentUpdateView(PermissionRequiredMixin, UpdateView):
    model = Equipment
    form_class = EquipmentForm
    template_name = "equipment/form.html"
    permission_required = "equipment.change_equipment"
    extra_context = {"title": "Edit equipment"}


class _RecordCreateView(PermissionRequiredMixin, CreateView):
    """Shared logic: the record belongs to the equipment in the URL."""
    template_name = "equipment/form.html"

    def dispatch(self, request, *args, **kwargs):
        self.equipment = get_object_or_404(Equipment, pk=kwargs["pk"])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["equipment"] = self.equipment
        return ctx

    def get_success_url(self):
        return self.equipment.get_absolute_url()


class PMRecordCreateView(_RecordCreateView):
    form_class = PMRecordForm
    permission_required = "equipment.add_pmrecord"
    extra_context = {"title": "Add PM record"}

    def form_valid(self, form):
        form.instance.equipment = self.equipment
        form.instance.performed_by = self.request.user
        return super().form_valid(form)


class FaultRecordCreateView(_RecordCreateView):
    form_class = FaultRecordForm
    permission_required = "equipment.add_faultrecord"
    extra_context = {"title": "Log a fault"}

    def form_valid(self, form):
        form.instance.equipment = self.equipment
        return super().form_valid(form)
