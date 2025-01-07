from django import forms


class AccountDeletionForm(forms.Form):
    feedback = forms.CharField(
        label="Help us improve",
        widget=forms.Textarea(attrs={"placeholder": "Share your feedback..."}),
        required=False,
    )
    confirmation = forms.BooleanField(
        label="I confirm that I want to delete my account.", required=True
    )
