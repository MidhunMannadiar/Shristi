
document.addEventListener("DOMContentLoaded", function () {

    const notifications = document.querySelectorAll(".notification");

    notifications.forEach(function (notification) {

        const closeButton = notification.querySelector(".notification-close");

        function hideNotification() {
            if (notification.classList.contains("hide")) {
                return;
            }

            notification.classList.add("hide");

            setTimeout(function () {
                notification.remove();
            }, 500);
        }

        // Automatically hide after 4 seconds
        const timer = setTimeout(hideNotification, 4000);

        // Close manually
        if (closeButton) {
            closeButton.addEventListener("click", function () {
                clearTimeout(timer);
                hideNotification();
            });
        }

    });

});
