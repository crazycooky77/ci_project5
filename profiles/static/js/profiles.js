function addrInputResize() {
    let selectBox = document.getElementById('id_country')
    let inputBox = document.getElementById('id_county')
    selectBox.style.width = (inputBox.getBoundingClientRect().width + 2) + 'px'
}

if (window.location.pathname === '/profile/add-address' ||
    window.location.pathname.split("/")[2] === 'edit-address') {
    $(document).ready(function () {
        addrInputResize()
        window.onresize = function() {
            addrInputResize()
        }
    })
}


function mobileResize() {
    let addrLine2 = document.getElementById('id_addr_line2')
    let addrLine3 = document.getElementById('id_addr_line3')
    let addrLine1Width = document.getElementById('id_addr_line1').getBoundingClientRect().width
    let addrLine2Width = document.getElementById('id_addr_line2').getBoundingClientRect().width
    let addrLine3Width = document.getElementById('id_addr_line3').getBoundingClientRect().width

    addrLine2.style.width = (addrLine1Width - (addrLine2Width - addrLine1Width)) + 'px'
    addrLine3.style.width = (addrLine1Width - (addrLine3Width - addrLine1Width)) + 'px'
}


if (window.innerWidth <= 320) {
    $(document).ready(function () {
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
        if (window.location.pathname.split('/')[2] === 'edit-address' ||
            window.location.pathname.split('/')[2] === 'add-address') {
            let labels = document.getElementsByClassName('label-input')
            for (let i = 0; i < labels.length - 1; i++) {
                document.getElementsByClassName('label-input')[i].firstElementChild.textContent = ''
            }
            mobileResize()
            addrInputResize()
            window.onresize = function () {
                mobileResize()
                addrInputResize()
            }
        }
    })
}