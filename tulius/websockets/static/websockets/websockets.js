jQuery(document).ready(function($) {
    var ws4redis = WS4Redis({
        uri: websocket_uri,
        connecting: on_connecting,
        connected: on_connected,
        receive_message: receiveMessage,
        disconnected: on_disconnected,
        heartbeat_msg: ''
    });

    // attach this function to an event handler on your site
    function sendMessage() {
        ws4redis.send_message('A message');
    }

    function on_connecting() {
        console.log('Websocket is connecting...');
    }

    function on_connected() {
        ws4redis.send_message('Hello');
    }

    function on_disconnected(evt) {
        console.log('Websocket was disconnected: ' + JSON.stringify(evt));
    }

    // receive a message though the websocket from the server
    function receiveMessage(msg) {
        console.log('Message from Websocket: ' + msg);
        var kind = msg.split(' ', 1)[0];
        if (kind == 'new_pm') {
            $('.new_messages').addClass('active');
            $('.new_messages').attr('title', "У вас новое сообщение!")
        }
    }
});
