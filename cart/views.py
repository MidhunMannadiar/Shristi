
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q

from products.models import Product
from .cart import Cart
from .models import CartItem


@login_required
def cart_detail(request):
    """Display the logged-in customer's shopping cart."""

    # Remove unavailable products from the database cart
    CartItem.objects.filter(
        user=request.user
    ).filter(
        Q(product__is_active=False) |
        Q(product__category__is_active=False)
    ).delete()

    cart = Cart(request)
    cart_items = list(cart)

    context = {
        "cart_items": cart_items,
        "cart_total": cart.get_total_price(),
        "cart_count": len(cart),
    }

    return render(request, "cart/cart.html", context)



@require_POST
def add_to_cart(request, product_id):
    """Add a product to the authenticated customer's cart."""

    product = get_object_or_404(
        Product,
        id=product_id,
        is_active=True,
        category__is_active=True
    )

    quantity = request.POST.get("quantity", 1)

    # Guest user: temporarily preserve the requested product.
    if not request.user.is_authenticated:
        try:
            quantity = int(quantity)

            if quantity < 1:
                raise ValueError

            if quantity > product.stock:
                messages.error(
                    request,
                    f"Only {product.stock} units are available."
                )
                return redirect(
                    "storefront:product_detail",
                    slug=product.slug
                )

        except (ValueError, TypeError):
            messages.error(request, "Please select a valid quantity.")
            return redirect(
                "storefront:product_detail",
                slug=product.slug
            )

        request.session["pending_add_to_cart"] = {
            "product_id": product.id,
            "quantity": quantity,
        }

        messages.info(
            request,
            "Please log in to add this product to your shopping bag."
        )

        return redirect("accounts:customer_login")

    # Authenticated user: use the existing cart functionality.
    cart = Cart(request)

    try:
        cart.add(product, quantity)

        from wishlist.services import remove_from_wishlist

        remove_from_wishlist(request, product)

        messages.success(
            request,
            f"{product.name} added to your shopping bag."
        )

    except ValueError as error:
        messages.error(request, str(error))

    return redirect("cart:cart_detail")



@login_required
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


@login_required
@require_POST
def remove_from_cart(request, product_id):
    """Remove a product from the customer's cart."""

    cart = Cart(request)

    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)

    messages.success(
        request,
        "Product removed from your shopping bag."
    )

    return redirect("cart:cart_detail")


@login_required
@require_POST
def save_for_later(request, product_id):
    """Move a product from cart to wishlist."""

    product = get_object_or_404(
        Product,
        id=product_id,
        is_active=True,
        category__is_active=True
    )

    cart_item = CartItem.objects.filter(
        user=request.user,
        product=product
    ).first()

    if not cart_item:
        messages.error(
            request,
            "Product not found in your shopping bag."
        )
        return redirect("cart:cart_detail")

    from wishlist.services import add_to_wishlist

    add_to_wishlist(request, product)

    cart = Cart(request)
    cart.remove(product)

    messages.success(
        request,
        f"{product.name} saved to your wishlist."
    )

    return redirect("cart:cart_detail")


@login_required
@require_POST
def update_cart_ajax(request, product_id):
    """Update cart quantity using AJAX."""

    cart = Cart(request)
    quantity = request.POST.get("quantity")

    try:
        quantity = int(quantity)

        if quantity < 0:
            raise ValueError("Invalid quantity.")

        product = get_object_or_404(
            Product,
            id=product_id
        )

        if quantity == 0:
            cart.remove(product)

            return JsonResponse({
                "success": True,
                "removed": True,
                "cart_count": len(cart),
                "cart_total": str(cart.get_total_price()),
            })

        cart.update_quantity(product_id, quantity)

        return JsonResponse({
            "success": True,
            "removed": False,
            "quantity": quantity,
            "item_subtotal": str(
                product.selling_price * quantity
            ),
            "cart_total": str(cart.get_total_price()),
            "cart_count": len(cart),
        })

    except (ValueError, TypeError) as error:
        return JsonResponse({
            "success": False,
            "message": str(error),
        }, status=400)

    except Product.DoesNotExist:
        CartItem.objects.filter(
            user=request.user,
            product_id=product_id
        ).delete()

        return JsonResponse({
            "success": True,
            "removed": True,
            "cart_count": len(cart),
            "cart_total": str(cart.get_total_price()),
        })
