from django.views.generic.edit import CreateView, FormView
from django.urls import reverse_lazy
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.shortcuts import render, redirect
from .forms import (
    RegisterForm,
    LoginForm,
    VerificationCodeForm,
    ResendCodeForm,
    SetUsernameForm,
)
from .models import VerificationCode


class SignUpView(CreateView):
    form_class = RegisterForm
    template_name = "accounts/signup.html"
    success_url = reverse_lazy("login")

    # def form_valid(self, form):
    #     valid = super(SignUpView, self).form_valid(form)
    #     self.request.session["user_id"] = self.object.id
    #     return redirect(self.success_url)


class SendVerificationCodeView(FormView):
    template_name = "accounts/send_verification_code.html"
    success_url = reverse_lazy("verify_code")

    def get(self, request, *args, **kwargs):
        print("SendVerificationCodeView.get() called")  # Debug statement
        user_id = request.session.get("user_id")
        if not user_id:
            print("User ID not found in session")  # Debug statement
            return redirect("signup")
        user = User.objects.get(pk=user_id)
        code = get_random_string(length=6, allowed_chars="0123456789")
        VerificationCode.objects.update_or_create(user=user, defaults={"code": code})
        send_mail(
            "Your verification code",
            f"Your verification code is {code}",
            "from@example.com",  # Replace with your from email address
            [user.email],
            fail_silently=False,
        )
        print("Verification code sent")  # Debug statement

        # Simplify method call
        return render(request, self.template_name)


class VerifyCodeView(FormView):
    form_class = VerificationCodeForm
    template_name = "accounts/verify_code.html"
    success_url = reverse_lazy("set_username")

    def form_valid(self, form):
        user_id = self.request.session.get("user_id")
        if not user_id:
            return redirect("signup")
        user = User.objects.get(pk=user_id)
        try:
            verification_code = VerificationCode.objects.get(user=user)
        except VerificationCode.DoesNotExist:
            form.add_error(None, "Verification code not found.")
            return self.form_invalid(form)

        if form.cleaned_data["code"] == verification_code.code:
            user.is_active = True
            user.save()
            verification_code.delete()
            return super().form_valid(form)
        else:
            form.add_error("code", "Invalid verification code")
            return self.form_invalid(form)


class ResendVerificationCodeView(FormView):
    form_class = ResendCodeForm
    template_name = "accounts/resend_code.html"
    success_url = reverse_lazy("send_verification_code")

    def form_valid(self, form):
        email = form.cleaned_data["email"]
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            form.add_error("email", "Email not found")
            return self.form_invalid(form)

        code = get_random_string(length=6, allowed_chars="0123456789")
        VerificationCode.objects.update_or_create(user=user, defaults={"code": code})
        send_mail(
            "Your verification code",
            f"Your verification code is {code}",
            "from@example.com",
            [user.email],
            fail_silently=False,
        )
        self.request.session["user_id"] = user.id
        return super().form_valid(form)


class SetUsernameView(FormView):
    form_class = SetUsernameForm
    template_name = "accounts/set_username.html"
    success_url = reverse_lazy("login")

    def form_valid(self, form):
        user_id = self.request.session.get("user_id")
        if not user_id:
            return redirect("signup")
        user = User.objects.get(pk=user_id)
        user.username = form.cleaned_data["username"]
        user.save()
        login(self.request, user)
        return super().form_valid(form)


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
            return super().form_valid(form)
        else:
            form.add_error(None, "Invalid email or password")
            return self.form_invalid(form)
