from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.views.decorators.http import require_POST
from django.contrib.auth import logout
from django.db import transaction
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib.auth.decorators import user_passes_test
from .forms import (
    AdminLoginForm,
    AddressForm,
    CustomerCreateForm,
    CustomerUpdateForm,
)
from django.contrib.auth import get_user_model
from .models import User, EmailVerification, Address
from django.contrib.auth.backends import ModelBackend
from functools import wraps
from .services import (
    generate_and_send_otp,
    verify_otp as verify_otp_code,
)
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import update_session_auth_hash
from products.models import Category, Product


User = get_user_model()



def admin_login(request):

    if (
        request.user.is_authenticated
        and request.user.is_admin
        and request.user.is_active
    ):
        return redirect("accounts:admin_dashboard")

    if request.method == "POST":

        form = AdminLoginForm(request.POST)

        if form.is_valid():

            email = form.cleaned_data["email"].strip().lower()
            password = form.cleaned_data["password"]

            user = authenticate(
                request,
                email=email,
                password=password
            )

            if (
                user is not None
                and user.is_admin
                and user.is_active
            ):

                login(request, user)

                return redirect("accounts:admin_dashboard")

            messages.error(
                request,
                "Invalid email or password."
            )

    else:
        form = AdminLoginForm()

    return render(
        request,
        "accounts/admin_login.html",
        {"form": form}
    )


from django.utils import timezone


def admin_required(view_func):

    @wraps(view_func)
    @login_required(login_url="accounts:admin_login")
    def wrapper(request, *args, **kwargs):

        if not request.user.is_active or not request.user.is_admin:
            raise PermissionDenied

        return view_func(request, *args, **kwargs)

    return wrapper

@admin_required
def admin_dashboard(request):
    total_products = Product.objects.count()
    total_categories = Category.objects.count()
    total_customers = User.objects.filter(is_admin=False).count()

    return render(
        request,
        "shristi_admin/dashboard.html",
        {
            "now": timezone.now(),
            "total_products": total_products,
            "total_categories": total_categories,
            "total_customers": total_customers,
        }
    )

@admin_required
@require_POST
def admin_logout(request):

    logout(request)

    return redirect("accounts:admin_login")

# CUSTOMER MANAGEMENT

@admin_required
def customer_list(request):

    # Get only customer accounts
    customers = User.objects.filter(
        is_admin=False,
        is_superuser=False
    )

    # SEARCH
    search_query = request.GET.get("search", "").strip()

    if search_query:
        customers = customers.filter(
            Q(full_name__icontains=search_query) |
            Q(email__icontains=search_query)
        )

    # STATUS FILTER
    status_filter = request.GET.get("status", "all")

    if status_filter == "active":
        customers = customers.filter(is_active=True)

    elif status_filter == "blocked":
        customers = customers.filter(is_active=False)

    # SORTING
    sort_by = request.GET.get("sort", "-date_joined")

    allowed_sort_fields = [
        "full_name",
        "-full_name",
        "email",
        "-email",
        "date_joined",
        "-date_joined",
    ]

    if sort_by not in allowed_sort_fields:
        sort_by = "-date_joined"

    customers = customers.order_by(sort_by)

    # PAGINATION
    page_size = request.GET.get("page_size", "10")

    allowed_page_sizes = ["10", "25", "50", "100"]

    if page_size not in allowed_page_sizes:
        page_size = "10"

    paginator = Paginator(customers, int(page_size))

    page_number = request.GET.get("page")

    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "shristi_admin/customer_list.html",
        {
            "customers": page_obj,
            "page_obj": page_obj,
            "search_query": search_query,
            "status_filter": status_filter,
            "sort_by": sort_by,
            "page_size": page_size,
        }
    )


# CUSTOMER DETAILS

@admin_required
def customer_detail(request, customer_id):

    customer = get_object_or_404(
        User.objects.prefetch_related("addresses"),
        id=customer_id,
        is_admin=False,
        is_superuser=False
    )

    return render(
        request,
        "shristi_admin/customer_detail.html",
        {
            "customer": customer,
        }
    )


# BLOCK / UNBLOCK CUSTOMER

