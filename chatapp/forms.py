from django import forms
from .models import Message, Offer


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ["text", "image"]
        widgets = {
            "text": forms.Textarea(attrs={"rows": 3}),
        }


class OfferForm(forms.ModelForm):
    class Meta:
        model = Offer
        fields = ["amount", "description"]
        widgets = {
            "amount": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "Enter offer amount"}
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Enter offer details",
                }
            ),
        }
