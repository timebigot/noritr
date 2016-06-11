//autofocus modals
/*
   $('#signup').on('shown.bs.modal', function () {
   $('#focus-signup').focus()
   })
   $('#login').on('shown.bs.modal', function () {
   $('#focus-login').focus()
   })
   */

//modals store_manage
$('#deleteItem').on('show.bs.modal', function (event) {
    var trigger = $(event.relatedTarget)
    var item_code = trigger.data('code') 
    var item_title = trigger.data('title') 
    var modal = $(this)
    modal.find('.modal-body').text('Are you sure you want to delete ' + item_title + '?')
    modal.find('.modal-footer input[value="code"]').val(item_code)
})
