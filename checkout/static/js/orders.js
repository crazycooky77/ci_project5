// Run all necessary functions once page content has loaded
window.addEventListener('load', () => {
    profileOrdersU500();
    profileOrdersO500();
    profileOrdersU1100();
    profileOrdersO1100();
});

// Run all necessary functions when page width is resized
window.addEventListener('resize', () => {
    let curWidth = window.innerWidth;
    if (curWidth !== prvWidth) {
        profileOrdersU500();
        profileOrdersO500();
        profileOrdersU1100();
        profileOrdersO1100();
    }
});


// Replace View Order button text with View on the profile orders page for screens up to 500px width
function profileOrdersU500() {
    if (window.innerWidth <= 500) {
        if (window.location.pathname.includes('/profile/orders')) {
            let buttons = document.querySelector('table');
            if (buttons) {
                let button = buttons.querySelectorAll('button');
                for (let j = 0; j < button.length; j++) {
                    if (button[j].innerHTML === 'View Order') {
                        button[j].innerHTML = 'View';
                    }
                }
            }
        }
    }
}


// Replace View button text with View Orders on the profile orders page for screens with above 500px width
function profileOrdersO500() {
    if (window.innerWidth > 500) {
        if (window.location.pathname.includes('/profile/orders')) {
            let buttons = document.querySelector('table');
            if (buttons) {
                let button = buttons.querySelectorAll('button');
                for (let j = 0; j < button.length; j++) {
                    if (button[j].innerHTML === 'View') {
                        button[j].innerHTML = 'View Order';
                    }
                }
            }
        }
    }
}


// Replace table headers with icons on the profile orders page for screens up to 1100px width
function profileOrdersU1100() {
    if (window.innerWidth <= 1100) {
        if (window.location.pathname.includes('/profile/orders')) {
            let headers = document.querySelectorAll('th');
            for (let i = 0; i < headers.length; i++) {
                if (headers[i].title === 'Date') {
                    headers[i].innerHTML = '<i class="fa-solid fa-calendar-day" title="Date"></i>';
                } else if (headers[i].title === 'Order #') {
                    headers[i].innerHTML = '<i class="fa-solid fa-hashtag" title="Order #"></i>';
                } else if (headers[i].title === 'Tracking') {
                    headers[i].innerHTML = '<i class="fa-solid fa-truck-fast" title="Tracking"></i>';
                } else if (headers[i].title === 'Order Status') {
                    headers[i].innerHTML = '<i class="fa-solid fa-spinner" title="Order Status"></i>';
                } else if (headers[i].title === 'Action') {
                    headers[i].innerHTML = '<i class="fa-solid fa-hand" title="Action"></i>';
                } else if (headers[i].title === 'View Order') {
                    headers[i].innerHTML = '<i class="fa-solid fa-eye" title="View Order"></i>';
                } else if (headers[i].title === 'Product') {
                    headers[i].innerHTML = '<i class="fa-solid fa-bottle-water" title="Product"></i>';
                } else if (headers[i].title === 'Size') {
                    headers[i].innerHTML = '<i class="fa-solid fa-weight-scale" title="Size"></i>';
                } else if (headers[i].title === 'Quantity') {
                    headers[i].innerHTML = '<i class="fa-solid fa-arrow-up-9-1" title="Quantity"></i>';
                } else if (headers[i].title === 'Individual Price') {
                    headers[i].innerHTML = '<i class="fa-solid fa-money-bill-1-wave" title="Individual Price"></i>';
                } else if (headers[i].title === 'Sum') {
                    headers[i].innerHTML = '<i class="fa-solid fa-sack-dollar" title="Sum"></i>';
                }
            }
        }
    }
}


// Replace icons with table headers on the profile orders page for screens above 1100px width
function profileOrdersO1100() {
    if (window.innerWidth > 1100) {
        if (window.location.pathname.includes('/profile/orders')) {
            let headers = document.querySelectorAll('th');
            for (let i = 0; i < headers.length; i++) {
                headers[i].innerHTML = headers[i].title;
            }
        }
    }
}