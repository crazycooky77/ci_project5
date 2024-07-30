// Run all necessary functions once DOM has loaded
window.addEventListener('DOMContentLoaded', () => {
    cartU800();
    cartO800();
});

// Run all necessary functions once page content has loaded
window.addEventListener('load', () => {
    cartU800();
    cartO800();
});

// Run all necessary functions when page width is resized
window.addEventListener('resize', () => {
    let curWidth = window.innerWidth;
    if (curWidth !== prvWidth) {
        cartU800();
        cartO800();
    }
});


// Replace table headers with icons for cart views for screens up to 800px width
function cartU800() {
    if (window.innerWidth <= 800) {
        if (window.location.pathname === '/cart') {
            let headers = document.querySelectorAll('th');
            for (let i = 0; i < headers.length; i++) {
                if (headers[i].title === 'Product') {
                    headers[i].innerHTML = '<i class="fa-solid fa-bottle-water"></i>';
                } else if (headers[i].title === 'Size') {
                    headers[i].innerHTML = '<i class="fa-solid fa-weight-scale"></i>';
                } else if (headers[i].title === 'Quantity') {
                    headers[i].innerHTML = '<i class="fa-solid fa-arrow-up-9-1"></i>';
                } else if (headers[i].title === 'Sum') {
                    headers[i].innerHTML = '<i class="fa-solid fa-sack-dollar"></i>';
                }
            }
            document.querySelector('[title="Free Shipping"]').innerText = 'Free';
        }
    }
}


// Replace icons with table headers for cart views for screens above 800px width
function cartO800() {
    if (window.innerWidth > 800) {
        if (window.location.pathname === '/cart') {
            let headers = document.querySelectorAll('th');
            for (let i = 0; i < headers.length; i++) {
                headers[i].innerHTML = headers[i].title;
            }
            document.querySelector('[title="Free Shipping"]').innerText = 'Free Shipping';
        }
    }
}