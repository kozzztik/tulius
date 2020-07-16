function LazyComponent(name, defs) {
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

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function forum_datetime(d) {
    return ((
        '0' + d.getDate()).slice(-2) + '.' +
        ('0' + (d.getMonth() + 1)).slice(-2) + '.' +
        d.getFullYear() + ' ' +
        ('0' + d.getHours()).slice(-2) + ':' +
        ('0' + d.getMinutes()).slice(-2));
}

axios.defaults.xsrfCookieName = 'csrftoken';
axios.defaults.xsrfHeaderName = "X-CSRFTOKEN";

Vue.use(VueLoading);
Vue.component('loading', VueLoading)
Vue.use(Tinybox);
Vue.component('multiselect', VueMultiselect.default)
