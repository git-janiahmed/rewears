from django import forms

from .models import AwaitingUser


class CommingSoonForm(forms.ModelForm):
    class Meta:
        model = AwaitingUser
        fields = ["email"]

        widgets = {
            "email": forms.EmailInput(attrs={"placeholder": "Enter Your Email "}),
        }
