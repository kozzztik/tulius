function do_trustmark(target_id, value) {
    $.ajax({
        // try to leverage ajaxQueue plugin to abort previous requests
        mode: "abort",
        // limit abortion to this input
        port: "trustmark" + target_id,
        dataType: "json",
        url: trustmarks_url,
        data: {
            value: value,
            target_id: target_id,
        },
        success: function(data) {
            if (data.success) {
                my_mark = data.my_mark;
                all_marks = data.all_marks;
                $("[id='trustmark-" + target_id + "-allmark']").each(function(index) {
                    $(this)[0].innerHTML = all_marks + "%";
                });
                $("[id='trustmark-" + target_id + "-mymark']").each(function(index) {
                    $(this)[0].innerHTML = my_mark + "%";
                });
            }
        }
    });
};
