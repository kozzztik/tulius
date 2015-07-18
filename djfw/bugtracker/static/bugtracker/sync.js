$(document).ready(function() {
    ;(function($) {
        $(".bugtracker-sync-link").each(function(index) {
            $(this).click(function() {
                var t=$(this)[0];
                var href=(t.attributes['url'].nodeValue);
                var wait_text=(t.attributes['wait_text'].nodeValue);
                var error_text=(t.attributes['error_text'].nodeValue);
                var success_text=(t.attributes['success_text'].nodeValue);
                var text_container_selector=(t.attributes['text_container'].nodeValue);
                var text_container=$(text_container_selector)[0];
                text_container.innerHTML = wait_text;
                $.ajax({
                    // try to leverage ajaxQueue plugin to abort previous requests
                    mode: "abort",
                    // limit abortion to this input
                    port: "bugtracker_sync_" + href,
                    dataType: "json",
                    url: href,
                    data: {},
                    success: function(data) { text_container.innerHTML = success_text; },
                    error: function() { text_container.innerHTML = error_text; }
                });
                return false
            });
        });
    })(jQuery);
});