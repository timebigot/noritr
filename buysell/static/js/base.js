//autofocus modal post
$('#contact').on('shown.bs.modal', function () {
    $('#focus-contact').focus();
})
//modals store_manage
$('#removeItem').on('show.bs.modal', function (event) {
    var trigger = $(event.relatedTarget);
    var item_code = trigger.data('code') ;
    var item_title = trigger.data('title');
    var modal = $(this);
    modal.find('.modal-body').text('Are you sure you want to remove ' + item_title + '?');
    modal.find('.modal-footer input[value="code"]').val(item_code);
});

//mobile-navbar
$("#buttonSearch").click(function() {
    $("#buttonSearch .fa-search, #buttonSearch .fa-close").toggleClass("fa-search fa-close");
    $("#mainSearch").toggleClass("visible-xs hidden-xs").toggleClass("visible-sm hidden-sm");
    $("#mainContent").toggleClass("hidden-xs visible-xs").toggleClass("hidden-sm visible-sm");
    
    if ($("#buttonUser .fa-close").hasClass("fa-close")) {
        $("#buttonUser .fa-close").addClass("fa-user").removeClass("fa-close");
        $("#mainUser").toggleClass("visible-xs hidden-xs").toggleClass("visible-sm hidden-sm");
        $("#mainContent").toggleClass("hidden-xs visible-xs").toggleClass("hidden-sm visible-sm");
    }
});

$("#buttonUser").click(function() {
    $("#buttonUser .fa-user, #buttonUser .fa-close").toggleClass("fa-user fa-close");
    $("#mainUser").toggleClass("visible-xs hidden-xs").toggleClass("visible-sm hidden-sm");
    $("#mainContent").toggleClass("hidden-xs visible-xs").toggleClass("hidden-sm visible-sm");

    if ($("#buttonSearch .fa-close").hasClass("fa-close")) {
        $("#buttonSearch .fa-close").addClass("fa-search").removeClass("fa-close");
        $("#mainSearch").toggleClass("visible-xs hidden-xs").toggleClass("visible-sm hidden-sm");
        $("#mainContent").toggleClass("hidden-xs visible-xs").toggleClass("hidden-sm visible-sm");
    }
});
