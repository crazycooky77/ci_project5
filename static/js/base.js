window.addEventListener("DOMContentLoaded", () => {
    // Restrict the width of the hyperlink element on the logo to the logo image width
    let logo = document.getElementsByClassName("nav-right")[0].firstElementChild
    logo.style.width = window.getComputedStyle(logo.firstChild).getPropertyValue("width")

    let scrollBtn = document.getElementById("footer-top-link");
    window.onscroll = function () {
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


function newSignup() {
    let newsModal = document.getElementById('news-modal')
    newsModal.style.display = 'block';

    let newsSpan = document.getElementById('news-modal').getElementsByClassName('modal-close')[0]
    newsSpan.onclick = function() {
        newsModal.style.display = 'none';
    }

    window.onclick = function(event) {
        if (!(newsModal.contains(event.target))) {
            newsModal.style.display = 'none';
        }
    }
}