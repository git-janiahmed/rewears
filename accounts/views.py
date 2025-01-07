from django.views.generic.edit import CreateView, FormView
from django.urls import reverse_lazy, reverse
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.shortcuts import render, redirect


from .forms import (
    InitialSignupForm,
    LoginForm,
    VerificationCodeForm,
    UsernameForm,
    ForgotPasswordForm,
    ResetPasswordForm,
)

from django.views import View
from django.utils import timezone
from datetime import timedelta
from django.http import JsonResponse
from django.contrib import messages
from .models import UserProfile
from django.contrib.auth.views import (
    PasswordResetView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetCompleteView,
    PasswordChangeView,
    PasswordChangeDoneView,
)


DEFAULT_FROM_EMAIL = "MS_bExJzU@trial-3z0vklo1pw7g7qrx.mlsender.net"


class customPasswordResetView(PasswordResetView):
    template_name = "accounts/forgot_password.html"
    html_email_template_name = (
        "accounts/emails/forgetPasswordEmail.html"  # Custom HTML email
    )


class customPassworddoneView(PasswordResetDoneView):
    template_name = "accounts/password_reset_done.html"


class customPasswordResetDoneView(PasswordResetCompleteView):
    template_name = "accounts/password_reset_complete.html"


from django.template.loader import render_to_string
from django.utils.html import strip_tags


class InitialSignupView(FormView):
    template_name = "accounts/initial_signup.html"
    form_class = InitialSignupForm
    success_url = reverse_lazy("verify-email")

    def form_valid(self, form):
        user = form.save(commit=False)
        user.set_password(form.cleaned_data["password"])
        user.save()

        # Create user profile
        UserProfile.objects.get_or_create(user=user)

        # Generate and send verification code
        code = user.userprofile.generate_verification_code()
        self._send_verification_email(user.email, code)

        self.request.session["signup_email"] = user.email
        return super().form_valid(form)

    def _send_verification_email(self, email, code):

        context = {
            "verification_code": code,
            "regenerate_url": self.request.build_absolute_uri(
                reverse_lazy("regenerate-code")
            ),
        }

        html_message = render_to_string(
            "accounts/emails/email_verification.html", context
        )
        plain_message = strip_tags(html_message)

        send_mail(
            subject="Verify your email",
            message=plain_message,
            html_message=html_message,
            from_email=DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )


class RegenerateCodeView(View):
    def get(self, request):
        if "signup_email" not in request.session:
            return JsonResponse(
                {"success": False, "message": "No ongoing signup process found."},
                status=400,
            )

        try:
            user_profile = UserProfile.objects.get(
                user__email=request.session["signup_email"]
            )

            if not user_profile.can_regenerate_code():
                wait_time = (
                    120
                    - (timezone.now() - user_profile.verification_code_created).seconds
                )
                return JsonResponse(
                    {
                        "success": False,
                        "message": f"Please wait {wait_time} seconds before requesting a new code.",
                    },
                    status=400,
                )

            # Generate and send new code
            code = user_profile.generate_verification_code()
            send_mail(
                "Your New Verification Code",
                f"Your new verification code is: {code}",
                "from@yourdomain.com",
                [user_profile.user.email],
                fail_silently=False,
            )

            return JsonResponse(
                {
                    "success": True,
                    "message": "New verification code has been sent to your email.",
                }
            )

        except UserProfile.DoesNotExist:
            return JsonResponse(
                {"success": False, "message": "User not found."}, status=400
            )


class VerifyEmailView(FormView):
    template_name = "accounts/verify_email.html"
    form_class = VerificationCodeForm
    success_url = reverse_lazy("set-username")

    def dispatch(self, request, *args, **kwargs):
        if "signup_email" not in request.session:
            return redirect("initial-signup")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        email = self.request.session["signup_email"]
        user_profile = UserProfile.objects.get(user__email=email)

        # Check if code is expired (15 minutes)
        if timezone.now() - user_profile.verification_code_created > timedelta(
            minutes=15
        ):
            form.add_error(
                None, "Verification code has expired. Please request a new one."
            )
            return self.form_invalid(form)

        if form.cleaned_data["code"] != user_profile.verification_code:
            form.add_error("code", "Invalid verification code.")
            return self.form_invalid(form)

        user_profile.email_verified = True
        user_profile.save()
        return super().form_valid(form)


class SetUsernameView(FormView):
    template_name = "accounts/set_username.html"
    form_class = UsernameForm
    success_url = reverse_lazy("login")

    def dispatch(self, request, *args, **kwargs):
        if "signup_email" not in request.session:
            return redirect("initial-signup")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        email = self.request.session["signup_email"]
        try:
            user = User.objects.get(email=email)

            # Check if the username is still temporary
            if not user.username.startswith("temp_"):
                form.add_error(None, "Username has already been set.")
                return self.form_invalid(form)

            user.username = form.cleaned_data["username"]
            user.is_active = True
            user.save()

            # Sending the welcome email
            context = {"username": user.username}
            html_message = render_to_string(
                "accounts/emails/welcome_email.html", context
            )
            plain_message = strip_tags(html_message)
            send_mail(
                subject="Welcome to Rewears",
                message=plain_message,
                html_message=html_message,
                recipient_list=[user.email],
                from_email=DEFAULT_FROM_EMAIL,
            )

            # Clean up session
            del self.request.session["signup_email"]

            # Log the user in
            login(self.request, user)
            return super().form_valid(form)

        except User.DoesNotExist:
            form.add_error(
                None, "User not found. Please start the signup process again."
            )
            return self.form_invalid(form)


from django.http import HttpResponseRedirect


class LoginView(FormView):
    form_class = LoginForm
    template_name = "accounts/login.html"
    success_url = reverse_lazy("userdashboardIndex")

    def form_valid(self, form):
        email = form.cleaned_data["email"]
        password = form.cleaned_data["password"]
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            form.add_error(None, "Invalid email or password")
            return self.form_invalid(form)
        user = authenticate(self.request, username=user.username, password=password)
        if user is not None:
            login(self.request, user)
            next_url = self.request.GET.get("next")
            if next_url:
                return HttpResponseRedirect(next_url)
            return super().form_valid(form)
        else:
            form.add_error(None, "Invalid email or password")
            return self.form_invalid(form)
