
document.addEventListener("DOMContentLoaded", function () {

    let cropper = null;
    let currentInput = null;
    let selectedFile = null;
    let imageURL = null;
    let isCropping = false;

    const updatingInputs = new WeakSet();

    // Create cropping modal
    const modal = document.createElement("div");

    modal.className = "shristi-cropper-modal";

    modal.innerHTML = `
        <div class="cropper-container-box">

            <div class="cropper-header">
                <h2>Crop Image</h2>
                <button type="button" class="cropper-close">&times;</button>
            </div>

            <div class="cropper-image-wrapper">
                <img id="cropperImage" src="" alt="Image to crop">
            </div>

            <div class="cropper-controls">
                <button type="button" id="zoomIn">Zoom In +</button>
                <button type="button" id="zoomOut">Zoom Out -</button>
                <button type="button" id="rotateLeft">Rotate Left</button>
                <button type="button" id="rotateRight">Rotate Right</button>
                <button type="button" id="resetCrop">Reset</button>
            </div>

            <div class="cropper-actions">
                <button type="button" class="cropper-close">Cancel</button>
                <button type="button" class="crop-confirm">Crop & Confirm</button>
            </div>

        </div>
    `;

    document.body.appendChild(modal);

    const cropperImage = modal.querySelector("#cropperImage");
    const confirmButton = modal.querySelector(".crop-confirm");

    // Open cropping modal
    function openCropper(file, input) {

        if (typeof Cropper === "undefined") {
            alert("Cropper.js is not loaded. Please check your script imports.");
            input.value = "";
            return;
        }

        if (isCropping) {
            return;
        }

        isCropping = true;

        currentInput = input;
        selectedFile = file;

        imageURL = URL.createObjectURL(file);

        cropperImage.onload = function () {

            if (cropper) {
                cropper.destroy();
            }

            cropper = new Cropper(cropperImage, {
                aspectRatio: 1,
                viewMode: 1,
                dragMode: "move",
                autoCropArea: 0.85,
                responsive: true,
                background: false,
                guides: true,
                center: true,
                movable: true,
                zoomable: true,
                rotatable: true,
                scalable: false
            });

        };

        cropperImage.onerror = function () {
            alert("This image format cannot be opened by your browser.");
            closeCropper(true);
        };

        cropperImage.src = imageURL;

        modal.classList.add("active");
    }

    // Close modal and release resources
    function closeCropper(clearInput = false) {

        if (clearInput && currentInput) {
            currentInput.value = "";
        }

        modal.classList.remove("active");

        if (cropper) {
            cropper.destroy();
            cropper = null;
        }

        cropperImage.onload = null;
        cropperImage.onerror = null;
        cropperImage.removeAttribute("src");

        if (imageURL) {
            URL.revokeObjectURL(imageURL);
            imageURL = null;
        }

        currentInput = null;
        selectedFile = null;
        isCropping = false;
        confirmButton.disabled = false;
    }

    // Close buttons
    modal.querySelectorAll(".cropper-close").forEach(button => {

        button.addEventListener("click", function () {
            closeCropper(true);
        });

    });

    // Zoom controls
    modal.querySelector("#zoomIn").addEventListener("click", function () {

        if (cropper) {
            cropper.zoom(0.1);
        }

    });

    modal.querySelector("#zoomOut").addEventListener("click", function () {

        if (cropper) {
            cropper.zoom(-0.1);
        }

    });

    // Rotate controls
    modal.querySelector("#rotateLeft").addEventListener("click", function () {

        if (cropper) {
            cropper.rotate(-90);
        }

    });

    modal.querySelector("#rotateRight").addEventListener("click", function () {

        if (cropper) {
            cropper.rotate(90);
        }

    });

    // Reset crop
    modal.querySelector("#resetCrop").addEventListener("click", function () {

        if (cropper) {
            cropper.reset();
        }

    });

    // Confirm crop
    confirmButton.addEventListener("click", function () {

        if (!cropper || !currentInput || !selectedFile) {
            return;
        }

        confirmButton.disabled = true;

        const canvas = cropper.getCroppedCanvas({
            width: 1000,
            height: 1000,
            imageSmoothingEnabled: true,
            imageSmoothingQuality: "high"
        });

        if (!canvas) {
            alert("Unable to crop this image. Please try another image.");
            confirmButton.disabled = false;
            return;
        }

        const input = currentInput;
        const originalName = selectedFile.name;

        canvas.toBlob(function (blob) {

            if (!blob) {
                alert("Image cropping failed. Please try again.");
                confirmButton.disabled = false;
                return;
            }

            // Convert cropped image to JPEG
            const fileName = originalName.replace(/\.[^.]+$/, "") + ".jpg";

            const croppedFile = new File(
                [blob],
                fileName,
                {
                    type: "image/jpeg",
                    lastModified: Date.now()
                }
            );

            const dataTransfer = new DataTransfer();

            dataTransfer.items.add(croppedFile);

            // Assign cropped image to original file input
            updatingInputs.add(input);

            try {

                input.files = dataTransfer.files;

                input.dispatchEvent(
                    new Event("change", { bubbles: true })
                );

            } catch (error) {

                console.error("Unable to assign cropped image:", error);

                alert("Unable to update the image input. Please try again.");

                updatingInputs.delete(input);
                confirmButton.disabled = false;

                return;

            }

            updatingInputs.delete(input);

            closeCropper(false);

        }, "image/jpeg", 0.92);

    });

    // Detect image inputs
    const imageInputs = document.querySelectorAll(
        'input[type="file"][data-crop-image="true"]'
    );

    // Attach cropping functionality
    imageInputs.forEach(input => {

        input.addEventListener("change", function () {

            if (updatingInputs.has(this)) {
                return;
            }

            const file = this.files[0];

            if (!file) {
                return;
            }

            if (!file.type.startsWith("image/")) {

                alert("Please select a valid image file.");

                this.value = "";

                return;
            }

            openCropper(file, this);

        });

    });

    console.log("Shristi image cropper initialized.");
    console.log("Image inputs detected:", imageInputs.length);

});
