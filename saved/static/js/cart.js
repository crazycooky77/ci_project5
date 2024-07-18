window.addEventListener('DOMContentLoaded', () => {
    cartU800()
    cartO800()
})

window.addEventListener('load', () => {
    cartU800()
    cartO800()
})

window.addEventListener('resize', () => {
    cartU800()
    cartO800()
})


function cartU800() {
    if (window.innerWidth <= 800) {
        if (window.location.pathname === '/cart') {
            let headers = document.querySelectorAll('th')
            for (let i = 0; i < headers.length; i++) {
                if (headers[i].title === 'Product') {
                    headers[i].innerHTML = '<i class="fa-solid fa-bottle-water"></i>'
                } else if (headers[i].title === 'Size') {
                    headers[i].innerHTML = '<i class="fa-solid fa-weight-scale"></i>'
                } else if (headers[i].title === 'Quantity') {
                    headers[i].innerHTML = '<i class="fa-solid fa-arrow-up-9-1"></i>'
                } else if (headers[i].title === 'Sum') {
                    headers[i].innerHTML = '<i class="fa-solid fa-sack-dollar"></i>'
                }
            }
        }
    }
}


function cartO800() {
    if (window.innerWidth > 800) {
        if (window.location.pathname === '/cart') {
            let headers = document.querySelectorAll('th')
            for (let i = 0; i < headers.length; i++) {
                headers[i].innerHTML = headers[i].title
            }
        }
    }
}