from django import forms
from accounts.models import UserProfile


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ["photo", "about", "location"]
        widgets = {
            "about": forms.Textarea(
                attrs={"placeholder": "Tell us more about yourself"}
            ),
            "location": forms.TextInput(attrs={"placeholder": "Enter your location"}),
        }


class ProfileSettingsForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ["gender", "birthday"]
        widgets = {
            "gender": forms.Select(attrs={"id": "gender"}),
            "birthday": forms.DateInput(attrs={"type": "date", "id": "bday"}),
        }


from django import forms


class DeleteAccountForm(forms.Form):
    feedback = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "placeholder": "Tell us why you’re closing your account",
                "class": "form-control",
                "rows": 4,
            }
        ),
        required=False,
    )
    confirmation = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
        error_messages={"required": "You must confirm before deleting your account."},
    )


from django import forms
from .models import Report
from django.contrib.auth.models import User


class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ["subject", "description", "media_file"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        reported_user = kwargs.pop("reported_user", None)
        super().__init__(*args, **kwargs)
        if reported_user:
            self.fields["reported_user"] = forms.ModelChoiceField(
                queryset=User.objects.filter(id=reported_user.id),
                initial=reported_user,
                widget=forms.HiddenInput(),
            )
