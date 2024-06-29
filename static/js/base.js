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

    $("input[type='number']").each(function(){
        $(this).attr("onkeydown", "return event.keyCode !== 69")
    })
})


function topScroll() {
    document.body.scrollTop = 0; // For Safari
    document.documentElement.scrollTop = 0; // For Chrome, Firefox, IE and Opera
}


function newSignup() {
    let email = prompt("Enter your email to sign up to our newsletter:")
    let form = document.getElementById('news-signup-form')
    if (email !== null && email !== "") {
        let hidden_input = document.createElement('input')
        hidden_input.style.display = 'none'
        hidden_input.name = 'news_email'
        hidden_input.id = 'id_news_email'
        hidden_input.value = email
        form.appendChild(hidden_input)
        form.submit()
    }
}