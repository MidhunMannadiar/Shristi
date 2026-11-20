from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_POST

from products.models import Product
from .services import (
    get_wishlist,
    add_to_wishlist,
    remove_from_wishlist,
)


def wishlist_detail(request):
    wishlist_products = get_wishlist(request)

    return render(
        request,
        "wishlist/wishlist.html",
        {
            "wishlist_products": wishlist_products,
        }
    )


@require_POST
def add_wishlist(request, product_id):
    product = get_object_or_404(
        Product,
        id=product_id,
        is_active=True,
        category__is_active=True
    )

    add_to_wishlist(request, product)

    messages.success(request, "Product added to your wishlist.")

    return redirect(request.META.get("HTTP_REFERER", "wishlist:wishlist_detail"))


@require_POST

@require_POST
def remove_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    remove_from_wishlist(request, product)

    messages.success(request, "Product removed from your wishlist.")

    return redirect(
        request.META.get(
            "HTTP_REFERER",
            "wishlist:wishlist_detail"
        )
    )

