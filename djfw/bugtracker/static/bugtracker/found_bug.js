$(document).ready(function() {
    ;(function($) {
        $(".modalajax").each(function(index) {
            var t=$(this)[0];
            var href=(t.attributes['href'].nodeValue);
            var modal=$(href);
            var action = modal[0].attributes['action'].nodeValue;
            var body = $(href + '_body');
            var success_container = $(href + '_success');
            var error_container = $(href + '_error');
            var wait_container = $(href + '_wait');
            var footer_container = $(href + '_footer');
            
            $(this).click(function() {
                body.hide();
                success_container.hide();
                error_container.hide();
                footer_container.hide();
                wait_container.show();
                modal.modal('show');
                $.ajax({
                    mode: "abort",
                    port: "ajaxform" + href,
                    dataType: "json",
                    url: action,
                    data: {},
                    success: function(data) {
                        body.children(0).replaceWith('<div>' + data['response'] + '</div>');
                        wait_container.hide();
                        body.fadeIn(500);
                        if (data['success']) {
                            footer_container.fadeIn(500);
                        }
                    },
                    error: function(data) {
                        error_container.children(0).replaceWith('<div>' + data.responseText + '</div>');
                        wait_container.hide();
                        error_container.fadeIn(500)
                    }
                });
                return false
            });
            $(href + '_submit_btn').on('click', function() {
                footer_container.hide();
                body.fadeOut(500, function() {
                    wait_container.show();
                    modal.ajaxSubmit({
                        url: action,
                        type: 'post',
                        success: function(data, statusText, xhr, $form) {
                            body.children(0).replaceWith('<div>' + data['response'] + '</div>');
                            wait_container.fadeOut(500, function() {
                                if (data['success']) {
                                     success_container.fadeIn(500).delay(1000).fadeOut(500, function() {
                                        modal.modal('hide');
                                    });
                                } else {
                                    body.fadeIn(500);
                                    footer_container.fadeIn(500);
                                }
                            });
                        },
                        error: function(data) {
                            wait_container.fadeOut(500, function() {
                                error_container.children(0).replaceWith('<div>' + data.responseText + '</div>');
                                error_container.fadeIn(500);
                            });
                        },
                        dataType: 'json'
                    });
                });
                return false
            });
        });
    })(jQuery);
    

});