function fast_reply(id) {
    var form_container=$('#replyformroot');
    var form = $('#replyform');
    var post = $("#" + id);
    var fast_reply_url=(post[0].attributes['fast_reply'].nodeValue);
    var extended_reply_url=(post[0].attributes['extended_reply'].nodeValue);
    var link = $('#extended-link');
    link[0].attributes['href'].nodeValue = extended_reply_url;

    form[0].attributes['action'].nodeValue = fast_reply_url;
                
    post.after(form_container);
                
    var selection = $.selection().get();
    text = selection.html;
    var selectedText = selection.text;
    if (text != "") {
        var elem = selectedText.anchorNode.parentNode;
        for ( var i = 0; i < 30; i++ ) {
            if ( elem.hasAttribute('replystr') ) {
                var data = $("textarea").htmlcode();
                $("textarea").htmlcode(data + '<div class="quote"><font size="1">' + elem.attributes['replystr'].nodeValue + '</font><br/>' + 
                    text + '</div>');
                break;
            } else {
                elem = elem.parentNode;
            }
        }
    }
    try {
        window.getSelection().removeAllRanges();
    } catch(e) {
        document.selection.empty(); // IE<9
    }
};

var editor_init_comments_update = false;
var editor_new_data = '';

function on_comments_refresh(param) {
    if (editor_init_comments_update) {
        editor_init_comments_update = false;
        $('#replyform').replaceWith(editor_new_data);
        $('#replyform_loading').hide();
        $('#replyform').show();
        $("#replyform textarea").wysibb(wbbOpt);
    }
}

$(document).ready(function() {
    on_refresh_end.push(on_comments_refresh);
});

function do_fast_reply() {
    var action = $('#replyform')[0].attributes['action'].nodeValue;
    var height = $('#replyform').height();
    $('#post-preview').hide();
    $('#replyform').hide();
    $('#replyform_error').hide();
    $('#replyform_loading').height(height);
    $('#replyform_loading').show();
    $("#replyform textarea").sync();
    $("#replyform textarea").destroy();
    $('#replyform').ajaxSubmit({
        url: action,
        success: function(data, statusText, xhr, $form) {
            editor_new_data = data.form;
            editor_init_comments_update = true;
            if (data.id) {
                refresh_page();
            } else {
                on_comments_refresh('error');
                $('#replyform_error')[0].innerHTML = data.error_message;
                $('#replyform_error').show();
            }
        },
        error: function(jqXHR, textStatus, errorThrown ) {
            $('#replyform_error')[0].innerHTML = errorThrown;
            $('#replyform_error').show();
            
            $('#replyform_loading').hide();
            $('#replyform').show();
            $("textarea").wysibb(wbbOpt);
            $("textarea").sync();
        },
        dataType: 'json'
    });
}