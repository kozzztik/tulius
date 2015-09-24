$(document).ready(function() {
    $('.menu-background').on('click', function() {
        $('.menu-background').hide();
        $('.sub-menu').hide();
        $('.menu-list > li > a').removeClass('active')
    });

    $('ul.menu-list > li > a').on('click', function() {
         $('.menu-background').show();
         $('.sub-menu').hide();
         $('.menu-list > li > a').removeClass('active')
         var selector = this.attributes['data-toggle'].nodeValue;
         $(selector).show();
         $(this).addClass('active');
    });

    $('.scroll-up').click(function(){
       $('html, body').animate({scrollTop:0}, 800);
   });
    $('.scroll-down').click(function(){
        var $elem = $('body');
        $('html, body').animate({scrollTop: $elem.height()}, 800);
   });


    var ws4redis = WS4Redis({
        uri: 'ws://127.0.0.1:8000/ws/pm?subscribe-user',
        receive_message: receiveMessage,
        heartbeat_msg: 'heartbeat'
    });
    // receive a message though the websocket from the server
    function receiveMessage(msg) {
        $('.new_messages').addClass('active')
        //alert(msg);
    }
});