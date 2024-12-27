document.getElementById('accept-cookie').onclick = function () {
    document.getElementById('cookie-warning').style.display = 'none';
    // set cookie 
    document.cookie = "cookieAccepted=true; path=/; max-age=" + 60 * 60 * 24 * 30;
};

// check if cookie is set
if (document.cookie.indexOf('cookieAccepted=true') !== -1) {
    document.getElementById('cookie-warning').style.display = 'none';
}