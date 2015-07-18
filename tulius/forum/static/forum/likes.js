function do_like(post_id) {
    var like_btn = $('#likebtn' + post_id)[0];
    var value=like_btn.attributes['value'].nodeValue;

    $.ajax({
        // try to leverage ajaxQueue plugin to abort previous requests
        mode: "abort",
        // limit abortion to this input
        port: "like" + post_id,
        dataType: "json",
        url: like_options.url,
        data: {
            postid: post_id,
            value: value
        },
        success: function(data) {
            if (data.success) {
                value = data.value;
                var btn = $('#likebtn' + data.comment_id)[0]
                btn.attributes['value'].nodeValue = value;
                if (data.value) {
                    btn.src = like_options.dislike_image;
                } else {
                    btn.src = like_options.like_image;
                }
            }
        },
        error: function() {
        }
    });
};