@admin_required
def customer_status_confirm(request, customer_id, action):

    if action not in ["block", "unblock"]:
        from django.http import Http404
        raise Http404("Invalid customer action.")

    customer = get_object_or_404(
        User,
        id=customer_id,
        is_admin=False,
        is_superuser=False
    )

    if request.method == "POST":

        customer.is_active = (action == "unblock")

        customer.save(update_fields=["is_active"])

        if action == "block":
            messages.success(
                request,
                f"{customer.email} has been blocked successfully."
            )
        else:
            messages.success(
                request,
                f"{customer.email} has been unblocked successfully."
            )

        return redirect(
            "accounts:customer_detail",
            customer_id=customer.id
        )

    return render(
        request,
        "shristi_admin/customer_status_confirm.html",
        {
            "customer": customer,
            "action": action,
        }
    )


def customer_signup(request):

    if request.method == "POST":
        print("SIGNUP POST REQUEST RECEIVED")
        full_name = request.POST.get("full_name", "").strip()
        email = request.POST.get("email", "").strip().lower()

        if not full_name or not email:
            messages.error(request, "Please fill in all required fields.")
            return render(request, "accounts/signup.html")

        try:
            validate_email(email)
        except ValidationError:
            print("INVALID EMAIL")
            messages.error(request, "Please enter a valid email address.")
            return render(request, "accounts/signup.html")

        if User.objects.filter(email=email).exists():
            print("EMAIL ALREADY EXISTS")
            messages.error(request, "An account with this email already exists.")
            return render(request, "accounts/signup.html")

        try:
            generate_and_send_otp(
                email,
                EmailVerification.Purpose.SIGNUP
            )
            print("GENERATING OTP FOR:", email)
            request.session["pending_signup"] = {
                "full_name": full_name,
                "email": email,
            }

            request.session.set_expiry(600)

            messages.success(
                request,
                "Verification code sent successfully!"
            )

            return redirect("accounts:verify_otp")

        except Exception:
            messages.error(
                request,
                "Unable to send the verification code. Please try again."
            )

    return render(request, "accounts/signup.html")




def customer_login(request):

    if request.user.is_authenticated:
        if request.user.is_admin:
            return redirect("accounts:admin_dashboard")

        return redirect("storefront:home")

    if request.method == "POST":

        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "")

        # Find the customer account
        customer = User.objects.filter(
            email__iexact=email,
            is_admin=False,
            is_superuser=False
        ).first()

        if customer and customer.check_password(password):

            if not customer.is_active:
                messages.error(
                    request,
                    "Your account is currently blocked. "
                    "Please contact customer support for assistance.",
                    extra_tags="login"
                )

                return render(
                    request,
                    "accounts/login.html"
                )

            user = authenticate(
                request,
                email=email,
                password=password
            )

            if user is not None:

                login(request, user)

                messages.success(
                    request,
                    "Welcome back to Shristi!",
                    extra_tags="login"
                )

                # Retrieve the product requested before login.
                pending_add = request.session.pop(
                    "pending_add_to_cart",
                    None
                )

                if pending_add:

                    product = Product.objects.filter(
                        id=pending_add.get("product_id"),
                        is_active=True,
                        category__is_active=True
                    ).first()

                    if product:
                        try:
                            from cart.cart import Cart
                            from wishlist.services import remove_from_wishlist

                            cart = Cart(request)

                            cart.add(
                                product,
                                pending_add.get("quantity", 1)
                            )

                            remove_from_wishlist(request, product)

                            messages.success(
                                request,
                                f"{product.name} added to your shopping bag."
                            )

                            return redirect("cart:cart_detail")

                        except (ValueError, TypeError) as error:
                            messages.error(request, str(error))

                    else:
                        messages.error(
                            request,
                            "This product is no longer available."
                        )

                return redirect("storefront:home")

        messages.error(
            request,
            "Invalid email or password. Please try again."
        )

    # Display login page for GET requests and failed login attempts.
    return render(request, "accounts/login.html")





