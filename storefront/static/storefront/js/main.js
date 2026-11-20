
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
   PRODUCT DETAIL - QUANTITY SELECTOR
========================================= */

document.addEventListener("DOMContentLoaded", function () {

    const productQuantity = document.getElementById("productQuantity");
    const cartQuantity = document.getElementById("cartQuantity");
    const minusButton = document.getElementById("quantityMinus");
    const plusButton = document.getElementById("quantityPlus");

    if (!productQuantity || !cartQuantity) {
        return;
    }

    const minimum = parseInt(productQuantity.min) || 1;
    const maximum = parseInt(productQuantity.max) || 0;

    function updateQuantity(value) {

        let quantity = parseInt(value);

        if (isNaN(quantity)) {
            quantity = minimum;
        }

        quantity = Math.max(minimum, Math.min(quantity, maximum));

        productQuantity.value = quantity;
        cartQuantity.value = quantity;

        // Disable buttons at quantity limits
        if (minusButton) {
            minusButton.disabled = quantity <= minimum;
        }

        if (plusButton) {
            plusButton.disabled = quantity >= maximum;
        }
    }

    // Decrease quantity
    if (minusButton) {
        minusButton.addEventListener("click", function () {

            const current = parseInt(productQuantity.value) || minimum;

            if (current > minimum) {
                updateQuantity(current - 1);
            }

        });
    }

    // Increase quantity
    if (plusButton) {
        plusButton.addEventListener("click", function () {

            const current = parseInt(productQuantity.value) || minimum;

            if (current < maximum) {
                updateQuantity(current + 1);
            }

        });
    }

    // Handle manual quantity input
    productQuantity.addEventListener("input", function () {
        if (productQuantity.value !== "") {
            const value = parseInt(productQuantity.value);

            if (!isNaN(value)) {
                cartQuantity.value = Math.max(
                    minimum,
                    Math.min(value, maximum)
                );
            }
        }
    });

    productQuantity.addEventListener("change", function () {
        updateQuantity(productQuantity.value);
    });

    // Initial quantity
    if (maximum >= minimum) {
        updateQuantity(productQuantity.value);
    } else {
        productQuantity.disabled = true;

        if (minusButton) minusButton.disabled = true;
        if (plusButton) plusButton.disabled = true;
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
