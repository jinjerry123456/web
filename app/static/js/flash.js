// flash disappear
$(document).ready(function () {
    // Set flash message to fade out after 3 seconds
    setTimeout(function () {
        $('.flash-message').fadeOut('slow');
    }, 3000); // 3 seconds
});