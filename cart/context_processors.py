
from .cart import Cart


def cart_count(request):

    if request.user.is_authenticated:
        return {
            "cart_count": len(Cart(request))
        }

    return {
        "cart_count": 0
    }
