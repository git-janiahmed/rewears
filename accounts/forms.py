from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.crypto import get_random_string
from django.core.validators import MinLengthValidator
import re, uuid


class InitialSignupForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(), validators=[MinLengthValidator(8)]
    )

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        # Generate a temporary unique username
        temp_username = f"temp_{uuid.uuid4().hex[:30]}"
        user.username = temp_username
        if commit:
            user.save()
        return user

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")

        # Password validation
        if not re.search(r"[A-Z]", password):
            raise forms.ValidationError(
                "Password must contain at least one uppercase letter."
            )
        if not re.search(r"[a-z]", password):
            raise forms.ValidationError(
                "Password must contain at least one lowercase letter."
            )
        if not re.search(r"\d", password):
            raise forms.ValidationError("Password must contain at least one number.")

        return cleaned_data


class VerificationCodeForm(forms.Form):
    code = forms.CharField(
        max_length=6, min_length=6, widget=forms.TextInput(attrs={"type": "number"})
    )


class UsernameForm(forms.Form):
    username = forms.CharField(max_length=30)

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken.")
        if not re.match(r"^[a-zA-Z0-9_]+$", username):
            raise forms.ValidationError(
                "Username can only contain letters, numbers, and underscores."
            )
        return username


class LoginForm(forms.Form):
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)


# forms.py


class ForgotPasswordForm(forms.Form):
    email = forms.EmailField()


class ResetPasswordForm(forms.Form):
    new_password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("new_password") != cleaned_data.get("confirm_password"):
            raise forms.ValidationError("Passwords do not match")
        return cleaned_data


