
from .services import get_wishlist


def wishlist_context(request):
    """Provide wishlist data for the current customer."""

    if not request.user.is_authenticated:
        return {
            "wishlist_product_ids": set(),
            "wishlist_count": 0,
        }

    wishlist_products = get_wishlist(request)

    wishlist_product_ids = {
        product.id for product in wishlist_products
    }

    return {
        "wishlist_product_ids": wishlist_product_ids,
        "wishlist_count": len(wishlist_product_ids),
    }
