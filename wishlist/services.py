
from wishlist.models import WishlistItem
from products.models import Product


WISHLIST_SESSION_KEY = "wishlist"


def get_wishlist(request):
    """
    Return wishlist products for authenticated and guest users.
    """

    if request.user.is_authenticated:
        wishlist_items = WishlistItem.objects.filter(
            user=request.user,
            product__is_active=True,
            product__category__is_active=True
        ).select_related("product", "product__category")

        return [item.product for item in wishlist_items]

    product_ids = request.session.get(WISHLIST_SESSION_KEY, [])

    products = Product.objects.filter(
        id__in=product_ids,
        is_active=True,
        category__is_active=True
    ).select_related("category")

    return list(products)


def add_to_wishlist(request, product):
    """
    Add a product to the user's wishlist.
    """

    if request.user.is_authenticated:
        WishlistItem.objects.get_or_create(
            user=request.user,
            product=product
        )
        return

    wishlist = request.session.get(WISHLIST_SESSION_KEY, [])

    product_id = str(product.id)

    if product_id not in wishlist:
        wishlist.append(product_id)

    request.session[WISHLIST_SESSION_KEY] = wishlist
    request.session.modified = True


def remove_from_wishlist(request, product):
    """
    Remove a product from the user's wishlist.
    """

    if request.user.is_authenticated:
        WishlistItem.objects.filter(
            user=request.user,
            product=product
        ).delete()
        return

    wishlist = request.session.get(WISHLIST_SESSION_KEY, [])

    product_id = str(product.id)

    if product_id in wishlist:
        wishlist.remove(product_id)

    request.session[WISHLIST_SESSION_KEY] = wishlist
    request.session.modified = True
