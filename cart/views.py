
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.http import JsonResponse
from products.models import Product
from .cart import Cart


def cart_detail(request):
    """Display the shopping cart."""

    cart = Cart(request)

    # Remove unavailable products from the session
    available_products = Product.objects.filter(
        id__in=cart.cart.keys(),
        is_active=True,
        category__is_active=True
    )

    available_ids = {str(product.id) for product in available_products}

    for product_id in list(cart.cart.keys()):
        if product_id not in available_ids:
            cart.remove(product_id)

    cart_items = list(cart)

    context = {
        "cart_items": cart_items,
        "cart_total": cart.get_total_price(),
        "cart_count": len(cart),
    }

    return render(request, "cart/cart.html", context)



@require_POST
def add_to_cart(request, product_id):
    """Add a product to cart and remove it from wishlist."""

    product = get_object_or_404(
        Product,
        id=product_id,
        is_active=True,
        category__is_active=True
    )

    cart = Cart(request)

    quantity = request.POST.get("quantity", 1)

    try:
        cart.add(product, quantity)

        # Remove product from wishlist after successful cart addition
        from wishlist.services import remove_from_wishlist

        remove_from_wishlist(request, product)

        messages.success(
            request,
            f"{product.name} added to your shopping bag."
        )

    except ValueError as error:
        messages.error(request, str(error))

    return redirect("cart:cart_detail")



@require_POST
def update_cart(request, product_id):
    """Update the quantity of a cart product."""

    cart = Cart(request)
    quantity = request.POST.get("quantity", 1)

    try:
        cart.update_quantity(product_id, quantity)
        messages.success(request, "Cart quantity updated.")

    except ValueError as error:
        messages.error(request, str(error))

    return redirect("cart:cart_detail")



@require_POST
def remove_from_cart(request, product_id):
    """Remove a product from the shopping cart."""

    cart = Cart(request)

    cart.remove(product_id)

    messages.success(request, "Product removed from your shopping bag.")

    return redirect("cart:cart_detail")



@require_POST
def save_for_later(request, product_id):
    """Move a product from cart to wishlist."""

    product = get_object_or_404(
        Product,
        id=product_id,
        is_active=True,
        category__is_active=True
    )

    cart = Cart(request)

    # Check whether the product exists in cart
    if str(product.id) not in cart.cart:
        messages.error(request, "Product not found in your shopping bag.")
        return redirect("cart:cart_detail")

    # Add product to wishlist
    from wishlist.services import add_to_wishlist

    add_to_wishlist(request, product)

    # Remove product from cart
    cart.remove(product.id)

    messages.success(
        request,
        f"{product.name} saved to your wishlist."
    )

    return redirect("cart:cart_detail")


@require_POST
def update_cart_ajax(request, product_id):
    cart = Cart(request)
    quantity = request.POST.get("quantity")

    try:
        quantity = int(quantity)

        if quantity < 0:
            raise ValueError("Invalid quantity.")

        if quantity == 0:
            cart.remove(product_id)

            return JsonResponse({
                "success": True,
                "removed": True,
                "cart_count": len(cart),
                "cart_total": str(cart.get_total_price()),
            })

        cart.update_quantity(product_id, quantity)

        product = Product.objects.get(
            id=product_id,
            is_active=True,
            category__is_active=True
        )

        return JsonResponse({
            "success": True,
            "removed": False,
            "quantity": quantity,
            "item_subtotal": str(product.selling_price * quantity),
            "cart_total": str(cart.get_total_price()),
            "cart_count": len(cart),
        })

    except (ValueError, TypeError) as error:
        return JsonResponse({
            "success": False,
            "message": str(error),
        }, status=400)

    except Product.DoesNotExist:
        cart.remove(product_id)

        return JsonResponse({
            "success": True,
            "removed": True,
            "cart_count": len(cart),
            "cart_total": str(cart.get_total_price()),
        })