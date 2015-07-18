function delete_material(url, name) {
    $('#delete-material-button')[0].attributes['href'].nodeValue = url;
    $('#delete-material-name')[0].innerHTML = name;
    $('#delete-material-popup').modal('show');
};
