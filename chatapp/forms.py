from django import forms
from .models import Message, Offer


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ["text"]
        widgets = {
            "text": forms.Textarea(attrs={"rows": 3}),
        }


class OfferForm(forms.ModelForm):
    class Meta:
        model = Offer
        fields = ["price"]
