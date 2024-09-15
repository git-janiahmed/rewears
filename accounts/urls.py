from django.urls import path
from .views import SignUpView, LoginView
from django.contrib.auth.views import LogoutView
from .views import (
    SendVerificationCodeView,
    VerifyCodeView,
    ResendVerificationCodeView,
    SetUsernameView,
)

urlpatterns = [
    path("signup/", SignUpView.as_view(), name="signup"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(next_page="login"), name="logout"),
    path(
        "send_verification_code/",
        SendVerificationCodeView.as_view(),
        name="send_verification_code",
    ),
    path("verify_code/", VerifyCodeView.as_view(), name="verify_code"),
    path("resend_code/", ResendVerificationCodeView.as_view(), name="resend_code"),
    path("set_username/", SetUsernameView.as_view(), name="set_username"),
]
