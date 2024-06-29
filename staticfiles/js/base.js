$(document).ready(function () {
    // Restrict the width of the hyperlink element on the logo to the logo image width
    let logo = document.getElementsByClassName("nav-left")[0].firstElementChild
    logo.style.width = window.getComputedStyle(logo.firstChild).getPropertyValue("width")

    let scrollBtn = document.getElementById("footer-top-link");
    window.onscroll = function() {
        if (document.body.scrollTop > 20 || document.documentElement.scrollTop > 20) {
            scrollBtn.style.visibility = "unset";
        } else {
            scrollBtn.style.visibility = "hidden";
        }
    }
})


function topScroll() {
    document.body.scrollTop = 0; // For Safari
    document.documentElement.scrollTop = 0; // For Chrome, Firefox, IE and Opera
}