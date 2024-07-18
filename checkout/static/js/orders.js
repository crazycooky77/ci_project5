window.addEventListener('DOMContentLoaded', () => {
    profileOrdersU500()
    profileOrdersO500()
    profileOrdersU1100()
    profileOrdersO1100()
})

window.addEventListener('load', () => {
    profileOrdersU500()
    profileOrdersO500()
    profileOrdersU1100()
    profileOrdersO1100()
})

window.addEventListener('resize', () => {
    profileOrdersU500()
    profileOrdersO500()
    profileOrdersU1100()
    profileOrdersO1100()
})


function profileOrdersU500() {
    if (window.innerWidth <= 500) {
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


function profileOrdersO500() {
    if (window.innerWidth > 500) {
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


function profileOrdersU1100() {
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


function profileOrdersO1100() {
    if (window.innerWidth > 1100) {
        if (window.location.pathname.includes('/profile/orders')) {
            let headers = document.querySelectorAll('th')
            for (let i = 0; i < headers.length; i++) {
                headers[i].innerHTML = headers[i].title
            }
        }
    }
}