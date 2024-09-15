from django import forms
from .models import Product, ProductImage, Brand, Size, Color


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "title",
            "description",
            "brand",
            "size",
            "condition",
            "colors",
            "material",
            "price",
            "status",
        ]

    colors = forms.ModelMultipleChoiceField(
        queryset=Color.objects.all(), widget=forms.CheckboxSelectMultiple
    )


class ProductUpdateForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "title",
            "description",
            "condition",
            "material",
            "price",
            "status",
        ]


class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ["image"]
