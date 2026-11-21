
const searchToggle = document.getElementById("searchToggle");
const searchPanel = document.getElementById("searchPanel");

if (searchToggle && searchPanel) {
    searchToggle.addEventListener("click", function () {
        const isOpen = searchPanel.classList.toggle("active");

        searchToggle.setAttribute("aria-expanded", isOpen);
    });
}


// =====================================
// MOBILE FILTER DRAWER
// =====================================

const mobileFilterToggle = document.getElementById("mobileFilterToggle");
const closeFilterDrawer = document.getElementById("closeFilterDrawer");
const shopSidebar = document.getElementById("shopSidebar");
const filterDrawerOverlay = document.getElementById("filterDrawerOverlay");

// Open drawer
if (mobileFilterToggle && shopSidebar && filterDrawerOverlay) {

    mobileFilterToggle.addEventListener("click", function () {

        shopSidebar.classList.add("active");
        filterDrawerOverlay.classList.add("active");

        document.body.classList.add("filter-drawer-open");

    });

}

// Close drawer
function closeMobileFilterDrawer() {

    if (shopSidebar && filterDrawerOverlay) {

        shopSidebar.classList.remove("active");
        filterDrawerOverlay.classList.remove("active");

        document.body.classList.remove("filter-drawer-open");

    }

}

// Close button
if (closeFilterDrawer) {

    closeFilterDrawer.addEventListener("click", closeMobileFilterDrawer);

}

// Close when clicking overlay
if (filterDrawerOverlay) {

    filterDrawerOverlay.addEventListener("click", closeMobileFilterDrawer);

}

// Close using Escape key
document.addEventListener("keydown", function (event) {

    if (event.key === "Escape") {
        closeMobileFilterDrawer();
    }

});


/* =====================================
   PRODUCT IMAGE GALLERY
===================================== */

const mainProductImage = document.getElementById("mainProductImage");
const productThumbnails = document.querySelectorAll(".product-thumbnail");

productThumbnails.forEach(function (thumbnail) {

    thumbnail.addEventListener("click", function () {

        const selectedImage = this.dataset.image;

        if (mainProductImage && selectedImage) {
            mainProductImage.src = selectedImage;
        }

        // Remove active class from all thumbnails
        productThumbnails.forEach(function (item) {
            item.classList.remove("active");
        });

        // Highlight selected thumbnail
        this.classList.add("active");

    });

});






/* =========================================
   PRODUCT DETAIL - STOCK-BASED QUANTITY
========================================= */

document.addEventListener("DOMContentLoaded", function () {

    const productQuantity = document.getElementById("productQuantity");
    const cartQuantity = document.getElementById("cartQuantity");

    const minusButton = document.getElementById("quantityMinus");
    const plusButton = document.getElementById("quantityPlus");

    const addToCartButton = document.getElementById("addToCartButton");
    const cartForm = document.querySelector(".add-to-cart-form");

    if (!productQuantity || !cartQuantity) {
        return;
    }

    const stock = Number(productQuantity.dataset.stock);

    function updateQuantity(value) {

        let quantity = Number(value);

        if (!Number.isInteger(quantity) || quantity < 1) {
            quantity = 1;
        }

        if (quantity > stock) {
            quantity = stock;
        }

        productQuantity.value = quantity;
        cartQuantity.value = quantity;

        if (minusButton) {
            minusButton.disabled = quantity <= 1 || stock === 0;
        }

        if (plusButton) {
            plusButton.disabled = stock === 0;
        }

        if (addToCartButton) {
            addToCartButton.disabled = stock === 0;
        }
    }

    // DECREASE QUANTITY
    minusButton?.addEventListener("click", function () {

        const currentQuantity = Number(productQuantity.value);

        if (currentQuantity > 1) {
            updateQuantity(currentQuantity - 1);
        }

    });

    // INCREASE QUANTITY
    plusButton?.addEventListener("click", function () {

        const currentQuantity = Number(productQuantity.value);

        if (currentQuantity >= stock) {
            showStockToast(`Only ${stock} items left in stock!`);
            return;
        }

        updateQuantity(currentQuantity + 1);

    });

    // MANUAL QUANTITY INPUT
    productQuantity.addEventListener("input", function () {

        if (productQuantity.value === "") {
            return;
        }

        const quantity = Number(productQuantity.value);

        if (!Number.isInteger(quantity) || quantity < 1) {
            showStockToast("Please enter a valid quantity.");
            return;
        }

        if (quantity > stock) {
            updateQuantity(stock);
            showStockToast(`Only ${stock} items left in stock!`);
            return;
        }

        updateQuantity(quantity);

    });

    // INPUT BLUR
    productQuantity.addEventListener("blur", function () {

        if (productQuantity.value === "") {
            updateQuantity(stock > 0 ? 1 : 0);
        }

    });

    // ADD TO CART VALIDATION
    cartForm?.addEventListener("submit", function (event) {

        const quantity = Number(productQuantity.value);

        if (
            stock <= 0 ||
            !Number.isInteger(quantity) ||
            quantity < 1 ||
            quantity > stock
        ) {

            event.preventDefault();

            showStockToast(
                stock <= 0
                    ? "This product is out of stock."
                    : `Only ${stock} items left in stock!`
            );

            return;
        }

        cartQuantity.value = quantity;

    });

    // INITIALIZE
    if (stock > 0) {
        updateQuantity(1);
    } else {
        productQuantity.value = 0;
        cartQuantity.value = 0;

        if (addToCartButton) {
            addToCartButton.disabled = true;
        }
    }

});





