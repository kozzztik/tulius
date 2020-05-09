function LazyComponent(name, defs) {
    return Vue.component(name, function(resolve, reject) {
        fetch(defs['template']).then(response => response.text()).then(
            function(response) {
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
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

axios.defaults.xsrfCookieName = 'csrftoken';
axios.defaults.xsrfHeaderName = "X-CSRFTOKEN";

Vue.use(VueLoading);
Vue.component('loading', VueLoading)