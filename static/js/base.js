// Run all necessary functions once DOM has loaded
window.addEventListener('DOMContentLoaded', () => {
    scrollOpt();
    footerResize();
    baseU320();
    baseO320();
    baseU500();
    baseO500();
});

// Run all necessary functions once page content has loaded
window.addEventListener('load', () => {
    footerResize();
    baseU320();
    baseO320();
    baseU500();
    baseO500();
});

// Run all necessary functions when page width is resized
let prvWidth = window.innerWidth;
window.addEventListener('resize', () => {
    let curWidth = window.innerWidth;
    if (curWidth !== prvWidth) {
        footerResize();
        baseU320();
        baseO320();
        baseU500();
        baseO500();
    }
});


// Function to display and style the Back to top button for the site
function scrollOpt() {
    let scrollBtn = document.getElementById('footer-top-link');
    let footLinks = document.getElementById('footer-links');
    window.onscroll = function () {
        if (document.body.scrollTop > 20 || document.documentElement.scrollTop > 20) {
            scrollBtn.style.visibility = 'unset';
            scrollBtn.style.width = '15%';
            if (window.innerWidth <= 500) {
                footLinks.style.width = '85%';
            }
        } else {
            scrollBtn.style.visibility = 'hidden';
            if (window.innerWidth <= 500) {
                scrollBtn.style.width = '0%';
                footLinks.style.width = '100%';
            }
        }
    };
}


// Function to style footer elements based on screen width and Back to top button visibility
function footerResize() {
    let scrollBtn = document.getElementById('footer-top-link');
    let footLinks = document.getElementById('footer-links');
    if (scrollBtn) {
        if (scrollBtn.style.visibility === 'hidden' || scrollBtn.style.visibility === '') {
            if (window.innerWidth <= 500) {
                scrollBtn.style.width = '0%';
                footLinks.style.width = '100%';
            } else {
                scrollBtn.style.width = '15%';
                footLinks.style.width = '70%';
            }
        } else {
            if (window.innerWidth <= 500) {
                scrollBtn.style.width = '15%';
                footLinks.style.width = '85%';
            } else {
                scrollBtn.style.width = '15%';
                footLinks.style.width = '70%';
            }
        }
    }
}


// Function to scroll to the top of the page
function topScroll() {
    // For Safari
    document.body.scrollTop = 0;
    // For Chrome, Firefox, IE and Opera
    document.documentElement.scrollTop = 0;
}


// Function to show/hide modals for various features on different pages
function modals(buttonId, modalId) {
    let button = document.getElementById(buttonId);
    let modal = document.getElementById(modalId);
    let toolTip = modal.querySelector('.modal-tooltip');
    modal.style.display = 'block';
    let span = modal.getElementsByClassName('modal-close')[0];
    span.onclick = function() {
        modal.style.display = 'none';
        if (toolTip) {
            toolTip.style.display = 'none';
        }
    };
    window.onclick = function(event) {
        if (!(modal.contains(event.target)) && button !== event.target) {
            modal.style.display = 'none';
            if (toolTip) {
                toolTip.style.display = 'none';
            }
        }
    };
    let prvWidth = window.innerWidth;
    window.onresize = function() {
        let curWidth = window.innerWidth;
        if (curWidth !== prvWidth) {
            modal.style.display = 'none';
            if (toolTip) {
                toolTip.style.display = 'none';
            }
        }
    };
}


// Function to copy the support email to clipboard
function copyMailto(modalId) {
    let modal = document.getElementById(modalId);
    navigator.clipboard.writeText(event.target.innerText).then(() => {
        let toolTip = modal.querySelector('.modal-tooltip');
        toolTip.style.display = 'block';
    });
}


// Move nav buttons for screens up to 320px width
function baseU320() {
    if (window.innerWidth <= 320) {
        $(document.getElementsByClassName('sub-nav-div')[0]).detach().appendTo("nav");
    }
}


// Move nav buttons for screens above 320px width
function baseO320() {
    if (window.innerWidth > 320) {
        $(document.getElementsByClassName('sub-nav-div')[0]).detach().appendTo(".nav-middle");
    }
}


// Replace elements in nav bar for screens up to 500px width
function baseU500() {
    if (window.innerWidth <= 800) {
        // Remove text content from left nav buttons/links (only icons remain)
        let navIcons = document.getElementsByClassName('nav-left')[0];
        if (navIcons.querySelector('button')) {
            navIcons.querySelector('button').lastChild.textContent = '';
        }
        let navAnchors = navIcons.querySelectorAll('a');
        for (let i = 0; i < navAnchors.length; i++) {
            navAnchors[i].lastChild.textContent = '';
        }
        // Replace longer middle nav button text with shorter text
        let navButtons = document.getElementsByClassName('nav-buttons')[0].querySelectorAll('button');
        for (let j = 0; j < navButtons.length; j++) {
            if (navButtons[j].title === 'All Products') {
                navButtons[j].innerHTML = 'All';
            } else if (navButtons[j].title === 'New Products') {
                navButtons[j].innerHTML = 'New';
            }
        }
    }
}


// Replace elements in nav bar for screens above 500px width
function baseO500() {
    if (window.innerWidth > 800) {
        // Add text content to left nav buttons/links (icons remain)
        let navIcons = document.getElementsByClassName('nav-left')[0];
        if (navIcons.querySelector('button')) {
            navIcons.querySelector('button').lastChild.textContent = ' ' + navIcons.querySelector('button').title;
        }
        let navAnchors = navIcons.querySelectorAll('a');
        for (let i = 0; i < navAnchors.length; i++) {
            navAnchors[i].lastChild.textContent = ' ' + navAnchors[i].title;
        }
        // Replace shorter middle nav button text with original longer text
        let navButtons = document.getElementsByClassName('nav-buttons')[0].querySelectorAll('button');
        for (let j = 0; j < navButtons.length; j++) {
            if (navButtons[j].title === 'All Products') {
                navButtons[j].innerHTML = 'All Products';
            }
            else if (navButtons[j].title === 'New Products') {
                navButtons[j].innerHTML = "What's New";
            }
        }
    }
}