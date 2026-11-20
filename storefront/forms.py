
from django import forms


class ContactForm(forms.Form):

    name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            "id": "contactName",
            "placeholder": "Enter your name",
        })
    )

    email = forms.EmailField(
        max_length=254,
        required=True,
        widget=forms.EmailInput(attrs={
            "id": "contactEmail",
            "placeholder": "Enter your email",
        })
    )

    subject = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            "id": "contactSubject",
            "placeholder": "What is your message about?",
        })
    )

    message = forms.CharField(
        max_length=5000,
        required=True,
        widget=forms.Textarea(attrs={
            "id": "contactMessage",
            "rows": 5,
            "placeholder": "Write your message here...",
        })
    )
