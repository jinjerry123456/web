document.getElementById('accept-cookie').onclick = function () {
    document.getElementById('cookie-warning').style.display = 'none';
    // set cookie with expiry date of 1 minute
    document.cookie = "cookieAccepted=true; path=/; max-age=" + 60;
};

// check if cookie is set
if (document.cookie.indexOf('cookieAccepted=true') !== -1) {
    document.getElementById('cookie-warning').style.display = 'none';
}