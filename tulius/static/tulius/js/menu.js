function hide_menu() {
    $('.menu-background').hide();
    $('.sub-menu').hide();
    $('.menu-list > li > a').removeClass('active')
}

$(document).ready(function() {
    $('.menu-background').on('click', function() {
        hide_menu()
    });

    $('ul.menu-list > li > a').on('click', function() {
         var selector = this.attributes['data-toggle'].nodeValue;
         if ($(selector).is(":visible")) {
            hide_menu();
         } else {
            $('.menu-background').show();
            $('.sub-menu').hide();
            $('.menu-list > li > a').removeClass('active')

            $(selector).show();
            $(this).addClass('active');
         }
    });

    $('.scroll-up').click(function(){
       $('html, body').animate({scrollTop:0}, 800);
   });
    $('.scroll-down').click(function(){
        var $elem = $('body');
        $('html, body').animate({scrollTop: $elem.height()}, 800);
   });


    var ws4redis = WS4Redis({
        uri: websocket_uri + 'pm?subscribe-user',
        receive_message: receiveMessage,
        heartbeat_msg: 'heartbeat'
    });
    // receive a message though the websocket from the server
    function receiveMessage(msg) {
        if (msg > last_read_pm_id) {
        $('.new_messages').addClass('active')
        //alert(msg);
        }
    }
});