
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
