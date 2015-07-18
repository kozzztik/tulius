function do_vote(voting_id) { 
    var value = $(":radio[name=voting-radio-" + voting_id + "]").filter(":checked").val();
    if (value === undefined) {
                    
    } else {
        $.ajax({
            // try to leverage ajaxQueue plugin to abort previous requests
            mode: "abort",
            // limit abortion to this input
            port: "vote" + voting_id,
            dataType: "json",
            url: vote_options.url,
            data: {
                choice_id: value
            },
            success: function(data) {
                $("#voting-" + voting_id)[0].innerHTML = data.html
            },
            error: function(data) {
                $("#voting-error-" + voting_id)[0].innerHTML = data.responseText;
            }
        });
    }
};

function do_vote_preview(voting_id) {
    $.ajax({
        // try to leverage ajaxQueue plugin to abort previous requests
        mode: "abort",
        // limit abortion to this input
        port: "vote" + voting_id,
        dataType: "json",
        url: vote_options.preview_url,
        data: {
           voting_id: voting_id
        },
        success: function(data) {
            $("#name-body-" + voting_id)[0].innerHTML = data.html;
            $("#votes-count-" + voting_id).hide();
        },
        error: function(data) {
            $("#voting-error-" + voting_id)[0].innerHTML = data.responseText;
        }
    });
};
