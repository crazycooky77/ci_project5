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


function delAccount() {
    let delButton = document.getElementsByClassName('del-button')[0]
    let delAccModal = document.getElementById('del-acc-modal')
    delAccModal.style.display = 'block';
    let delAccSpan = document.getElementById('del-acc-modal').getElementsByClassName('modal-close')[0]
    delAccSpan.onclick = function() {
        delAccModal.style.display = 'none';
    }
    window.onclick = function(event) {
        if (!(delAccModal.contains(event.target)) && delButton !== event.target) {
            delAccModal.style.display = 'none';
        }
    }
    window.onresize = function() {
        delAccModal.style.display = 'none';
    }
}