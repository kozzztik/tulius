export function LazyComponent(name, defs) {
    var template_resolved = false;
    return Vue.component(name, function(resolve, reject) {
        if (template_resolved)
            return resolve(defs);
        fetch(defs['template']).then(response => response.text()).then(
            function(response) {
                template_resolved = true;
                defs['template'] = response;
                resolve(defs);
            }
        )
    })
}

export function forum_datetime(d) {
    return ((
        '0' + d.getDate()).slice(-2) + '.' +
        ('0' + (d.getMonth() + 1)).slice(-2) + '.' +
        d.getFullYear() + ' ' +
        ('0' + d.getHours()).slice(-2) + ':' +
        ('0' + d.getMinutes()).slice(-2));
}