def forgot_password(request):

    if request.method == "POST":

        email = request.POST.get("email", "").strip().lower()

        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, "Please enter a valid email address.")
            return render(request, "accounts/forgot_password.html")

        customer = User.objects.filter(
            email__iexact=email,
            is_admin=False,
            is_superuser=False
        ).first()

        if not customer:
            messages.error(
                request,
                "No account found with this email address."
            )
            return render(request, "accounts/forgot_password.html")

        if not customer.is_active:
            messages.error(
                request,
                "Your account is currently blocked. Please contact support."
            )
            return render(request, "accounts/forgot_password.html")

        try:
            generate_and_send_otp(
                customer.email,
                EmailVerification.Purpose.PASSWORD_RESET
            )

            request.session["pending_password_reset"] = {
                "email": customer.email
            }

            request.session.pop("password_reset_verified", None)

            request.session.set_expiry(600)

            messages.success(
                request,
                "Verification code sent successfully!"
            )

            return redirect("accounts:verify_otp")

        except Exception:
            messages.error(
                request,
                "Unable to send verification code. Please try again."
            )

    return render(request, "accounts/forgot_password.html")




def verify_otp(request):
    pending_email_change = request.session.get("pending_email_change")
    pending_signup = request.session.get("pending_signup")
    pending_password_reset = request.session.get("pending_password_reset")

    # Handle email change verification first
    if pending_email_change:

        if (
            not request.user.is_authenticated
            or pending_email_change.get("user_id") != request.user.id
        ):
            request.session.pop("pending_email_change", None)
            messages.error(
                request,
                "Your email change session has expired. Please try again."
            )
            return redirect("accounts:customer_login")

        email = pending_email_change["email"]
        purpose = EmailVerification.Purpose.EMAIL_CHANGE

    elif pending_signup:
        email = pending_signup["email"]
        purpose = EmailVerification.Purpose.SIGNUP

    elif pending_password_reset:
        email = pending_password_reset["email"]
        purpose = EmailVerification.Purpose.PASSWORD_RESET

    else:
        messages.error(
            request,
            "Your verification session has expired. Please try again."
        )
        return redirect("accounts:customer_login")

    if request.method == "POST":
        entered_otp = request.POST.get("otp", "").strip()

        if len(entered_otp) != 6 or not entered_otp.isdigit():
            messages.error(
                request,
                "Please enter a valid 6-digit verification code."
            )
            return render(request, "accounts/verify_otp.html")

        is_verified, message = verify_otp_code(
            email,
            purpose,
            entered_otp
        )

        if is_verified:

            # Complete email change
            if purpose == EmailVerification.Purpose.EMAIL_CHANGE:

                if User.objects.filter(
                    email__iexact=email
                ).exclude(pk=request.user.pk).exists():

                    request.session.pop("pending_email_change", None)
                    messages.error(
                        request,
                        "This email address is already registered."
                    )
                    return redirect("accounts:customer_profile")

                with transaction.atomic():
                    user = User.objects.select_for_update().get(
                        pk=request.user.pk
                    )
                    user.email = email
                    user.save(update_fields=["email"])

                request.session.pop("pending_email_change", None)

                messages.success(
                    request,
                    "Your email address has been updated successfully."
                )
                return redirect("accounts:customer_profile")

            # Complete signup verification
            elif purpose == EmailVerification.Purpose.SIGNUP:
                request.session["signup_email_verified"] = email
                messages.success(request, message)
                return redirect("accounts:set_password")

            # Complete password reset verification
            elif purpose == EmailVerification.Purpose.PASSWORD_RESET:
                request.session["password_reset_verified"] = email
                messages.success(
                    request,
                    "Email verified successfully. You can now reset your password."
                )
                return redirect("accounts:set_password")

        messages.error(request, message)

    return render(request, "accounts/verify_otp.html")



