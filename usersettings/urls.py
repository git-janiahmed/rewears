from django.urls import path
from .views import (
    ProfileSettingsUpdateView,
    UserProfileUpdateView,
    DeleteAccountView,
    AccountDeactivatedView,
    ReportCreateView,
    ReportSuccessView,
)

urlpatterns = [
    path("settings", ProfileSettingsUpdateView.as_view(), name="usersettings"),
    path("profile", UserProfileUpdateView.as_view(), name="userprofile"),
    path("delete", DeleteAccountView.as_view(), name="account_delete"),
    path(
        "report/<int:reported_user_id>/",
        ReportCreateView.as_view(),
        name="report_create",
    ),
    path(
        "delete/sucess", AccountDeactivatedView.as_view(), name="account_deactivated"
    ),
    path("report/success/", ReportSuccessView.as_view(), name="report_success"),
]
