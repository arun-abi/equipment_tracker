from django.urls import path

from . import views

urlpatterns = [
    
    path("signup/", views.signup, name="signup"),
    path("", views.dashboard, name="dashboard"),
    path("equipment/", views.EquipmentListView.as_view(), name="equipment_list"),
    path("equipment/add/", views.EquipmentCreateView.as_view(), name="equipment_add"),
    path("equipment/<int:pk>/", views.EquipmentDetailView.as_view(), name="equipment_detail"),
    path("equipment/<int:pk>/edit/", views.EquipmentUpdateView.as_view(), name="equipment_edit"),
    path("equipment/<int:pk>/pm/add/", views.PMRecordCreateView.as_view(), name="pm_add"),
    path("equipment/<int:pk>/fault/add/", views.FaultRecordCreateView.as_view(), name="fault_add"),

]
