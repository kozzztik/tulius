$(document).ready(function() {
    ;(function($) {
        $(".emoticon_link").each(function(index) {
            $(this).click(function() {
                var t=$(this)[0];
                var filename=(t.attributes['filename'].nodeValue);
                var text=(t.attributes['text'].nodeValue);
                EmotionsDialog.insert(filename, text);
            });
        });
    })(jQuery);
});