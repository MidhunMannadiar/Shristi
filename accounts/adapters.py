
from django.urls import reverse

from allauth.socialaccount.adapter import DefaultSocialAccountAdapter


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):

    def populate_user(self, request, sociallogin, data):
        user = super().populate_user(request, sociallogin, data)

        user.email = data.get("email", "").strip().lower()
        user.full_name = data.get("name", "")

        return user

    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)

        if not user.has_usable_password():
            request.session["google_password_setup"] = True

        return user

    def pre_social_login(self, request, sociallogin):
        super().pre_social_login(request, sociallogin)

        if sociallogin.is_existing:
            request.session["google_login_redirect"] = True

    def get_login_redirect_url(self, request):

        # New Google signup: password setup takes priority
        if request.session.get("google_password_setup"):
            return reverse("accounts:google_set_password")

        # Existing Google login: always redirect to Shop
        if request.session.pop("google_login_redirect", False):
            return reverse("storefront:shop")

        return super().get_login_redirect_url(request)
