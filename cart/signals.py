
from django.contrib import messages
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver

from products.models import Product
from .cart import Cart


@receiver(user_logged_in)
def add_pending_product_to_cart(sender, request, user, **kwargs):

    pending_add = request.session.get("pending_add_to_cart")

    if not pending_add:
        return

    product = Product.objects.filter(
        id=pending_add.get("product_id"),
        is_active=True,
        category__is_active=True
    ).first()

    if not product:
        request.session.pop("pending_add_to_cart", None)

        messages.error(
            request,
            "This product is no longer available."
        )
        return

    try:
        cart = Cart(request)

        cart.add(
            product,
            pending_add.get("quantity", 1)
        )

        from wishlist.services import remove_from_wishlist

        remove_from_wishlist(request, product)

        request.session.pop("pending_add_to_cart", None)

        messages.success(
            request,
            f"{product.name} added to your shopping bag."
        )

    except (ValueError, TypeError) as error:
        messages.error(request, str(error))
