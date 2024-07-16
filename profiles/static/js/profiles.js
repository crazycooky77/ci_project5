window.addEventListener("DOMContentLoaded", () => {
    windowU500()
    windowO500()
    windowU800()
    windowO800()
    windowU1100()
    windowO1100()
})

window.addEventListener("load", () => {
    windowU500()
    windowO500()
    windowU800()
    windowO800()
    windowU1100()
    windowO1100()
})

window.addEventListener("resize", () => {
    windowU500()
    windowO500()
    windowU800()
    windowO800()
    windowU1100()
    windowO1100()
})


if (window.location.pathname.includes('profile') ||
    window.location.pathname.includes('email') ||
    window.location.pathname === '/password/change/') {
    document.body.addEventListener('click', function (e) {
        if (window.innerWidth <= 500) {
            let hamMenu = document.getElementById('ham-menu');
            let hamIcon = document.getElementById('ham-icon-button');

            if (hamIcon === e.target && (hamMenu.style.display === '' || hamMenu.style.display === 'none')) {
                hamMenu.style.display = 'flex';
            } else if (hamMenu.style.display === 'flex' && !(hamMenu.contains(e.target))) {
                hamMenu.style.display = 'none';
            }
        }
    })
}


function addrInputResize() {
    let selectBox = document.getElementById('id_country')
    let selectBoxWidth = document.getElementById('id_country').getBoundingClientRect().width
    let inputBoxWidth = document.getElementById('id_county').getBoundingClientRect().width

    selectBox.style.width = (selectBoxWidth + (inputBoxWidth - selectBoxWidth)) + 'px'
}


function mobileResize() {
    let addrLine2 = document.getElementById('id_addr_line2')
    let addrLine3 = document.getElementById('id_addr_line3')
    let addrLine1Width = document.getElementById('id_addr_line1').getBoundingClientRect().width
    let addrLine2Width = document.getElementById('id_addr_line2').getBoundingClientRect().width
    let addrLine3Width = document.getElementById('id_addr_line3').getBoundingClientRect().width

    addrLine2.style.width = (addrLine1Width - (addrLine2Width - addrLine1Width)) + 'px'
    addrLine3.style.width = (addrLine1Width - (addrLine3Width - addrLine1Width)) + 'px'
    addrInputResize()
}


function windowU500() {
    if (window.innerWidth <= 500) {
        if (window.location.pathname === '/profile/add-address' ||
            window.location.pathname.split("/")[2] === 'edit-address') {
            addrInputResize()
        }
        if (window.location.pathname.includes('/profile/orders')) {
            let buttons = document.querySelector('table')
            if (buttons) {
                let button = buttons.querySelectorAll('button')
                for (let j = 0; j < button.length; j++) {
                    if (button[j].innerHTML === 'View Order') {
                        button[j].innerHTML = 'View'
                    }
                }
            }
        }
    }
}


function windowO500() {
    if (window.innerWidth > 500) {
        if (window.location.pathname === '/profile/add-address' ||
            window.location.pathname.split("/")[2] === 'edit-address') {
            addrInputResize()
        }
        if (window.location.pathname.includes('/profile/orders')) {
            let buttons = document.querySelector('table')
            if (buttons) {
                let button = buttons.querySelectorAll('button')
                for (let j = 0; j < button.length; j++) {
                    if (button[j].innerHTML === 'View') {
                        button[j].innerHTML = 'View Order'
                    }
                }
            }
        }
    }
}


function windowU800() {
    if (window.innerWidth <= 800) {
        if (window.location.pathname.split('/')[2] === 'edit-address' ||
            window.location.pathname.split('/')[2] === 'add-address') {
            let labels = document.getElementsByClassName('label-input')
            for (let i = 0; i < labels.length - 1; i++) {
                document.getElementsByClassName('label-input')[i].firstElementChild.textContent = ''
            }
            mobileResize()
        }
    }
}


function windowO800() {
    if (window.innerWidth > 800) {
        if (window.location.pathname.split('/')[2] === 'edit-address' ||
            window.location.pathname.split('/')[2] === 'add-address') {
            let labels = document.getElementsByClassName('label-input')
            for (let i = 0; i < labels.length - 1; i++) {
                document.getElementsByClassName('label-input')[i].firstElementChild.textContent = document.getElementsByClassName('label-input')[i].firstElementChild.ariaLabel
            }
            mobileResize()
        }
    }


}


function windowU1100() {
    if (window.innerWidth <= 1100) {
        if (window.location.pathname.includes('/profile/orders')) {
            let headers = document.querySelectorAll('th')
            for (let i = 0; i < headers.length; i++) {
                if (headers[i].title === 'Date') {
                    headers[i].innerHTML = '<i class="fa-solid fa-calendar-day"></i>'
                } else if (headers[i].title === 'Order #') {
                    headers[i].innerHTML = '<i class="fa-solid fa-hashtag"></i>'
                } else if (headers[i].title === 'Tracking') {
                    headers[i].innerHTML = '<i class="fa-solid fa-truck-fast"></i>'
                } else if (headers[i].title === 'Order Status') {
                    headers[i].innerHTML = '<i class="fa-solid fa-spinner"></i>'
                } else if (headers[i].title === 'Action') {
                    headers[i].innerHTML = '<i class="fa-solid fa-hand"></i>'
                } else if (headers[i].title === 'View' || headers[i].title === 'View Order') {
                    headers[i].innerHTML = '<i class="fa-solid fa-eye"></i>'
                } else if (headers[i].title === 'Product') {
                    headers[i].innerHTML = '<i class="fa-solid fa-bottle-water"></i>'
                } else if (headers[i].title === 'Size') {
                    headers[i].innerHTML = '<i class="fa-solid fa-weight-scale"></i>'
                } else if (headers[i].title === 'Quantity') {
                    headers[i].innerHTML = '<i class="fa-solid fa-arrow-up-9-1"></i>'
                } else if (headers[i].title === 'Individual Price') {
                    headers[i].innerHTML = '<i class="fa-solid fa-money-bill-1-wave"></i>'
                } else if (headers[i].title === 'Sum') {
                    headers[i].innerHTML = '<i class="fa-solid fa-sack-dollar"></i>'
                }
            }
        }
    }
}


function windowO1100() {
    if (window.innerWidth > 1100) {
        if (window.location.pathname.includes('/profile/orders')) {
            let headers = document.querySelectorAll('th')
            for (let i = 0; i < headers.length; i++) {
                headers[i].innerHTML = headers[i].title
            }
        }
    }
}