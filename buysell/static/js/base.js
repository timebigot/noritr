//autofocus modals
$('#signup').on('shown.bs.modal', function () {
    $('#focus-signup').focus()
})
$('#login').on('shown.bs.modal', function () {
    $('#focus-login').focus()
})
