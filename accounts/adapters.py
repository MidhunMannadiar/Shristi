
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