def set_password(request):

    pending_signup = request.session.get("pending_signup")
    verified_signup_email = request.session.get(
        "signup_email_verified"
    )

    pending_password_reset = request.session.get(
        "pending_password_reset"
    )
    verified_reset_email = request.session.get(
        "password_reset_verified"
    )

    # PASSWORD RESET FLOW
    if pending_password_reset and verified_reset_email:

        email = pending_password_reset["email"]

        if email != verified_reset_email:
            messages.error(
                request,
                "Password reset verification failed."
            )
            return redirect("accounts:forgot_password")

        customer = User.objects.filter(
            email__iexact=email,
            is_admin=False,
            is_superuser=False,
            is_active=True
        ).first()

        if not customer:
            messages.error(
                request,
                "Customer account not found or unavailable."
            )
            return redirect("accounts:forgot_password")

        if request.method == "POST":

            password = request.POST.get("password", "")
            confirm_password = request.POST.get(
                "confirm_password", ""
            )

            if password != confirm_password:
                messages.error(request, "Passwords do not match.")
                return render(request, "accounts/set_password.html")

            try:
                validate_password(password, customer)
            except ValidationError as error:
                for message in error.messages:
                    messages.error(request, message)

                return render(
                    request,
                    "accounts/set_password.html"
                )

            customer.set_password(password)
            customer.save(update_fields=["password"])

            # Clear password-reset session data
            request.session.pop("pending_password_reset", None)
            request.session.pop("password_reset_verified", None)

            messages.success(
                request,
                "Your password has been reset successfully. Please log in."
            )

            return redirect("accounts:customer_login")

        return render(
            request,
            "accounts/set_password.html"
        )

    # SIGNUP FLOW
    if not pending_signup or not verified_signup_email:
        messages.error(
            request,
            "Please complete email verification before setting your password."
        )
        return redirect("accounts:customer_signup")

    if pending_signup["email"] != verified_signup_email:
        messages.error(
            request,
            "Email verification failed. Please sign up again."
        )
        return redirect("accounts:customer_signup")

    if User.objects.filter(email=verified_signup_email).exists():
        messages.error(
            request,
            "An account with this email already exists."
        )
        return redirect("accounts:customer_login")

    if request.method == "POST":

        password = request.POST.get("password", "")
        confirm_password = request.POST.get("confirm_password", "")

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, "accounts/set_password.html")

        try:
            validate_password(password)
        except ValidationError as error:
            for message in error.messages:
                messages.error(request, message)

            return render(
                request,
                "accounts/set_password.html"
            )

        user = User.objects.create_user(
            email=verified_signup_email,
            password=password,
            full_name=pending_signup["full_name"],
            is_admin=False,
            is_staff=False,
            is_active=True
        )

        login(
            request,
            user,
            backend="django.contrib.auth.backends.ModelBackend"
        )

        request.session.pop("pending_signup", None)
        request.session.pop("signup_email_verified", None)

        messages.success(
            request,
            "Your Shristi account has been created successfully!"
        )

        return redirect("storefront:home")

    return render(
        request,
        "accounts/set_password.html"
    )


from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.password_validation import validate_password


def google_set_password(request):

    if not request.user.is_authenticated:
        return redirect("accounts:customer_login")

    if not request.session.get("google_password_setup"):
        return redirect("storefront:home")

    if request.method == "POST":

        password = request.POST.get("password", "")
        confirm_password = request.POST.get("confirm_password", "")

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(
                request,
                "accounts/google_set_password.html"
            )

        try:
            validate_password(password, request.user)
        except ValidationError as error:
            for message in error.messages:
                messages.error(request, message)

            return render(
                request,
                "accounts/google_set_password.html"
            )

        request.user.set_password(password)
        request.user.save()

        update_session_auth_hash(request, request.user)

        request.session.pop("google_password_setup", None)

        messages.success(
            request,
            "Your password has been created successfully!"
        )

        return redirect("storefront:home")

    return render(
        request,
        "accounts/google_set_password.html"
    )


