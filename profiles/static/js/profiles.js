/* Hide/display expanded hamburger menu on profile pages for screens below 500px width */
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