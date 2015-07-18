function do_preview() {
    var t=$('#post-preview-link')[0];
    var url = t.attributes['url'].nodeValue;
    var body_elem = $('#id_body')[0];
    var title_elem = $('#id_title')[0];
                
    $("textarea").sync();
                
    var body_text = body_elem.value
    var title_text = title_elem.value

    $.ajax({
        mode: "abort",
        port: "preview",
        dataType: "text",
        type : "POST",
        url: url,
        data: {title: title_text, body: body_text},
        success: function(data, textStatus, jqXHR ) {
        var root_elem = $('#post-preview');
            root_elem[0].innerHTML = data;
            root_elem.show();
        },
        error: function(jqXHR, textStatus, errorThrown ) {
            var root_elem = $('#post-preview');
            root_elem[0].innerHTML = errorThrown;
            root_elem.show();
        }
    });
};
