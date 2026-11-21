
document.addEventListener("DOMContentLoaded", function () {

    const cartItems = document.querySelectorAll(".cart-item");

    const currency = (amount) => {
        return "₹" + Number(amount).toFixed(2);
    };


    /* =========================================
       HEADER CART COUNT
    ========================================= */

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


    /* =========================================
       EMPTY CART
    ========================================= */

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


    /* =========================================
       CUSTOM REMOVE CONFIRMATION MODAL
    ========================================= */

    const removeModal = document.getElementById(
        "removeConfirmationModal"
    );

    const cancelRemoveButton = document.getElementById(
        "cancelRemoveButton"
    );

    const cancelRemoveIcon = document.getElementById(
        "cancelRemoveIcon"
    );

    const confirmRemoveButton = document.getElementById(
        "confirmRemoveButton"
    );

    const removeProductImage = document.getElementById(
        "removeProductImage"
    );

    const removeProductName = document.getElementById(
        "removeProductName"
    );

    const removeProductPrice = document.getElementById(
        "removeProductPrice"
    );

    let pendingRemoveForm = null;


    // OPEN MODAL
    function openRemoveModal(form) {

        const item = form.closest(".cart-item");

        if (!item || !removeModal) return;

        pendingRemoveForm = form;

        const productName = item.querySelector(
            ".cart-item-details h3"
        );

        const productImage = item.querySelector(
            ".cart-item-image img"
        );

        const productPrice = item.querySelector(
            ".cart-item-price"
        );

        removeProductName.textContent =
            productName
                ? productName.textContent.trim()
                : "Selected product";

        removeProductPrice.textContent =
            productPrice
                ? productPrice.textContent.trim()
                : "";

        if (productImage) {

            removeProductImage.src = productImage.src;
            removeProductImage.alt = productImage.alt;
            removeProductImage.style.display = "block";

        } else {

            removeProductImage.removeAttribute("src");
            removeProductImage.alt = "";
            removeProductImage.style.display = "none";

        }

        removeModal.classList.add("active");
        removeModal.setAttribute("aria-hidden", "false");

        confirmRemoveButton.focus();
    }


    // CLOSE MODAL
    function closeRemoveModal() {

        if (!removeModal) return;

        removeModal.classList.remove("active");
        removeModal.setAttribute("aria-hidden", "true");

        pendingRemoveForm = null;
    }


    // CANCEL BUTTON
    cancelRemoveButton.addEventListener(
        "click",
        closeRemoveModal
    );


    // CLOSE ICON
    cancelRemoveIcon.addEventListener(
        "click",
        closeRemoveModal
    );


    // CLICK OUTSIDE MODAL
    removeModal.addEventListener("click", function (event) {

        if (event.target === removeModal) {
            closeRemoveModal();
        }

    });


    // ESCAPE KEY
    document.addEventListener("keydown", function (event) {

        if (
            event.key === "Escape" &&
            removeModal.classList.contains("active")
        ) {
            closeRemoveModal();
        }

    });


    // CONFIRM REMOVE BUTTON
    confirmRemoveButton.addEventListener("click", function () {

        if (!pendingRemoveForm) return;

        const form = pendingRemoveForm;

        confirmRemoveButton.disabled = true;
        confirmRemoveButton.textContent = "Removing...";

        closeRemoveModal();

        updateCart(form, 0).finally(function () {

            confirmRemoveButton.disabled = false;
            confirmRemoveButton.textContent = "Yes, Remove";

        });

    });


    /* =========================================
       AJAX CART UPDATE
    ========================================= */

    async function updateCart(form, quantity) {

        const item = form.closest(".cart-item");

        const input = form.querySelector(
            ".cart-quantity-input"
        );

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

                throw new Error(
                    data.message || "Unable to update cart."
                );

            }

            // UPDATE HEADER COUNT
            updateHeaderCount(data.cart_count);


            // REMOVE PRODUCT
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


            // UPDATE CART TOTAL
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


            // UPDATE CART ITEM COUNT
            const headingCount = document.querySelector(
                ".cart-section-heading span"
            );

            if (headingCount) {

                headingCount.textContent =
                    `${data.cart_count} item${data.cart_count === 1 ? "" : "s"}`;

            }

        } catch (error) {

            showStockToast(error.message);

            if (input) {
                input.value = input.defaultValue;
            }

        } finally {

            if (form.isConnected) {

                buttons.forEach(button => {
                    button.disabled = false;
                });

            }

        }

    }


    /* =========================================
       QUANTITY CONTROLS
    ========================================= */

    cartItems.forEach(function (item) {

        const form = item.querySelector(".cart-quantity-form");

        const minusButton = item.querySelector(".quantity-minus");

        const plusButton = item.querySelector(".quantity-plus");

        const quantityInput = item.querySelector(
            ".cart-quantity-input"
        );


        // SKIP OUT-OF-STOCK PRODUCTS
        if (!form || !minusButton || !plusButton || !quantityInput) {
            return;
        }


        // DECREASE QUANTITY
        minusButton.addEventListener("click", function () {

            const current = parseInt(quantityInput.value) || 0;

            if (current === 1) {

                openRemoveModal(form);

                return;

            }

            if (current > 1) {

                updateCart(form, current - 1);

            }

        });


        // INCREASE QUANTITY
        plusButton.addEventListener("click", function () {

            const current = parseInt(quantityInput.value) || 0;

            const maximum = parseInt(quantityInput.max) || 0;

            if (current >= maximum) {

                showStockToast(
                    `Only ${maximum} items left in stock!`
                );

                return;

            }

            updateCart(form, current + 1);

        });

    });

});


/* =========================================
   CART - STOCK WARNING TOAST
========================================= */

function showStockToast(message) {

    let container = document.querySelector(
        ".notification-container"
    );

    if (!container) {

        container = document.createElement("div");

        container.className = "notification-container";

        document.body.appendChild(container);

    }

    const toast = document.createElement("div");

    toast.className = "notification notification-warning";

    toast.innerHTML = `
        <span class="notification-icon">⚠</span>
        <span class="notification-text"></span>
        <button type="button" class="notification-close">&times;</button>
    `;

    toast.querySelector(".notification-text").textContent = message;

    container.appendChild(toast);


    const closeToast = () => {

        if (!toast.isConnected) return;

        toast.classList.add("hide");

        setTimeout(() => toast.remove(), 500);

    };


    toast.querySelector(".notification-close")
        .addEventListener("click", closeToast);

    setTimeout(closeToast, 4000);

}
