function formset_delete(prefix, widget, id) {
    var row = $("#id" + prefix + widget + "_" + id)
    var delete_btn_row = row.find(".formset_delete")
    var delete_btn = delete_btn_row.find("a")
    $( '<div class="formset_ajax_loader"></div>' ).insertBefore(delete_btn);
    delete_btn.hide()
    $.ajax({
        dataType: "json",
        url: "?widget="+widget+"&action=delete_item",
        type: "POST",
        data: {
            id: id,
        },
        success: function(data) {
            row.detach();
        },
        error: function() {
            delete_btn_row.find(".formset_ajax_loader").detach();
            delete_btn.show();
        }
    });

}

function formset_add(prefix, widget) {
    var row = $("#id" + prefix + widget + "_add")
    var add_btn_row = row.find(".formset_add")
    var add_btn = add_btn_row.find("a")
    $( '<div class="formset_ajax_loader"></div>' ).insertBefore(add_btn);
    add_btn.hide();
    var form = $("#id" + prefix + widget + "_form");
    form.ajaxSubmit({
        dataType: "html",
        url: "?widget="+widget+"&action=add_item",
        type: "POST",
        success: function(data) {
            form.replaceWith(data);
        },
        error: function() {
            add_btn_row.find(".formset_ajax_loader").detach();
            add_btn.show();
        }
    });

}