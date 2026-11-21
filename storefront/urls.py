from django.urls import path
from . import views

app_name = "storefront"

urlpatterns = [
    path("", views.home, name="home"),
    path("shop/", views.shop, name="shop"),
    path(
    "categories/",
    views.all_categories,
    name="all_categories"
    ),

    # Live Search Suggestions
    path(
        "search-suggestions/",
        views.search_suggestions,
        name="search_suggestions"
    ),

    path("product/<slug:slug>/", views.product_detail, name="product_detail"),
]