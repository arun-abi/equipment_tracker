from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path('', include('equipment.urls')),
    path("login/", auth_views.LoginView.as_view(), name="login"),
    # path("signup/", auth_views.SignUpView.as_view(), name="signup"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("", include("equipment.urls")),
]