/* ================= POPUP NOTIFICATIONS ================= */

document.addEventListener("DOMContentLoaded", function () {

    const notifications = document.querySelectorAll(".notification");

    notifications.forEach(function (notification) {

        setTimeout(function () {

            notification.classList.add("hide");

            setTimeout(function () {
                notification.remove();
            }, 500);

        }, 4000);

    });

});


/* ================= PRODUCT IMAGE ZOOM ================= */

document.addEventListener("DOMContentLoaded", function () {

    const viewer = document.querySelector(".product-image-viewer");
    const imageContainer = document.querySelector(".product-main-image");
    const mainImage = document.getElementById("mainProductImage");
    const zoomPreview = document.getElementById("productZoomPreview");

    // Stop if the product image elements are unavailable
    if (!viewer || !imageContainer || !mainImage || !zoomPreview) {
        return;
    }

    // Disable zoom on touch devices
    if (!window.matchMedia("(hover: hover) and (pointer: fine)").matches) {
        return;
    }

    const zoomLevel = 1.5;
    const lensSize = 120;

    // Create magnifier lens
    const lens = document.createElement("div");
    lens.className = "product-zoom-lens";

    imageContainer.appendChild(lens);

    // Create a duplicate image inside the preview
    const previewImage = document.createElement("img");
    previewImage.alt = "";

    previewImage.style.width = "100%";
    previewImage.style.height = "100%";
    previewImage.style.objectFit = "cover";
    previewImage.style.display = "block";
    previewImage.style.transform = `scale(${zoomLevel})`;
    previewImage.style.transformOrigin = "center center";

    zoomPreview.appendChild(previewImage);

    function updatePreviewImage() {
        previewImage.src = mainImage.src;
    }

    updatePreviewImage();

    // Update preview when a thumbnail changes the main image
    const imageObserver = new MutationObserver(function () {
        updatePreviewImage();
    });

    imageObserver.observe(mainImage, {
        attributes: true,
        attributeFilter: ["src"]
    });

    function moveLens(event) {

        const rect = imageContainer.getBoundingClientRect();

        const lensWidth = lens.offsetWidth;
        const lensHeight = lens.offsetHeight;

        let x = event.clientX - rect.left;
        let y = event.clientY - rect.top;

        // Keep the lens inside the image
        let left = Math.max(
            0,
            Math.min(x - lensWidth / 2, rect.width - lensWidth)
        );

        let top = Math.max(
            0,
            Math.min(y - lensHeight / 2, rect.height - lensHeight)
        );

        lens.style.left = `${left}px`;
        lens.style.top = `${top}px`;

        // Set zoom origin based on lens centre
        const centerX = left + lensWidth / 2;
        const centerY = top + lensHeight / 2;

        const originX = (centerX / rect.width) * 100;
        const originY = (centerY / rect.height) * 100;

        previewImage.style.transformOrigin =
            `${originX}% ${originY}%`;
    }

    imageContainer.addEventListener("mouseenter", function () {

        if (!mainImage.complete || !mainImage.naturalWidth) {
            return;
        }

        viewer.classList.add("zoom-active");
        lens.classList.add("active");

    });

    imageContainer.addEventListener("mousemove", moveLens);

    imageContainer.addEventListener("mouseleave", function () {

        viewer.classList.remove("zoom-active");
        lens.classList.remove("active");

    });

});




/* =====================================
   LIVE SEARCH SUGGESTIONS
===================================== */

const liveSearchInput = document.getElementById("liveSearchInput");
const searchSuggestions = document.getElementById("searchSuggestions");

