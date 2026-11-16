
import secrets

from datetime import timedelta

from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.utils import timezone

from .models import EmailVerification


def generate_and_send_otp(email, purpose):

    # Generate a secure 6-digit OTP
    otp = f"{secrets.randbelow(1000000):06d}"

    # Set OTP expiration time (5 minutes)
    expires_at = timezone.now() + timedelta(minutes=5)

    # Invalidate previous unused OTPs
    EmailVerification.objects.filter(
        email=email,
        purpose=purpose,
        is_used=False
    ).update(is_used=True)

    # Send OTP email
    send_mail(
        subject="Your Shristi Verification Code",
        message=(
            f"Your Shristi verification code is {otp}.\n\n"
            "This code expires in 5 minutes.\n"
            "Please do not share this code with anyone."
        ),
        from_email=None,
        recipient_list=[email],
        fail_silently=False,
    )

    # Store only the hashed OTP
    EmailVerification.objects.create(
        email=email,
        purpose=purpose,
        otp_hash=make_password(otp),
        expires_at=expires_at
    )

    return True


from django.contrib.auth.hashers import check_password


def verify_otp(email, purpose, entered_otp):

    verification = EmailVerification.objects.filter(
        email=email,
        purpose=purpose,
        is_used=False
    ).order_by("-created_at").first()

    # Check whether an OTP exists
    if verification is None:
        return False, "No valid verification code found."

    # Check OTP expiry
    if timezone.now() > verification.expires_at:
        verification.is_used = True
        verification.save(update_fields=["is_used"])
        return False, "Verification code has expired."

    # Allow a maximum of 5 incorrect attempts
    if verification.attempts >= 5:
        verification.is_used = True
        verification.save(update_fields=["is_used"])
        return False, "Too many incorrect attempts. Request a new code."

    # Check entered OTP
    if not check_password(entered_otp, verification.otp_hash):

        verification.attempts += 1

        if verification.attempts >= 5:
            verification.is_used = True

        verification.save(update_fields=["attempts", "is_used"])

        return False, "Incorrect verification code."

    # OTP successfully verified
    verification.is_used = True
    verification.save(update_fields=["is_used"])

    return True, "Email verified successfully."
