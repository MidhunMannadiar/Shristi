
from .services import get_wishlist


def wishlist_context(request):
    wishlist_products = get_wishlist(request)

    wishlist_product_ids = {
        product.id for product in wishlist_products
    }

    return {
        "wishlist_product_ids": wishlist_product_ids,
        "wishlist_count": len(wishlist_product_ids),
    }