if (liveSearchInput && searchSuggestions) {

    let searchTimeout;
    let selectedIndex = -1;
    let currentRequest = null;

    const searchLoading = document.getElementById("searchLoading");

    // Get currently displayed suggestion items
    function getSuggestionItems() {
        return Array.from(
            searchSuggestions.querySelectorAll(".search-suggestion-item")
        );
    }

    // Update keyboard selection
    function updateSelection() {

        const items = getSuggestionItems();

        items.forEach((item, index) => {
            const isSelected = index === selectedIndex;

            item.classList.toggle("selected", isSelected);
            item.setAttribute("aria-selected", isSelected);

            if (isSelected) {
                item.scrollIntoView({
                    block: "nearest"
                });
            }
        });
    }

    // Reset keyboard selection
    function resetSelection() {
        selectedIndex = -1;
        updateSelection();
    }

    // Display loading message
    function showLoading() {
        searchSuggestions.innerHTML = "";
        searchSuggestions.appendChild(searchLoading);

        searchLoading.hidden = false;
        searchSuggestions.hidden = false;
    }

    // Hide loading message
    function hideLoading() {
        searchLoading.hidden = true;
    }

    // Handle input
    liveSearchInput.addEventListener("input", function () {

        const query = this.value.trim();

        clearTimeout(searchTimeout);

        // Cancel previous request
        if (currentRequest) {
            currentRequest.abort();
            currentRequest = null;
        }

        resetSelection();

        if (query.length < 2) {
            searchSuggestions.innerHTML = "";
            searchSuggestions.hidden = true;
            return;
        }

        showLoading();

        searchTimeout = setTimeout(async function () {

            const controller = new AbortController();
            currentRequest = controller;

            try {

                const response = await fetch(
                    `/search-suggestions/?q=${encodeURIComponent(query)}`,
                    { signal: controller.signal }
                );

                if (!response.ok) {
                    throw new Error("Search request failed");
                }

                const data = await response.json();

                // Ignore outdated search results
                if (liveSearchInput.value.trim() !== query) {
                    return;
                }

                searchSuggestions.innerHTML = "";

                if (data.results.length === 0) {

                    const message = document.createElement("div");
                    message.className = "search-suggestion-message";
                    message.textContent = "No products found.";

                    searchSuggestions.appendChild(message);

                } else {

                    data.results.forEach(product => {

                        const item = document.createElement("a");

                        item.href = product.url;
                        item.className = "search-suggestion-item";
                        item.setAttribute("role", "option");
                        item.setAttribute("aria-selected", "false");

                        const image = document.createElement("img");
                        image.src = product.image || "/static/images/placeholder.png";
                        image.alt = product.name;

                        const info = document.createElement("div");
                        info.className = "search-suggestion-info";

                        const name = document.createElement("span");
                        name.className = "search-suggestion-name";
                        name.textContent = product.name;

                        const price = document.createElement("span");
                        price.className = "search-suggestion-price";
                        price.textContent = `₹${product.price}`;

                        info.appendChild(name);
                        info.appendChild(price);

                        item.appendChild(image);
                        item.appendChild(info);

                        searchSuggestions.appendChild(item);
                    });
                }

                searchSuggestions.hidden = false;
                resetSelection();

            } catch (error) {

                if (error.name !== "AbortError") {
                    console.error("Live search error:", error);
                }

            } finally {

                if (currentRequest === controller) {
                    currentRequest = null;
                }

                hideLoading();
            }

        }, 300);
    });

    // Keyboard navigation
    liveSearchInput.addEventListener("keydown", function (event) {

        const items = getSuggestionItems();

        if (event.key === "ArrowDown" && items.length > 0) {

            event.preventDefault();

            if (searchSuggestions.hidden) {
                searchSuggestions.hidden = false;
            }

            selectedIndex = (selectedIndex + 1) % items.length;
            updateSelection();
        }

        else if (event.key === "ArrowUp" && items.length > 0) {

            event.preventDefault();

            selectedIndex = selectedIndex <= 0
                ? items.length - 1
                : selectedIndex - 1;

            updateSelection();
        }

        else if (event.key === "Enter" && selectedIndex >= 0) {

            event.preventDefault();

            if (items[selectedIndex]) {
                window.location.href = items[selectedIndex].href;
            }
        }

        else if (event.key === "Escape") {

            searchSuggestions.hidden = true;
            resetSelection();
        }
    });

    // Close suggestions when clicking outside
    document.addEventListener("click", function (event) {

        if (
            !liveSearchInput.contains(event.target) &&
            !searchSuggestions.contains(event.target)
        ) {
            searchSuggestions.hidden = true;
            resetSelection();
        }
    });

    // Show suggestions again on focus
    liveSearchInput.addEventListener("focus", function () {

        if (
            this.value.trim().length >= 2 &&
            searchSuggestions.children.length > 0
        ) {
            searchSuggestions.hidden = false;
        }
    });
}


document.addEventListener("DOMContentLoaded", function () {

    const categoriesGrid = document.getElementById("categoriesGrid");
    const viewAllBtn = document.getElementById("viewAllCategoriesBtn");
    const viewAllContainer = document.getElementById("viewAllCategoriesContainer");

    if (!categoriesGrid || !viewAllBtn || !viewAllContainer) {
        return;
    }

    const categories = categoriesGrid.querySelectorAll(".category-card");

    const visibleCount = 4;
    let expanded = false;

    if (categories.length <= visibleCount) {
        viewAllContainer.style.display = "none";
        return;
    }

    function updateCategories() {

        categories.forEach((category, index) => {
            category.style.display =
                expanded || index < visibleCount ? "" : "none";
        });

        viewAllBtn.innerHTML = expanded
            ? 'Show Less <span aria-hidden="true">↑</span>'
            : 'View All Categories <span aria-hidden="true">→</span>';
    }

    viewAllBtn.addEventListener("click", function () {

        expanded = !expanded;
        updateCategories();

    });

    updateCategories();

});

function showStockToast(message) {
    let container = document.querySelector(".notification-container");

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
        toast.classList.add("hide");
        setTimeout(() => toast.remove(), 500);
    };

    toast.querySelector(".notification-close").addEventListener("click", closeToast);

    setTimeout(closeToast, 4000);
}