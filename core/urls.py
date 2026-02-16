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
    path("complete-trip/<int:trip_id>/", views.complete_trip_view, name="complete_trip"),
    path("safety-points/", views.safety_points_view, name="safety_points"),
    path("redeem-reward/<int:reward_id>/", views.redeem_reward_view, name="redeem_reward"),
    path("sos/", views.sos_view, name="sos"),
    path("add-feedback/", views.add_feedback_view, name="add_feedback"),
    path("safety-survey/<int:trip_id>/", views.safety_survey_view, name="safety_survey"),
    # path("smart-assistant/", views.smart_assistant_view, name="smart_assistant"),
    path("delete-contact/<int:contact_id>/", views.delete_contact_view, name="delete_contact"),
    path("logout/", views.logout_view, name="logout"),
]
