if (window.location.pathname === '/profile/add-address' ||
    window.location.pathname.split("/")[2] === 'edit-address') {
    $(document).ready(function () {
        let selectBox = document.getElementById('id_country')
        let inputBox = document.getElementById('id_county')
        selectBox.style.width = (inputBox.getBoundingClientRect().width + 2) + 'px'
        window.onresize = function() {
            let selectBox = document.getElementById('id_country')
            let inputBox = document.getElementById('id_county')
            selectBox.style.width = (inputBox.getBoundingClientRect().width + 2) + 'px'
        }
    })
}