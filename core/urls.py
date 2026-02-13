from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("profile/", views.profile_view, name="profile"),
    path("profile/edit/", views.profile_edit_view, name="profile_edit"),
    path("safe-trips/", views.safe_trips_view, name="safe_trips"),
    path("safety-points/", views.safety_points_view, name="safety_points"),
    path("sos/", views.sos_view, name="sos"),
    path("logout/", views.logout_view, name="logout"),
]
