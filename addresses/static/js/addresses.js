// Run all necessary functions once page content has loaded
window.addEventListener('DOMContentLoaded', () => {
    addrU800();
    addrO800();
});


// Run all necessary functions once page content has loaded
window.addEventListener('load', () => {
    addrInputResize();
});


// Run all necessary functions when page width is resized
window.addEventListener('resize', () => {
    let curWidth = window.innerWidth;
    if (curWidth !== prvWidth) {
        addrU800();
        addrO800();
        addrInputResize();
    }
});


// Function to resize address input fields for consistency
function addrInputResize() {
    if (window.location.pathname === '/profile/add-address' ||
        window.location.pathname.split('/')[2] === 'edit-address') {
        let formInputs = document.getElementsByClassName('label-input');
        let width = $(formInputs[0].lastElementChild).outerWidth();
        for (let i = 0; i < formInputs.length - 1; i++) {
            if (!(formInputs[i].lastElementChild.required)) {
                $(formInputs[i].lastElementChild).outerWidth(width);
            }
        }
    }
}


// Function to remove label text for form fields on add/edit address pages below 800px screen width
function addrU800() {
    if (window.innerWidth <= 800) {
        if (window.location.pathname.split('/')[2] === 'edit-address' ||
            window.location.pathname.split('/')[2] === 'add-address') {
            let labels = document.getElementsByClassName('label-input');
            for (let i = 0; i < labels.length - 1; i++) {
                document.getElementsByClassName('label-input')[i].firstElementChild.textContent = '';
            }
        }
    }
}


// Function to add label text for form fields on add/edit address pages above 800px screen width
function addrO800() {
    if (window.innerWidth > 800) {
        if (window.location.pathname.split('/')[2] === 'edit-address' ||
            window.location.pathname.split('/')[2] === 'add-address') {
            let labels = document.getElementsByClassName('label-input');
            for (let i = 0; i < labels.length - 1; i++) {
                document.getElementsByClassName('label-input')[i].firstElementChild.textContent = document.getElementsByClassName('label-input')[i].firstElementChild.ariaLabel;
            }
        }
    }
}