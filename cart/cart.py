
from decimal import Decimal

from products.models import Product


class Cart:
    """
    Session-based shopping cart for Shristi.
    """

    def __init__(self, request):
        self.session = request.session
        self.session_key = "cart"

        self.cart = self.session.get(self.session_key, {})

    def _save(self):
        self.session[self.session_key] = self.cart
        self.session.modified = True

    def add(self, product, quantity=1, override_quantity=False):
        try:
            quantity = int(quantity)
        except (ValueError, TypeError):
            raise ValueError("Invalid product quantity.")

        if quantity < 1:
            raise ValueError("Quantity must be at least 1.")

        if not product.is_active or not product.category.is_active:
            raise ValueError("This product is unavailable.")

        if product.stock <= 0:
            raise ValueError("This product is out of stock.")

        product_id = str(product.id)

        if override_quantity:
            new_quantity = quantity
        else:
            new_quantity = self.cart.get(product_id, 0) + quantity

        if new_quantity > product.stock:
            raise ValueError(
                f"Only {product.stock} units are available."
            )

        self.cart[product_id] = new_quantity
        self._save()

    def update_quantity(self, product_id, quantity):
        try:
            quantity = int(quantity)
        except (ValueError, TypeError):
            raise ValueError("Invalid product quantity.")

        if quantity < 1:
            raise ValueError("Quantity must be at least 1.")

        product = Product.objects.filter(
            id=product_id,
            is_active=True,
            category__is_active=True
        ).first()

        if not product:
            raise ValueError("Product is unavailable.")

        if quantity > product.stock:
            raise ValueError(
                f"Only {product.stock} units are available."
            )

        product_id = str(product.id)

        if product_id not in self.cart:
            raise ValueError("Product not found in cart.")

        self.cart[product_id] = quantity
        self._save()

    def remove(self, product_id):
        product_id = str(product_id)

        if product_id in self.cart:
            del self.cart[product_id]
            self._save()

    def clear(self):
        self.cart = {}
        self._save()

    def __iter__(self):
        products = Product.objects.filter(
            id__in=self.cart.keys(),
            is_active=True,
            category__is_active=True
        ).select_related("category")

        product_map = {
            str(product.id): product
            for product in products
        }

        for product_id, quantity in self.cart.items():
            product = product_map.get(product_id)

            if product is None:
                continue

            unit_price = product.selling_price

            yield {
                "product": product,
                "quantity": quantity,
                "unit_price": unit_price,
                "total_price": unit_price * quantity,
            }

    def __len__(self):
        return sum(self.cart.values())

    def get_total_price(self):
        return sum(
            (item["total_price"] for item in self),
            Decimal("0.00")
        )
