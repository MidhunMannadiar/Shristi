
from wishlist.models import WishlistItem


def get_wishlist(request):
    """
    Return wishlist products belonging to the logged-in customer.
    """

    if not request.user.is_authenticated:
        return []

    wishlist_items = WishlistItem.objects.filter(
        user=request.user,
        product__is_active=True,
        product__category__is_active=True
    ).select_related(
        "product",
        "product__category"
    )

    return [item.product for item in wishlist_items]


def add_to_wishlist(request, product):
    """
    Add a product to the logged-in customer's wishlist.
    """

    if not request.user.is_authenticated:
        return False

    WishlistItem.objects.get_or_create(
        user=request.user,
        product=product
    )

    return True


def remove_from_wishlist(request, product):
    """
    Remove a product from the logged-in customer's wishlist.
    """

    if not request.user.is_authenticated:
        return False

    WishlistItem.objects.filter(
        user=request.user,
        product=product
    ).delete()

    return True
