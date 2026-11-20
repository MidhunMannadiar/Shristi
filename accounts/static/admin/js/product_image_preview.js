
document.addEventListener("DOMContentLoaded", function () {

    // =====================================
    // MAIN PRODUCT IMAGE
    // =====================================

    const mainInput = document.getElementById("id_main_image");
    const mainPreview = document.getElementById("mainImagePreview");
    const mainPlaceholder = document.getElementById("mainImagePlaceholder");
    const mainRemoveButton = document.getElementById("removeMainImageButton");

    function setupImagePreview(input, preview, placeholder, removeButton) {

        if (!input || !preview || !placeholder || !removeButton) {
            return;
        }

        const originalImageUrl = preview.dataset.originalImage || "";
        const hasSavedImage = Boolean(originalImageUrl);

        let previewUrl = null;

        function updateRemoveButton() {
            removeButton.style.display =
                input.files.length > 0 || hasSavedImage
                    ? "inline-flex"
                    : "none";
        }

        // Select and preview image
        input.addEventListener("change", function () {

            const file = this.files[0];

            if (!file) {
                updateRemoveButton();
                return;
            }

            if (!file.type.startsWith("image/")) {
                alert("Please select a valid image file.");
                this.value = "";
                updateRemoveButton();
                return;
            }

            if (previewUrl) {
                URL.revokeObjectURL(previewUrl);
            }

            previewUrl = URL.createObjectURL(file);

            preview.src = previewUrl;
            preview.style.display = "block";
            placeholder.style.display = "none";

            updateRemoveButton();
        });

        // Remove image
        removeButton.addEventListener("click", function () {

            // Remove newly selected image
            if (input.files.length > 0) {

                input.value = "";

                if (previewUrl) {
                    URL.revokeObjectURL(previewUrl);
                    previewUrl = null;
                }

                if (hasSavedImage) {

                    preview.src = originalImageUrl;
                    preview.style.display = "block";
                    placeholder.style.display = "none";

                } else {

                    preview.src = "";
                    preview.style.display = "none";
                    placeholder.style.display = "flex";

                }

                updateRemoveButton();
                return;
            }

            // Remove saved image
            if (hasSavedImage) {

                const confirmed = confirm(
                    "Are you sure you want to remove this image?"
                );

                if (confirmed) {
                    preview.dataset.removeSavedImage = "true";

                    // Mark the image for removal on form submission.
                    const form = input.closest("form");

                    if (form) {
                        let marker = form.querySelector(
                            'input[name="remove_main_image"]'
                        );

                        if (!marker) {
                            marker = document.createElement("input");
                            marker.type = "hidden";
                            marker.name = "remove_main_image";
                            marker.value = "true";
                            form.appendChild(marker);
                        }
                    }

                    preview.src = "";
                    preview.style.display = "none";
                    placeholder.style.display = "flex";

                    hasSavedImage = false;
                    updateRemoveButton();
                }
            }
        });

        updateRemoveButton();

        window.addEventListener("beforeunload", function () {
            if (previewUrl) {
                URL.revokeObjectURL(previewUrl);
            }
        });
    }

    setupImagePreview(
        mainInput,
        mainPreview,
        mainPlaceholder,
        mainRemoveButton
    );


    // =====================================
    // PRODUCT GALLERY IMAGES
    // =====================================

    const galleryItems = document.querySelectorAll(".gallery-image-item");

    galleryItems.forEach(function (item) {

        const input = item.querySelector('input[type="file"]');
        const preview = item.querySelector(".gallery-image-preview");
        const placeholder = item.querySelector(".gallery-image-placeholder");
        const removeButton = item.querySelector(".remove-gallery-image-button");
        const deleteCheckbox = item.querySelector('input[type="checkbox"]');

        if (!input || !preview || !placeholder || !removeButton) {
            return;
        }

        const originalImageUrl = preview.dataset.originalImage || "";
        const hasSavedImage = Boolean(originalImageUrl);

        let previewUrl = null;

        function updateRemoveButton() {
            removeButton.style.display =
                input.files.length > 0 || hasSavedImage
                    ? "inline-flex"
                    : "none";
        }

        input.addEventListener("change", function () {

            const file = this.files[0];

            if (!file) {
                updateRemoveButton();
                return;
            }

            if (!file.type.startsWith("image/")) {
                alert("Please select a valid image file.");
                this.value = "";
                updateRemoveButton();
                return;
            }

            if (previewUrl) {
                URL.revokeObjectURL(previewUrl);
            }

            previewUrl = URL.createObjectURL(file);

            preview.src = previewUrl;
            preview.style.display = "block";
            placeholder.style.display = "none";

            if (deleteCheckbox) {
                deleteCheckbox.checked = false;
            }

            updateRemoveButton();
        });

        removeButton.addEventListener("click", function () {

            // Remove newly selected image
            if (input.files.length > 0) {

                input.value = "";

                if (previewUrl) {
                    URL.revokeObjectURL(previewUrl);
                    previewUrl = null;
                }

                if (hasSavedImage) {

                    preview.src = originalImageUrl;
                    preview.style.display = "block";
                    placeholder.style.display = "none";

                } else {

                    preview.src = "";
                    preview.style.display = "none";
                    placeholder.style.display = "flex";

                }

                updateRemoveButton();
                return;
            }

            // Mark existing gallery image for deletion
            if (hasSavedImage && deleteCheckbox) {

                const confirmed = confirm(
                    "Are you sure you want to remove this gallery image?"
                );

                if (confirmed) {

                    deleteCheckbox.checked = true;

                    preview.src = "";
                    preview.style.display = "none";
                    placeholder.style.display = "flex";

                    removeButton.style.display = "none";
                }
            }
        });

        updateRemoveButton();

        window.addEventListener("beforeunload", function () {
            if (previewUrl) {
                URL.revokeObjectURL(previewUrl);
            }
        });

    });

});
