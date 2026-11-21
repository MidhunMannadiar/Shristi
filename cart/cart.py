
from django.db import transaction
from products.models import Product
from .models import CartItem


class Cart:

    def __init__(self, request):
        self.user = request.user

    def _get_active_product(self, product_id):
        return Product.objects.filter(
            id=product_id,
            is_active=True,
            category__is_active=True
        ).first()

    def add(self, product, quantity=1, override_quantity=False):

        try:
            quantity = int(quantity)
        except (TypeError, ValueError):
            raise ValueError("Invalid quantity.")

        if quantity < 1:
            raise ValueError("Quantity must be at least 1.")

        if not self.user.is_authenticated:
            raise ValueError("Please log in to use your cart.")

        product = self._get_active_product(product.id)

        if not product:
            raise ValueError("This product is currently unavailable.")

        with transaction.atomic():

            cart_item, created = CartItem.objects.get_or_create(
                user=self.user,
                product=product,
                defaults={"quantity": quantity}
            )

            if not created:

                new_quantity = (
                    quantity
                    if override_quantity
                    else cart_item.quantity + quantity
                )

                if new_quantity > product.stock:
                    raise ValueError(
                        f"Only {product.stock} units are available."
                    )

                cart_item.quantity = new_quantity
                cart_item.save(update_fields=["quantity", "updated_at"])

            elif quantity > product.stock:
                cart_item.delete()

                raise ValueError(
                    f"Only {product.stock} units are available."
                )

        return cart_item

    def update_quantity(self, product_id, quantity):

        try:
            quantity = int(quantity)
        except (TypeError, ValueError):
            raise ValueError("Invalid quantity.")

        if quantity < 1:
            raise ValueError("Quantity must be at least 1.")

        product = self._get_active_product(product_id)

        if not product:
            raise ValueError("This product is currently unavailable.")

        if quantity > product.stock:
            raise ValueError(
                f"Only {product.stock} units are available."
            )

        cart_item = CartItem.objects.filter(
            user=self.user,
            product=product
        ).first()

        if not cart_item:
            raise ValueError("Product not found in your cart.")

        cart_item.quantity = quantity
        cart_item.save(update_fields=["quantity", "updated_at"])

        return cart_item

    def remove(self, product):
        CartItem.objects.filter(
            user=self.user,
            product_id=product.id
        ).delete()

    def clear(self):
        CartItem.objects.filter(user=self.user).delete()

    def __iter__(self):
        """Iterate through the customer's cart items."""

        cart_items = CartItem.objects.filter(
            user=self.user
        ).select_related(
            "product",
            "product__category"
        )

        for item in cart_items:

            yield {
                "product": item.product,
                "quantity": item.quantity,
                "unit_price": item.product.selling_price,
                "total_price": item.subtotal,
                "is_out_of_stock": item.product.stock <= 0,
            }

    def __len__(self):

        from django.db.models import Sum

        total_quantity = CartItem.objects.filter(
            user=self.user
        ).aggregate(
            total=Sum("quantity")
        )["total"]

        return total_quantity or 0

    def get_total_price(self):
        """Calculate the total price of available products only."""

        from django.db.models import (
            Sum,
            F,
            DecimalField,
            ExpressionWrapper
        )

        total = CartItem.objects.filter(
            user=self.user,
            product__stock__gt=0
        ).aggregate(
            total=Sum(
                ExpressionWrapper(
                    F("product__selling_price") * F("quantity"),
                    output_field=DecimalField()
                )
            )
        )["total"]

        return total or 0
