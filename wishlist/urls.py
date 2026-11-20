from django.urls import path
from . import views

app_name = "wishlist"

urlpatterns = [
    path("", views.wishlist_detail, name="wishlist_detail"),
    path("add/<int:product_id>/", views.add_wishlist, name="add_wishlist"),
    path("remove/<int:product_id>/", views.remove_wishlist, name="remove_wishlist"),
]
