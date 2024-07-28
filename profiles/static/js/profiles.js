// Hide/display expanded hamburger menu on profile pages for screens up to 800px width
if (window.location.pathname.includes('profile') ||
    window.location.pathname.includes('email') ||
    window.location.pathname === '/password/change/') {
    let hamMenu = document.getElementById('ham-menu');
    window.addEventListener('resize', () => {
        if (window.innerWidth > 800) {
            hamMenu.style.display = 'flex';
        }
        else {
            hamMenu.style.display = 'none';
        }
    });
    document.body.addEventListener('click', function (e) {
        if (window.innerWidth <= 800) {
            let hamIcon = document.getElementById('ham-icon-button');
            if ((hamIcon === e.target || hamIcon === e.target.parentElement) && (hamMenu.style.display === '' || hamMenu.style.display === 'none')) {
                hamMenu.style.display = 'flex';
            } else if (hamMenu.style.display === 'flex' && !(hamMenu.contains(e.target))) {
                hamMenu.style.display = 'none';
            }
        }
    });
}