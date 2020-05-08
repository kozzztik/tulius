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

axios.defaults.xsrfCookieName = 'csrftoken';
axios.defaults.xsrfHeaderName = "X-CSRFTOKEN";
