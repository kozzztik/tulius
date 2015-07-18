function do_action(action) {
    var modal=$('#AddUserModal');
    modal[0].attributes['action'].nodeValue = '?action=' + action;
    modal.modal('show');
}

function delete_user(action, user_id) {
    $.ajax({
        dataType: "json",
        type : "POST",
        url: '',
        data: {
            action: action,
            user_id: user_id
        },
    });
}

function delete_admin(user_id) {
    $('#admin' + user_id).hide()
    delete_user('delete_admin', user_id);
}

function delete_guest(user_id) {
    $('#guest' + user_id).hide()
    delete_user('delete_guest', user_id);
}
