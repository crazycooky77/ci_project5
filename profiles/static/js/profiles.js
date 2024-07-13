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


if (window.innerWidth > 500) {
    if (window.location.pathname === '/profile/add-address' ||
        window.location.pathname.split("/")[2] === 'edit-address') {
        window.onload = function() {
            addrInputResize()
            window.onresize = function() {
                addrInputResize()
            }
        }
    }
}


if (window.innerWidth <= 1100) {
    window.addEventListener("DOMContentLoaded", () => {
        if (window.location.pathname.includes('/profile/orders')) {
            let headers = document.querySelectorAll('th')
            for (let i = 0; i < headers.length; i++) {
                if (headers[i].textContent === 'Date') {
                    headers[i].innerHTML = '<i class="fa-solid fa-calendar-day"></i>'
                } else if (headers[i].textContent === 'Order #') {
                    headers[i].innerHTML = '<i class="fa-solid fa-hashtag"></i>'
                } else if (headers[i].textContent === 'Tracking') {
                    headers[i].innerHTML = '<i class="fa-solid fa-truck-fast"></i>'
                } else if (headers[i].textContent === 'Order Status') {
                    headers[i].innerHTML = '<i class="fa-solid fa-spinner"></i>'
                } else if (headers[i].textContent === 'Action') {
                    headers[i].innerHTML = '<i class="fa-solid fa-hand"></i>'
                } else if (headers[i].textContent === 'View') {
                    headers[i].innerHTML = '<i class="fa-solid fa-eye"></i>'
                } else if (headers[i].textContent === 'Product') {
                    headers[i].innerHTML = '<i class="fa-solid fa-bottle-water"></i>'
                } else if (headers[i].textContent === 'Size') {
                    headers[i].innerHTML = '<i class="fa-solid fa-weight-scale"></i>'
                } else if (headers[i].textContent === 'Quantity') {
                    headers[i].innerHTML = '<i class="fa-solid fa-arrow-up-9-1"></i>'
                 } else if (headers[i].textContent === 'Individual Price') {
                    headers[i].innerHTML = '<i class="fa-solid fa-money-bill-1-wave"></i>'
                } else if (headers[i].textContent === 'Sum') {
                    headers[i].innerHTML = '<i class="fa-solid fa-sack-dollar"></i>'
                }
            }
        }
    })
}


if (window.innerWidth <= 800) {
    window.addEventListener('DOMContentLoaded', () => {
        if (window.location.pathname.split('/')[2] === 'edit-address' ||
            window.location.pathname.split('/')[2] === 'add-address') {
            let labels = document.getElementsByClassName('label-input')
            for (let i = 0; i < labels.length - 1; i++) {
                document.getElementsByClassName('label-input')[i].firstElementChild.textContent = ''
            }
            window.onload = function() {
                mobileResize()
            }
            window.onresize = function () {
                mobileResize()
            }
        }
    })
}


if (window.innerWidth <= 500) {
    window.addEventListener("DOMContentLoaded", () => {
        if (window.location.pathname.includes('profile') ||
            window.location.pathname.includes('email') ||
            window.location.pathname === '/password/change/') {
            let hamMenu = document.getElementById('ham-menu');
            let hamIcon = document.getElementById('ham-icon-button');

            document.body.addEventListener('click', function (e) {
                if (hamIcon === e.target && (hamMenu.style.display === '' || hamMenu.style.display === 'none')) {
                    hamMenu.style.display = 'flex';
                } else if (hamMenu.style.display === 'flex' && !(hamMenu.contains(e.target))) {
                    hamMenu.style.display = 'none';
                }
            })
        }
        if (window.location.pathname.includes('/profile/orders')) {
            let buttons = document.querySelector('table')
            if (buttons) {
                buttons.querySelectorAll('button')
                for (let j = 0; j < buttons.length; j++) {
                    if (buttons[j].textContent === 'View Order') {
                        buttons[j].innerHTML = 'View'
                    }
                }
            }
        }
    })
}