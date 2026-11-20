
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

from .models import Address


User = get_user_model()


# ==========================================
# ADMIN LOGIN FORM
# ==========================================

class AdminLoginForm(forms.Form):

    email = forms.EmailField(
        label="Email Address",
        widget=forms.EmailInput(attrs={
            "class": "form-control",
            "placeholder": "Enter your admin email",
            "autocomplete": "username",
        })
    )

    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Enter your password",
            "autocomplete": "current-password",
        })
    )

    def clean_email(self):
        return self.cleaned_data["email"].strip().lower()


# ==========================================
# CUSTOMER ADDRESS FORM
# ==========================================

class AddressForm(forms.ModelForm):

    class Meta:
        model = Address

        fields = [
            "full_name",
            "phone_number",
            "address_line",
            "landmark",
            "city",
            "state",
            "pincode",
            "address_type",
            "is_default",
        ]

        widgets = {
            "full_name": forms.TextInput(attrs={
                "placeholder": "Enter full name",
                "class": "address-input",
            }),

            "phone_number": forms.TextInput(attrs={
                "placeholder": "Enter phone number",
                "class": "address-input",
            }),

            "address_line": forms.Textarea(attrs={
                "placeholder": "House number, street name, area",
                "class": "address-input",
                "rows": 3,
            }),

            "landmark": forms.TextInput(attrs={
                "placeholder": "Nearby landmark (optional)",
                "class": "address-input",
            }),

            "city": forms.TextInput(attrs={
                "placeholder": "Enter city",
                "class": "address-input",
            }),

            "state": forms.TextInput(attrs={
                "placeholder": "Enter state",
                "class": "address-input",
            }),

            "pincode": forms.TextInput(attrs={
                "placeholder": "Enter PIN code",
                "class": "address-input",
            }),

            "address_type": forms.Select(attrs={
                "class": "address-input",
            }),

            "is_default": forms.CheckboxInput(attrs={
                "class": "address-checkbox",
            }),
        }


# ==========================================
# CREATE CUSTOMER FORM
# ==========================================

class CustomerCreateForm(forms.Form):

    full_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            "class": "customer-input",
            "placeholder": "Enter full name",
        })
    )

    email = forms.EmailField(
        max_length=254,
        required=True,
        widget=forms.EmailInput(attrs={
            "class": "customer-input",
            "placeholder": "Enter email address",
        })
    )

    profile_image = forms.ImageField(
    required=False,
    widget=forms.ClearableFileInput(attrs={
        "class": "form-control",
        "data-crop-image": "true",
        "accept": "image/*",
    })
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "customer-input",
            "placeholder": "Enter password",
        }),
        required=True
    )

    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "customer-input",
            "placeholder": "Confirm password",
        }),
        required=True
    )

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()

        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                "An account with this email already exists."
            )

        return email

    def clean(self):
        cleaned_data = super().clean()

        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            self.add_error(
                "confirm_password",
                "Passwords do not match."
            )

        if password:
            try:
                validate_password(password)
            except forms.ValidationError as error:
                self.add_error("password", error)

        return cleaned_data


# ==========================================
# UPDATE CUSTOMER FORM
# ==========================================

class CustomerUpdateForm(forms.Form):

    full_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            "class": "customer-input",
            "placeholder": "Enter full name",
        })
    )

    email = forms.EmailField(
        max_length=254,
        required=True,
        widget=forms.EmailInput(attrs={
            "class": "customer-input",
            "placeholder": "Enter email address",
        })
    )

    profile_image = forms.ImageField(
    required=False,
    widget=forms.ClearableFileInput(attrs={
        "class": "form-control",
        "data-crop-image": "true",
        "accept": "image/*",
    })
    )

    is_active = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            "class": "customer-checkbox",
        })
    )

    def __init__(self, *args, customer=None, **kwargs):
        self.customer = customer
        super().__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()

        existing_user = User.objects.filter(
            email__iexact=email
        ).exclude(
            pk=self.customer.pk
        )

        if existing_user.exists():
            raise forms.ValidationError(
                "Another account already uses this email."
            )

        return email
