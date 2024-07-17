window.addEventListener("DOMContentLoaded", () => {
    addrU800()
    addrO800()
    addrInputResize()
})

window.addEventListener("load", () => {
    addrU800()
    addrO800()
    addrInputResize()
})

window.addEventListener("resize", () => {
    addrU800()
    addrO800()
    addrInputResize()
})


function addrInputResize() {
    if (window.location.pathname === '/profile/add-address' ||
        window.location.pathname.split("/")[2] === 'edit-address') {
        let formInputs = document.getElementsByClassName('label-input')
        let width = $(formInputs[0].lastElementChild).outerWidth()
        for (let i = 0; i < formInputs.length - 1; i++) {
            if (!(formInputs[i].lastElementChild.required)) {
                $(formInputs[i].lastElementChild).outerWidth(width)
            }
        }
    }
}


function addrU800() {
    if (window.innerWidth <= 800) {
        if (window.location.pathname.split('/')[2] === 'edit-address' ||
            window.location.pathname.split('/')[2] === 'add-address') {
            let labels = document.getElementsByClassName('label-input')
            for (let i = 0; i < labels.length - 1; i++) {
                document.getElementsByClassName('label-input')[i].firstElementChild.textContent = ''
            }
        }
    }
}


function addrO800() {
    if (window.innerWidth > 800) {
        if (window.location.pathname.split('/')[2] === 'edit-address' ||
            window.location.pathname.split('/')[2] === 'add-address') {
            let labels = document.getElementsByClassName('label-input')
            for (let i = 0; i < labels.length - 1; i++) {
                document.getElementsByClassName('label-input')[i].firstElementChild.textContent = document.getElementsByClassName('label-input')[i].firstElementChild.ariaLabel
            }
        }
    }
}