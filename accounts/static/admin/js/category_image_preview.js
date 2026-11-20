
document.addEventListener("DOMContentLoaded", function () {

    const imageInput = document.getElementById("id_image");
    const imagePreview = document.getElementById("categoryImagePreview");
    const imagePlaceholder = document.getElementById("categoryImagePlaceholder");
    const removeButton = document.getElementById("removeCategoryImageButton");
    const removeSavedImageForm = document.getElementById("removeSavedCategoryImageForm");

    if (!imageInput) return;

    const originalImageUrl = imagePreview.dataset.originalImage;
    const hasSavedImage = Boolean(originalImageUrl);

    let previewUrl = null;

    function updateRemoveButton() {
        removeButton.style.display =
            imageInput.files.length > 0 || hasSavedImage
                ? "inline-flex"
                : "none";
    }

    imageInput.addEventListener("change", function () {

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

        imagePreview.src = previewUrl;
        imagePreview.style.display = "block";
        imagePlaceholder.style.display = "none";

        updateRemoveButton();
    });

    removeButton.addEventListener("click", function () {

        // Remove newly selected image first
        if (imageInput.files.length > 0) {

            imageInput.value = "";

            if (previewUrl) {
                URL.revokeObjectURL(previewUrl);
                previewUrl = null;
            }

            if (hasSavedImage) {
                imagePreview.src = originalImageUrl;
                imagePreview.style.display = "block";
                imagePlaceholder.style.display = "none";
            } else {
                imagePreview.src = "";
                imagePreview.style.display = "none";
                imagePlaceholder.style.display = "flex";
            }

            updateRemoveButton();
            return;
        }

        // Remove previously saved image
        if (hasSavedImage && removeSavedImageForm) {

            const confirmed = confirm(
                "Are you sure you want to remove this category image?"
            );

            if (confirmed) {
                removeSavedImageForm.requestSubmit();
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
