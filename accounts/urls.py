from django.urls import path
from .views import LoginView
from django.contrib.auth.views import LogoutView
from .views import (
    InitialSignupView,
    VerifyEmailView,
    SetUsernameView,
    RegenerateCodeView,
    customPasswordResetView,
    customPassworddoneView,
    customPasswordResetDoneView,
)

from django.contrib.auth.views import PasswordChangeView, PasswordChangeDoneView

from django.contrib.auth import views as auth_views

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(next_page="login"), name="logout"),
    path("signup/", InitialSignupView.as_view(), name="signup"),
    path("verify-email/", VerifyEmailView.as_view(), name="verify-email"),
    path("set-username/", SetUsernameView.as_view(), name="set-username"),
    path("regenerate-code/", RegenerateCodeView.as_view(), name="regenerate-code"),
    path("password_reset/", customPasswordResetView.as_view(), name="password_reset"),
    path(
        "password_reset/done/",
        customPassworddoneView.as_view(),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="accounts/password_reset_confirm.html"
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        customPasswordResetDoneView.as_view(),
        name="password_reset_complete",
    ),
    path(
        "password/change/",
        PasswordChangeView.as_view(
            template_name="accounts/password_change.html",
            success_url="/password/change/done/",
        ),
        name="password_change",
    ),
    path(
        "password/change/done/",
        PasswordChangeDoneView.as_view(template_name="accounts/password_change_done.html"),
        name="password_change_done",
    ),
]
