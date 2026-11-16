
from django.urls import reverse
from django.shortcuts import redirect
from django.contrib import messages

from allauth.account.adapter import DefaultAccountAdapter


class CustomAccountAdapter(DefaultAccountAdapter):

    def get_signup_redirect_url(self, request):
        if request.session.get("google_password_setup"):
            return reverse("accounts:google_set_password")

        return super().get_signup_redirect_url(request)

    def get_login_redirect_url(self, request):
        if request.session.get("google_password_setup"):
            return reverse("accounts:google_set_password")

        return super().get_login_redirect_url(request)

    def respond_user_inactive(self, request, user):

        messages.error(
            request,
            "Your account is currently blocked. "
            "Please contact customer support for assistance."
        )

        return redirect("accounts:customer_login")
