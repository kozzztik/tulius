function delete_post_dialog(post_header, post_id, action) {
    $('#PostDeleteModal')[0].attributes['action'].nodeValue = action;
    var modal=$('#PostDeleteModal');
    var datacont = $("#PostDeleteModal #id_post");
    $("#PostDeleteModal h3")[0].innerHTML = post_header;
    datacont[0].value = post_id;
    $('#deletepost_success').hide();
    $('#deletepost_error').hide();
    $('#deletepost_form_body').show();
    $('#deletepost_footer').show();
    modal.modal('show');
}

function delete_comment(post_id) {
    var t=$('#' + post_id)[0];
    var is_thread=(t.attributes['is_thread'].nodeValue);
    if (is_thread=='0') {
        $('#deletethread_warning').hide();
        delete_post_dialog(delete_thread_options.comment_header, post_id, delete_thread_options.comment_url);
    } else {
        $('#deletethread_warning').show();
        delete_post_dialog(delete_thread_options.thread_header, post_id, delete_thread_options.thread_url);
    }
}

function delete_room(post_id) {
    $('#deletethread_warning').hide();
    delete_post_dialog(delete_thread_options.room_header, post_id, delete_thread_options.room_url)
}

$(document).ready(function() {    
    $('#deletepost_btn').on('click', function() {
        var content_span = $('#deletepost_form_body');
        var form_span = $('#PostDeleteModal');
        var error_span = $('#deletepost_error');
        var action = $('#PostDeleteModal')[0].attributes['action'].nodeValue;
        $('#deletepost_footer').hide();
        content_span.fadeOut(500, function() {
            form_span.ajaxSubmit({
                url: action,
                success: function(data, statusText, xhr, $form) {
                    if (data['result'] == 'success') {
                        var success_span = $('#deletepost_success'); 
                        success_span[0].innerHTML = data['text'];
                        success_span.fadeIn(500).delay(1000).fadeOut(500, function() {
                            form_span.modal('hide');
                            if (data['redirect'] == '') {
                                window.location.reload();
                            } else {
                                window.location.replace(data['redirect']);
                            }
                        });
                    }
                    else {
                        if (data['error_text'] == '') {
                            content_span.fadeIn(500)
                            $('#deletepost_footer').show();
                        } else {
                            error_span[0].innerHTML = data['error_text'];
                            error_span.show(500);
                        }
                    }
                },
                dataType: 'json'
            });
        });
    });

});