// ======= UI LOGIC ==========
$('.side-button').click(function() {
    // Remove active class from all buttons
    $('.side-button').removeClass('active');
    // Hide all pages
    $('.page').attr('hidden', true);
    // Add active class to clicked button
    $(this).addClass('active'); 
    var id = $(this).attr('class').split(' ')[1];
    $('#' + id).attr('hidden', false);
});