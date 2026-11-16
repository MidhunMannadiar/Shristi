
from django.contrib import messages
from django.contrib.auth import logout, get_user_model, SESSION_KEY
from django.shortcuts import redirect


class BlockedUserMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        # Get the user ID stored in the current session
        user_id = request.session.get(SESSION_KEY)

        if user_id:

            User = get_user_model()

            # Check the latest account status from the database
            user = User.objects.filter(
                pk=user_id
            ).only(
                "is_active",
                "is_admin"
            ).first()

            if user and not user.is_active and not user.is_admin:

                # Clear only this session
                logout(request)

                messages.error(
                    request,
                    "Your account has been blocked by the administrator. "
                    "You have been logged out. Please contact customer "
                    "support for assistance."
                )

                return redirect("accounts:customer_login")

        return self.get_response(request)
