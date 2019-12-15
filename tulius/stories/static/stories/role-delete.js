$(document).ready(function() {
    ;(function($) {
        $(".role-delete-link").each(function(index) {
            $(this).click(function() {
                var t=$(this)[0];
                var roleid=(t.attributes['roleid'].nodeValue);
                var modal=$('#RoleDeleteModal');
                var datacont = $("#RoleDeleteModal #id_role");
                datacont[0].value = roleid;
                $('#deleterole_success').hide();
                $('#deleterole_error').hide();
                $('#deleterole_form_body').show();
                $('#deleterole_footer').show();
                modal.modal('show');
            });
        });
    })(jQuery);
    
    $('#deleterole_btn').on('click', function() {
        var content_span = $('#deleterole_form_body');
        var form_span = $('#RoleDeleteModal');
        var error_span = $('#deleterole_error');
        var action = $('#RoleDeleteModal')[0].attributes['action'].nodeValue;
        $('#deleterole_footer').hide();
        content_span.fadeOut(500, function() {
            form_span.ajaxSubmit({
                url: action,
                success: function(data, statusText, xhr, $form) {
                    if (data['result'] == 'success') {
                        var success_span = $('#deleterole_success'); 
                        success_span.fadeIn(500).delay(1000).fadeOut(500, function() {
                            form_span.modal('hide');
                            window.location.reload();
                        });
                    }
                    else {
                        if (data['error_text'] == '') {
                            content_span.fadeIn(500)
                            $('#deleterole_footer').show();
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