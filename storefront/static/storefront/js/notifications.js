
/* ================= POPUP NOTIFICATIONS ================= */

document.addEventListener("DOMContentLoaded", function () {

    const notifications = document.querySelectorAll(".notification");

    notifications.forEach(function (notification) {

        if (notification.dataset.initialized === "true") {
            return;
        }

        notification.dataset.initialized = "true";

        let dismissTimer;

        function dismissNotification() {

            if (notification.classList.contains("hide")) {
                return;
            }

            clearTimeout(dismissTimer);

            notification.classList.add("hide");

            setTimeout(function () {
                notification.remove();
            }, 500);
        }

        // Close button
        const closeButton = notification.querySelector(".notification-close");

        if (closeButton) {
            closeButton.addEventListener("click", function (event) {
                event.preventDefault();
                event.stopPropagation();

                dismissNotification();
            });
        }

        // Automatically dismiss after 4 seconds
        dismissTimer = setTimeout(dismissNotification, 4000);

    });

});
