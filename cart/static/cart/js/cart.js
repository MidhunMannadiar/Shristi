
document.addEventListener("DOMContentLoaded", function () {
    const cartItems = document.querySelectorAll(".cart-item");

    const currency = (amount) => {
        return "₹" + Number(amount).toFixed(2);
    };

    function updateHeaderCount(count) {
        const cartLink = document.querySelector(
            '.header-icon[aria-label="Shopping bag"]'
        );

        if (!cartLink) return;

        let badge = cartLink.querySelector(".cart-count");

        if (count > 0) {
            if (!badge) {
                badge = document.createElement("span");
                badge.className = "cart-count";
                cartLink.appendChild(badge);
            }

            badge.textContent = count;
        } else if (badge) {
            badge.remove();
        }
    }

    function showEmptyCart() {
        const cartLayout = document.querySelector(".cart-layout");
        if (!cartLayout) return;

        const shopLink = cartLayout.querySelector(
            ".continue-shopping"
        );

        const shopUrl = shopLink ? shopLink.href : "#";

        cartLayout.outerHTML = `
            <div class="empty-cart">
                <div class="empty-cart-icon">
                    <i class="fa-solid fa-bag-shopping"></i>
                </div>
                <h2>Your Shopping Bag Is Empty</h2>
                <p>
                    Discover thoughtfully handcrafted pieces
                    and find something special for your home.
                </p>
                <a href="${shopUrl}" class="empty-cart-button">
                    Explore Collection
                </a>
            </div>
        `;
    }

    async function updateCart(form, quantity) {
        const item = form.closest(".cart-item");
        const input = form.querySelector(".cart-quantity-input");
        const buttons = form.querySelectorAll(".quantity-btn");

        buttons.forEach(button => button.disabled = true);

        try {
            const formData = new FormData(form);
            formData.set("quantity", quantity);

            const response = await fetch(form.action, {
                method: "POST",
                body: formData,
                headers: {
                    "X-Requested-With": "XMLHttpRequest"
                }
            });

            const data = await response.json();

            if (!response.ok || !data.success) {
                throw new Error(data.message || "Unable to update cart.");
            }

            updateHeaderCount(data.cart_count);

            if (data.removed) {
                item.remove();

                const remainingItems =
                    document.querySelectorAll(".cart-item");

                if (remainingItems.length === 0) {
                    showEmptyCart();
                }
            } else {
                input.value = data.quantity;

                item.querySelector(".item-subtotal").textContent =
                    currency(data.item_subtotal);
            }

            const subtotal = currency(data.cart_total);

            const subtotalElement =
                document.getElementById("cartSubtotal");

            const totalElement =
                document.getElementById("cartGrandTotal");

            if (subtotalElement) {
                subtotalElement.textContent = subtotal;
            }

            if (totalElement) {
                totalElement.textContent = subtotal;
            }

            const itemCount = document.querySelectorAll(".cart-item").length;
            const headingCount = document.querySelector(
                ".cart-section-heading span"
            );

            if (headingCount) {
                headingCount.textContent =
                    `${data.cart_count} item${data.cart_count === 1 ? "" : "s"}`;
            }

        } catch (error) {
            alert(error.message);
            input.value = input.defaultValue;
        } finally {
            if (form.isConnected) {
                buttons.forEach(button => button.disabled = false);
            }
        }
    }

    cartItems.forEach(function (item) {
        const form = item.querySelector(".cart-quantity-form");
        const minusButton = item.querySelector(".quantity-minus");
        const plusButton = item.querySelector(".quantity-plus");
        const quantityInput = item.querySelector(".cart-quantity-input");

        minusButton.addEventListener("click", function () {
            const current = parseInt(quantityInput.value) || 0;

            if (current > 0) {
                updateCart(form, current - 1);
            }
        });

        plusButton.addEventListener("click", function () {
            const current = parseInt(quantityInput.value) || 0;
            const maximum = parseInt(quantityInput.max) || 0;

            if (current < maximum) {
                updateCart(form, current + 1);
            }
        });
    });
});
