var readed_comments = [];
var on_refresh_end = [];

function trigger_event(handlers, param) {
    if (handlers.length) {
        for (i = 0; i < handlers.length; i++) {
            handlers[i](param);
        }
    }
}

function move_reply_form_back() {
    var form_container = $('#replyformroot');
    var reply_form = $('#replyform_placement');
    $('#replyform_placement').append(form_container);
}

function get_over_comment(comment_id) {
    if ((unreaded_comments.length > 0) && (unreaded_comments[0][0] == comment_id)) {
        $.merge(readed_comments, [comment_id]);
        unreaded_comments.shift();
        $('#' + comment_id + ' > table').removeClass("unreaded-post");
        init_refresh_comments();
    }
}

function process_comments_data(data) {
    $('#comments_container').html(data.html);
    $('#toppagination').each(function(index) {
        $(this).html(data.pagination);
    });
    $('#bottompagination').each(function(index) {
        $(this).html(data.pagination_bottom);
    });
    if (data.unreaded) {
        var new_unreaded = [];
        data.unreaded.forEach(function(item){
            var found = false;
            unreaded_comments.forEach(function(item2){
                if (item[0] == item2[0]) {
                    found = true;
                }
            })
            readed_comments.forEach(function(item2){
                if (item[0] == item2) {
                    found = true;
                }
            })
            if (!found) {
                new_unreaded = $.merge(new_unreaded, [item])
            }
        });
        unreaded_comments = $.merge(unreaded_comments, new_unreaded)
        if (unreaded_comments.length > 0) {
            $('#first_unreaded')[0].innerHTML = unreaded_comments.length;
            $('#first_unreaded').show();
        } else {
            $('#first_unreaded').hide();
        }
    }
    if (unreaded_comments.length > 0) {
        for (i = 0; i < unreaded_comments.length; i++) {
            var comment = unreaded_comments[i];
            var item = $("#" + comment[0]+ ' > table');
            item.addClass("unreaded-post");
            item.mouseenter(function() {
                var span = $(this).parent();
                var comment_id = span.attr('id');
                get_over_comment(comment_id);
            });
        }
    }
    trigger_event(on_refresh_end, 'success');
}

function scroll_to_comment(comment_id) {
    $("#" + comment_id).scrollintoview({
        duration: animation_speed,
        direction: "vertical",
        complete: function() {
            $('#' + comment_id + ' > table').removeClass("unreaded-post");
        }
    });
}

function set_page(page_num, post_id, bottom) {
    move_reply_form_back();
    var width = $('.pagination > ul').width();
    var height = $('.pagination > .pagination-btns').height();
    $('.pagination > .progress').width(width);
    $('.pagination > .progress').height(height - 21);
    
    $('.pagination > .pagination-btns').hide();
    
    $('.pagination > .progress').show();
    History.pushState(null, null, '?page=' + page_num);
    if (post_id) {
        window.location.hash = post_id;
    }
    if ((page_num > comments_page) && (unreaded_comments.length > 0)) {
        var t = unreaded_comments.length;
        for (i = 0; i < t; i++) {
            if (unreaded_comments[0][1] == comments_page) {
                get_over_comment(unreaded_comments[0][0]);
            } else {
                break;
            }
        }
    }
    $.ajax({
        mode: "abort",
        port: "comments_container",
        dataType: "json",
        type : "GET",
        url: comments_url,
        data: { page_num: page_num },
        success: function(data, textStatus, jqXHR ) {
            comments_page = page_num;
            process_comments_data(data);
            if (post_id) {
                scroll_to_comment(post_id);
            } else {
                if (bottom) {
                    $("#toppagination").scrollintoview({
                        duration: animation_speed,
                        direction: "vertical",
                    });
                }
            }
        },
        error: function(jqXHR, textStatus, errorThrown ) {
            $('.pagination > .progress').hide();
            $('.pagination > .pagination-btns').show();
            $('#comments_container')[0].innerHTML = errorThrown;
            $('#comments_container').show();
            trigger_event(on_refresh_end, 'error');
        }
    });
}

function refresh_page() {
    move_reply_form_back();
    $('#refreshcomments > #refresh').addClass("loading");
    
    $.ajax({
        mode: "abort",
        port: "comments_container",
        dataType: "json",
        type : "GET",
        url: comments_url,
        data: { page_num: comments_page },
        success: function(data, textStatus, jqXHR ) {
            $('#refreshcomments > #refresh').removeClass("loading");
            process_comments_data(data);
        },
        error: function(jqXHR, textStatus, errorThrown ) {
            $('#refreshcomments > #refresh').removeClass("loading");
            trigger_event(on_refresh_end, 'error');
        }
    });
}

function init_refresh_comments() {
    if (unreaded_comments.length <= 0) {
        $('#first_unreaded').hide();
    } else {
        $('#first_unreaded')[0].innerHTML = unreaded_comments.length;
    }
}

function first_unreaded() {
    if (unreaded_comments.length > 0) {
        var comment = unreaded_comments[0];
        $.merge(readed_comments, [comment[0]])
        unreaded_comments.shift();
        if (comment[1] == comments_page) {
            scroll_to_comment(comment[0]);
        } else {
            set_page(comment[1], comment[0] + '')
        }
    }
    init_refresh_comments();
}

$(document).ready(function() {  
    unreaded_comments.forEach(function(item){
        $('#' + item[0] + ' > table').mouseenter(function() {get_over_comment(item[0])});
    });
});

