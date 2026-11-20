
from django import forms
from django.forms import modelformset_factory

from .models import Category, Product, ProductImage


class CategoryForm(forms.ModelForm):

    class Meta:
        model = Category

        fields = [
            "name",
            "description",
            "image",
            "is_active",
        ]

        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter category name",
            }),

            "description": forms.Textarea(attrs={
                "class": "form-control",
                "placeholder": "Enter category description",
                "rows": 4,
            }),

            "image": forms.ClearableFileInput(attrs={
                "class": "form-control",
                "data-crop-image": "true",
            }),

            "is_active": forms.CheckboxInput(attrs={
                "class": "form-check-input",
            }),
        }


class ProductForm(forms.ModelForm):

    class Meta:
        model = Product

        fields = [
            "name",
            "category",
            "sku",
            "description",
            "original_price",
            "selling_price",
            "stock",
            "main_image",
            "is_active",
        ]

        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter product name",
            }),

            "category": forms.Select(attrs={
                "class": "form-control",
            }),

            "sku": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter unique SKU",
            }),

            "description": forms.Textarea(attrs={
                "class": "form-control",
                "placeholder": "Describe your product",
                "rows": 5,
            }),

            "original_price": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Enter original price",
                "min": "0.01",
                "step": "0.01",
            }),

            "selling_price": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Enter selling price",
                "min": "0.01",
                "step": "0.01",
            }),

            "stock": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Enter available stock",
                "min": "0",
            }),

            "main_image": forms.ClearableFileInput(attrs={
                "class": "form-control",
                "data-crop-image": "true",
            }),

            "is_active": forms.CheckboxInput(attrs={
                "class": "form-check-input",
            }),
        }

    def clean(self):

        cleaned_data = super().clean()

        original_price = cleaned_data.get("original_price")
        selling_price = cleaned_data.get("selling_price")

        if (
            original_price is not None
            and selling_price is not None
            and selling_price > original_price
        ):
            self.add_error(
                "selling_price",
                "Selling price cannot be greater than original price."
            )

        return cleaned_data


class ProductImageForm(forms.ModelForm):

    class Meta:
        model = ProductImage

        fields = [
            "image",
            "alt_text",
        ]

        widgets = {
            "image": forms.ClearableFileInput(attrs={
                "class": "form-control",
                "data-crop-image": "true",
            }),

            "alt_text": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Describe the image",
            }),
        }


ProductImageFormSet = modelformset_factory(
    ProductImage,
    form=ProductImageForm,
    extra=4,
    can_delete=True
)
