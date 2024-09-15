from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.crypto import get_random_string


class RegisterForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)
    accept_terms = forms.BooleanField(
        required=True,
        error_messages={"required": "You must accept the terms and conditions"},
    )

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "password"]

    def save(self, commit=True):
        user = super(RegisterForm, self).save(commit=False)
        # Generate a unique placeholder username
        unique_suffix = get_random_string(length=8)
        user.username = f"user_{unique_suffix}"
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.is_active = False  # Deactivate account until it is verified
            user.save()
        return user


class LoginForm(forms.Form):
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)


class VerificationCodeForm(forms.Form):
    code = forms.CharField(max_length=6, required=True)


class ResendCodeForm(forms.Form):
    email = forms.EmailField(required=True)


class SetUsernameForm(forms.Form):
    username = forms.CharField(max_length=150, required=True)

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if User.objects.filter(username=username).exists():
            raise ValidationError("Username already exists")
        return username
