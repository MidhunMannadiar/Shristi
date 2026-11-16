
const sidebar = document.getElementById("sidebar");
const menuToggle = document.getElementById("menuToggle");

if (sidebar && menuToggle) {

    menuToggle.addEventListener("click", function () {
        sidebar.classList.toggle("active");
    });

}
