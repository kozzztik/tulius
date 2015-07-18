$(document).ready(function() {
    ;(function($) {
        $(".invitelink").each(function(index) {
            $(this).click(function() {
                var t=$(this)[0];
                var roleid=(t.attributes['roleid'].nodeValue);
                var rolename=(t.attributes['rolename'].nodeValue);
                var modal=$('#InviteModal');
                var datacont = $("#id_role");
                datacont[0].value = roleid;
                $('#invite_success').hide();
                $('#invite_error').hide();
                $('#invite_form_body').show();
                $('#invite_footer').show();
                modal.modal('show');
            });
        });
    })(jQuery);
    
    $('#submit_form_btn').on('click', function() {
        var content_span = $('#invite_form_body');
        var form_span = $('#InviteModal');
        var error_span = $('#invite_error');
        var action = $('#InviteModal')[0].attributes['action'].nodeValue;
        $('#invite_footer').hide();
        content_span.fadeOut(500, function() {
            form_span.ajaxSubmit({
                url: action,
                success: function(data, statusText, xhr, $form) {
                    content_span.children(0).replaceWith(data['response']);
                    if (data['result'] == 'success') {
                        var success_span = $('#invite_success'); 
                        success_span.fadeIn(500).delay(1000).fadeOut(500, function() {
                            form_span.modal('hide');
                        });
                    }
                    else {
                        if (data['error_text'] == '') {
                            content_span.fadeIn(500)
                            $('#invite_footer').show();
                        } else {
                            error_span[0].innerHTML = data['error_text'];
                            error_span.fadeIn(500);
                        }
                    }
                },
                dataType: 'json'
            });
        });
    });

});