
from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("admin/login/", views.admin_login, name="admin_login"),
    path("admin/dashboard/", views.admin_dashboard, name="admin_dashboard"),
# Customer Management

path(
    "admin/customers/",
    views.customer_list,
    name="customer_list"
),

path(
    "admin/customers/add/",
    views.customer_create,
    name="customer_create"
),

path(
    "admin/customers/<int:customer_id>/",
    views.customer_detail,
    name="customer_detail"
),

path(
    "admin/customers/<int:customer_id>/edit/",
    views.customer_update,
    name="customer_update"
),

path(
    "admin/customers/<int:customer_id>/delete/",
    views.customer_delete,
    name="customer_delete"
),

path(
    "admin/customers/<int:customer_id>/<str:action>/",
    views.customer_status_confirm,
    name="customer_status"
),

path(
    "admin/customers/<int:customer_id>/addresses/add/",
    views.admin_customer_address_create,
    name="admin_customer_address_create"
),

path(
    "admin/customers/<int:customer_id>/addresses/<int:address_id>/edit/",
    views.admin_customer_address_update,
    name="admin_customer_address_update"
),

path(
    "admin/customers/<int:customer_id>/addresses/<int:address_id>/delete/",
    views.admin_customer_address_delete,
    name="admin_customer_address_delete"
),
    path("admin/logout/", views.admin_logout, name="admin_logout"),

    path("signup/", views.customer_signup, name="customer_signup"),
    path("login/", views.customer_login, name="customer_login"),

    path("forgot-password/", views.forgot_password, name="forgot_password"),
    path("verify-otp/", views.verify_otp, name="verify_otp"),
    path("set-password/", views.set_password, name="set_password"),

    path(
        "google/set-password/",
        views.google_set_password,
        name="google_set_password"
    ),

    path("profile/", views.customer_profile, name="customer_profile"),
    path("profile/edit/", views.edit_profile, name="edit_profile"),
    path(
    "profile/remove-image/",
    views.remove_profile_image,
    name="remove_profile_image"
),
    path(
    "profile/change-password/",
    views.change_password,
    name="change_password"
    ),
    path("logout/", views.customer_logout, name="customer_logout"),
    path(
    "profile/change-email/",
    views.request_email_change,
    name="request_email_change"
),
# ADDRESS MANAGEMENT

    path(
        "addresses/",
        views.address_list,
        name="address_list"
    ),

    path(
        "addresses/add/",
        views.add_address,
        name="add_address"
    ),

    path(
        "addresses/edit/<int:address_id>/",
        views.edit_address,
        name="edit_address"
    ),

    path(
        "addresses/delete/<int:address_id>/",
        views.delete_address,
        name="delete_address"
    ),


]