@login_required(login_url="accounts:customer_login")
def change_password(request):

    if request.method == "POST":

        current_password = request.POST.get("current_password", "")
        new_password = request.POST.get("new_password", "")
        confirm_password = request.POST.get("confirm_password", "")

        # Check whether all fields are filled
        if not current_password or not new_password or not confirm_password:
            messages.error(request, "Please fill in all password fields.")

            return render(
                request,
                "accounts/change_password.html"
            )

        # Verify current password
        if not request.user.check_password(current_password):
            messages.error(request, "Your current password is incorrect.")

            return render(
                request,
                "accounts/change_password.html"
            )

        # Check whether new password matches confirmation
        if new_password != confirm_password:
            messages.error(request, "New passwords do not match.")

            return render(
                request,
                "accounts/change_password.html"
            )

        # Prevent reusing the current password
        if request.user.check_password(new_password):
            messages.error(
                request,
                "Your new password must be different from your current password."
            )

            return render(
                request,
                "accounts/change_password.html"
            )

        # Validate new password using Django validators
        try:
            validate_password(new_password, request.user)

        except ValidationError as error:

            for message in error.messages:
                messages.error(request, message)

            return render(
                request,
                "accounts/change_password.html"
            )

        # Update password
        user = request.user
        user.set_password(new_password)
        user.save(update_fields=["password"])

        # Keep the user logged in
        update_session_auth_hash(request, user)

        messages.success(
            request,
            "Your password has been changed successfully!"
        )

        return redirect("accounts:customer_profile")

    return render(
        request,
        "accounts/change_password.html"
    )


@login_required(login_url="accounts:customer_login")
def request_email_change(request):

    if request.method == "POST":

        new_email = request.POST.get("email", "").strip().lower()

        # Validate email format
        try:
            validate_email(new_email)
        except ValidationError:
            messages.error(request, "Please enter a valid email address.")
            return render(request, "accounts/email_change.html")

        # Prevent using the current email
        if new_email == request.user.email.lower():
            messages.error(
                request,
                "This is already your current email address."
            )
            return render(request, "accounts/email_change.html")

        # Check whether another account already uses this email
        if User.objects.filter(email__iexact=new_email).exists():
            messages.error(
                request,
                "An account with this email already exists."
            )
            return render(request, "accounts/email_change.html")

        try:
            generate_and_send_otp(
                new_email,
                EmailVerification.Purpose.EMAIL_CHANGE
            )

            request.session["pending_email_change"] = {
                "email": new_email,
                "user_id": request.user.id,
            }

            request.session.set_expiry(600)

            messages.success(
                request,
                "Verification code sent to your new email address."
            )

            return redirect("accounts:verify_otp")

        except Exception:
            messages.error(
                request,
                "Unable to send verification code. Please try again.")

    return render(request, "accounts/email_change.html")


@login_required(login_url="accounts:customer_login")
def customer_profile(request):

    return render(
        request,
        "accounts/profile.html",
        {
            "profile_user": request.user
        }
    )


@login_required(login_url="storefront:home")
@require_POST
def customer_logout(request):

    logout(request)

    messages.success(
        request,
        "You have been logged out successfully."
    )

    return redirect("storefront:home")


@login_required(login_url="accounts:customer_login")
def edit_profile(request):

    if request.method == "POST":

        full_name = request.POST.get("full_name", "").strip()
        profile_image = request.FILES.get("profile_image")

        if not full_name:
            messages.error(request, "Full name is required.")

        elif len(full_name) > 150:
            messages.error(request, "Name cannot exceed 150 characters.")

        else:
            user = request.user

            # Keep the old image name before replacing it.
            old_image_name = (
                user.profile_image.name
                if user.profile_image
                else None
            )

            user.full_name = full_name

            if profile_image:
                user.profile_image = profile_image

            user.save()

            # Delete the old image only after the new image is saved.
            if (
                profile_image
                and old_image_name
                and old_image_name != user.profile_image.name
            ):
                user.profile_image.storage.delete(old_image_name)

            messages.success(
                request,
                "Your profile has been updated successfully!"
            )

            return redirect("accounts:customer_profile")

    return render(
        request,
        "accounts/edit_profile.html",
        {"profile_user": request.user}
    )


# REMOVE PROFILE IMAGE

@login_required(login_url="accounts:customer_login")
@require_POST
def remove_profile_image(request):

    user = request.user

    if user.profile_image:

        # Delete the image from the configured media storage.
        user.profile_image.delete(save=False)

        # Update the database field.
        user.save(update_fields=["profile_image"])

        messages.success(
            request,
            "Your profile picture has been removed successfully."
        )

    else:
        messages.info(
            request,
            "You don't have a profile picture to remove."
        )

    return redirect("accounts:edit_profile")


