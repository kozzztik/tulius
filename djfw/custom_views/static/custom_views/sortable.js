$(function() {
    $( ".sortable" ).sortable();
    $( ".sortable" ).disableSelection();
    $( ".sortable" ).sortable({
        update: function( event, ui ) {
            $.ajax({
                url: '',
                type: 'post',
                data: { items: $(this).sortable('toArray').join(',') }
            });
        }
    });
});