
$(window).bind("pageshow", function() {
    var form = $('form');
    // let the browser natively reset defaults
    form[0].reset();
});