# ADDRESS MANAGEMENT


@login_required(login_url="accounts:customer_login")
def address_list(request):

    addresses = Address.objects.filter(
        user=request.user
    ).order_by("-is_default", "-created_at")

    return render(
        request,
        "accounts/address_list.html",
        {
            "addresses": addresses
        }
    )


@login_required(login_url="accounts:customer_login")
def add_address(request):

    if request.method == "POST":

        form = AddressForm(request.POST)

        if form.is_valid():

            with transaction.atomic():

                address = form.save(commit=False)
                address.user = request.user

                if address.is_default or not Address.objects.filter(
                    user=request.user
                ).exists():

                    Address.objects.filter(
                        user=request.user,
                        is_default=True
                    ).update(is_default=False)

                    address.is_default = True

                address.save()

            messages.success(
                request,
                "Address added successfully!"
            )

            return redirect("accounts:address_list")

    else:
        form = AddressForm()

    return render(
        request,
        "accounts/address_form.html",
        {
            "form": form,
            "page_title": "Add New Address",
            "button_text": "Save Address",
        }
    )


@login_required(login_url="accounts:customer_login")
def edit_address(request, address_id):

    address = get_object_or_404(
        Address,
        id=address_id,
        user=request.user
    )

    if request.method == "POST":

        form = AddressForm(
            request.POST,
            instance=address
        )

        if form.is_valid():

            with transaction.atomic():

                updated_address = form.save(commit=False)

                if updated_address.is_default:

                    Address.objects.filter(
                        user=request.user,
                        is_default=True
                    ).exclude(
                        id=address.id
                    ).update(is_default=False)

                updated_address.save()

            messages.success(
                request,
                "Address updated successfully!"
            )

            return redirect("accounts:address_list")

    else:
        form = AddressForm(instance=address)

    return render(
        request,
        "accounts/address_form.html",
        {
            "form": form,
            "page_title": "Edit Address",
            "button_text": "Update Address",
        }
    )


@login_required(login_url="accounts:customer_login")
def delete_address(request, address_id):

    address = get_object_or_404(
        Address,
        id=address_id,
        user=request.user
    )

    if request.method == "POST":

        address.delete()

        messages.success(
            request,
            "Address deleted successfully!"
        )

        return redirect("accounts:address_list")

    return render(
        request,
        "accounts/delete_address.html",
        {
            "address": address
        }
    )



@admin_required
def customer_create(request):

    if request.method == "POST":
        form = CustomerCreateForm(request.POST, request.FILES)

        if form.is_valid():

            customer = User.objects.create_user(
                email=form.cleaned_data["email"],
                password=form.cleaned_data["password"],
                full_name=form.cleaned_data["full_name"],
            )

            profile_image = form.cleaned_data.get("profile_image")

            if profile_image:
                customer.profile_image = profile_image
                customer.save(update_fields=["profile_image"])

            messages.success(
                request,
                "Customer account created successfully."
            )

            return redirect(
                "accounts:customer_detail",
                customer_id=customer.id
            )

    else:
        form = CustomerCreateForm()

    return render(
        request,
        "shristi_admin/customer_form.html",
        {
            "form": form,
            "page_title": "Add Customer",
            "button_text": "Create Customer",
            "is_edit": False,
        }
    )


