window.addEventListener("DOMContentLoaded", () => {
    logoResize()
    scrollOpt()
    baseU500()
    baseO500()
})

window.addEventListener("load", () => {
    logoResize()
    baseU500()
    baseO500()
})

window.addEventListener("resize", () => {
    logoResize()
    baseU500()
    baseO500()
})


function logoResize() {
    // Restrict the width of the hyperlink element on the logo to the logo image width
    let logo = document.getElementsByClassName("nav-right")[0]
    let width = window.getComputedStyle(logo).getPropertyValue("width")
    logo.querySelector('a').style.width = width
    logo.querySelector('img').style.width = width
}


function scrollOpt() {
    let scrollBtn = document.getElementById("footer-top-link");
    window.onscroll = function () {
        if (document.body.scrollTop > 20 || document.documentElement.scrollTop > 20) {
            scrollBtn.style.visibility = "unset";
        } else {
            scrollBtn.style.visibility = "hidden";
        }
    }
}


function topScroll() {
    document.body.scrollTop = 0; // For Safari
    document.documentElement.scrollTop = 0; // For Chrome, Firefox, IE and Opera
}


function modals(buttonId, modalId) {
    let button = document.getElementById(buttonId)
    let modal = document.getElementById(modalId)
    modal.style.display = 'block';
    let span = modal.getElementsByClassName('modal-close')[0]
    span.onclick = function() {
        modal.style.display = 'none';
    }
    window.onclick = function(event) {
        if (!(modal.contains(event.target)) && button !== event.target) {
            modal.style.display = 'none';
        }
    }
    window.onresize = function() {
        modal.style.display = 'none';
    }
}



// function mailTo() {
//     let mailButton = document.getElementsByClassName('nav-support')[0].querySelector('a')
//     let newsModal = document.getElementById('sup-mailto-modal')
//     newsModal.style.display = 'block';
//     let newsSpan = document.getElementById('news-modal').getElementsByClassName('modal-close')[0]
//     newsSpan.onclick = function() {
//         newsModal.style.display = 'none';
//     }
//     window.onclick = function(event) {
//         if (!(newsModal.contains(event.target)) && mailButton !== event.target) {
//             newsModal.style.display = 'none';
//         }
//     }
//     window.onresize = function() {
//         newsModal.style.display = 'none';
//     }
// }


function baseU500() {
    if (window.innerWidth <= 800) {
        let navIcons = document.getElementsByClassName('nav-left')[0]
        if (navIcons.querySelector('button')) {
            navIcons.querySelector('button').lastChild.textContent = ''
        }
        let navAnchors = navIcons.querySelectorAll('a')
        for (let i = 0; i < navAnchors.length; i++) {
            navAnchors[i].lastChild.textContent = ''
        }
        let navButtons = document.getElementsByClassName('nav-buttons')[0].querySelectorAll('button')
        for (let j = 0; j < navButtons.length; j++) {
            if (navButtons[j].title === 'All Products') {
                navButtons[j].innerHTML = 'All'
            }
            else if (navButtons[j].title === "New Products") {
                navButtons[j].innerHTML = 'New'
            }
        }
        let navPipes = document.getElementsByClassName('nav-buttons')[0]
        navPipes.innerHTML = navPipes.innerHTML.replace(/\|/g, '')
    }
}


function baseO500() {
    if (window.innerWidth > 800) {
        let navIcons = document.getElementsByClassName('nav-left')[0]
        if (navIcons.querySelector('button')) {
            navIcons.querySelector('button').lastChild.textContent = ' ' + navIcons.querySelector('button').title
        }
        let navAnchors = navIcons.querySelectorAll('a')
        for (let i = 0; i < navAnchors.length; i++) {
            navAnchors[i].lastChild.textContent = ' ' + navAnchors[i].title
        }
        let navButtons = document.getElementsByClassName('nav-buttons')[0].querySelectorAll('button')
        for (let j = 0; j < navButtons.length; j++) {
            if (navButtons[j].title === 'All Products') {
                navButtons[j].innerHTML = 'All Products'
            }
            else if (navButtons[j].title === "New Products") {
                navButtons[j].innerHTML = "What's New"
            }
        }
        let navPipes = document.getElementsByClassName('nav-buttons')[0].childNodes
        for (let k = 1; k < navPipes.length - 1; k++) {
            if ((navPipes[k].nodeName === 'BUTTON' &&
                navPipes[k+1].nodeName === 'BUTTON')) {
                navPipes[k].parentNode.insertBefore(document.createTextNode("|"), navPipes[k].nextSibling)
            }
            else if ((navPipes[k].nodeName === '#text' &&
                navPipes[k-1].nodeName === 'BUTTON' &&
                navPipes[k+1].nodeName === 'BUTTON')) {
                navPipes[k].replaceWith(document.createTextNode("|"))
            }
        }
    }
}