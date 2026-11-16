
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.utils import timezone



class CustomUserManager(BaseUserManager):

    def normalize_user_email(self, email):
        if not email:
            raise ValueError("Email address is required.")

        return self.normalize_email(email).strip().lower()

    def get_by_natural_key(self, username):
        return self.get(email__iexact=username.strip())

    def create_user(self, email, password=None, **extra_fields):

        email = self.normalize_user_email(email)

        user = self.model(email=email, **extra_fields)

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password=None, **extra_fields):

        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_admin", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        if extra_fields.get("is_admin") is not True:
            raise ValueError("Superuser must have is_admin=True.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):

    email = models.EmailField(
        unique=True,
        max_length=254
    )

    full_name = models.CharField(
        max_length=150,
        blank=True,
        default=""
    )

    profile_image = models.ImageField(
        upload_to="profile_images/",
        blank=True,
        null=True
    )

    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    date_joined = models.DateTimeField(default=timezone.now)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email


class EmailVerification(models.Model):

    class Purpose(models.TextChoices):
        SIGNUP = "signup", "Signup"
        PASSWORD_RESET = "password_reset", "Password Reset"
        EMAIL_CHANGE = "email_change", "Email Change"

    email = models.EmailField(max_length=254)

    purpose = models.CharField(
        max_length=20,
        choices=Purpose.choices
    )

    otp_hash = models.CharField(max_length=128)

    expires_at = models.DateTimeField()

    attempts = models.PositiveSmallIntegerField(default=0)

    is_used = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.email} - {self.purpose}"


class Address(models.Model):

    class AddressType(models.TextChoices):
        HOME = "home", "Home"
        WORK = "work", "Work"
        OTHER = "other", "Other"

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="addresses"
    )

    full_name = models.CharField(max_length=150)

    phone_number = models.CharField(max_length=15)

    address_line = models.TextField()

    landmark = models.CharField(
        max_length=150,
        blank=True
    )

    city = models.CharField(max_length=100)

    state = models.CharField(max_length=100)

    pincode = models.CharField(max_length=10)

    address_type = models.CharField(
        max_length=10,
        choices=AddressType.choices,
        default=AddressType.HOME
    )

    is_default = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.full_name} - {self.city}"