@admin_required
def customer_update(request, customer_id):

    customer = get_object_or_404(
        User,
        id=customer_id,
        is_admin=False,
        is_superuser=False
    )

    if request.method == "POST":

        form = CustomerUpdateForm(
            request.POST,
            request.FILES,
            customer=customer
        )

        if form.is_valid():

            customer.full_name = form.cleaned_data["full_name"]
            customer.email = form.cleaned_data["email"]
            customer.is_active = form.cleaned_data["is_active"]

            new_profile_image = form.cleaned_data.get("profile_image")
            remove_profile_image = (
                request.POST.get("remove_profile_image") == "on"
            )

            old_profile_image_name = (
                customer.profile_image.name
                if customer.profile_image
                else None
            )

            # Replace the existing image with the new image.
            if new_profile_image:

                customer.profile_image = new_profile_image
                customer.save()

                # Delete the previous image after the new one is saved.
                if old_profile_image_name:
                    customer.profile_image.storage.delete(
                        old_profile_image_name
                    )

            # Remove the existing image if requested.
            elif remove_profile_image:

                customer.profile_image = None
                customer.save()

                if old_profile_image_name:
                    customer.profile_image.storage.delete(
                        old_profile_image_name
                    )

            else:
                customer.save()

            messages.success(
                request,
                "Customer details updated successfully."
            )

            return redirect(
                "accounts:customer_detail",
                customer_id=customer.id
            )

    else:

        form = CustomerUpdateForm(
            initial={
                "full_name": customer.full_name,
                "email": customer.email,
                "is_active": customer.is_active,
            },
            customer=customer
        )

    return render(
        request,
        "shristi_admin/customer_form.html",
        {
            "form": form,
            "customer": customer,
            "page_title": "Edit Customer",
            "button_text": "Update Customer",
            "is_edit": True,
        }
    )


@admin_required
def customer_delete(request, customer_id):

    customer = get_object_or_404(
        User,
        id=customer_id,
        is_admin=False,
        is_superuser=False
    )

    if request.method == "POST":

        customer_name = customer.full_name or customer.email

        customer.delete()

        messages.success(
            request,
            f"Customer '{customer_name}' deleted successfully."
        )

        return redirect("accounts:customer_list")

    return render(
        request,
        "shristi_admin/customer_delete_confirm.html",
        {
            "customer": customer,
        }
    )


@admin_required
def admin_customer_address_create(request, customer_id):

    customer = get_object_or_404(
        User,
        id=customer_id,
        is_admin=False,
        is_superuser=False
    )

    if request.method == "POST":

        form = AddressForm(request.POST)

        if form.is_valid():

            with transaction.atomic():

                address = form.save(commit=False)
                address.user = customer

                if address.is_default:
                    Address.objects.filter(
                        user=customer
                    ).update(is_default=False)

                address.save()

            messages.success(
                request,
                "Customer address added successfully."
            )

            return redirect(
                "accounts:customer_detail",
                customer_id=customer.id
            )

    else:
        form = AddressForm()

    return render(
        request,
        "shristi_admin/customer_address_form.html",
        {
            "form": form,
            "customer": customer,
            "page_title": "Add Customer Address",
            "button_text": "Add Address",
        }
    )

@admin_required
def admin_customer_address_update(request, customer_id, address_id):

    customer = get_object_or_404(
        User,
        id=customer_id,
        is_admin=False,
        is_superuser=False
    )

    address = get_object_or_404(
        Address,
        id=address_id,
        user=customer
    )

    if request.method == "POST":

        form = AddressForm(
            request.POST,
            instance=address
        )

        if form.is_valid():

            with transaction.atomic():

                updated_address = form.save(commit=False)

                if updated_address.is_default:
                    Address.objects.filter(
                        user=customer
                    ).exclude(
                        id=address.id
                    ).update(is_default=False)

                updated_address.save()

            messages.success(
                request,
                "Customer address updated successfully."
            )

            return redirect(
                "accounts:customer_detail",
                customer_id=customer.id
            )

    else:
        form = AddressForm(instance=address)

    return render(
        request,
        "shristi_admin/customer_address_form.html",
        {
            "form": form,
            "customer": customer,
            "address": address,
            "page_title": "Edit Customer Address",
            "button_text": "Update Address",
        }
    )

@admin_required
def admin_customer_address_delete(request, customer_id, address_id):

    customer = get_object_or_404(
        User,
        id=customer_id,
        is_admin=False,
        is_superuser=False
    )

    address = get_object_or_404(
        Address,
        id=address_id,
        user=customer
    )

    if request.method == "POST":

        address.delete()

        messages.success(
            request,
            "Customer address deleted successfully."
        )

        return redirect(
            "accounts:customer_detail",
            customer_id=customer.id
        )

    return render(
        request,
        "shristi_admin/customer_address_delete_confirm.html",
        {
            "customer": customer,
            "address": address,
        }
    )
