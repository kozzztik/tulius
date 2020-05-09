import routes from './routes.js'
import breadcrumbs from '/static/common/components/breadcrumbs.js'

const NotFound = { template: '<p>Страница не найдена</p>' }


var forum_app = Vue.component('forum_app', {
    template: '<div></div>',
    data: () => { return {
        currentRoute: window.location.pathname,
    }},
    params: ['loading'],
    computed: {
        ViewComponent () {
            return routes[this.currentRoute] || NotFound
        }
    },
    render (h) {
        return h(this.ViewComponent)
    },
    methods : {
        loading_start() {this.$parent.loading_start()},
        loading_end(items) {this.$parent.loading_end(items)}
    }
})

var app = new Vue({
    el: '#content-center',
    data: {
        breadcrumb_items: [],
        loading: true,
        "forum_app": forum_app,
        "breadcrumbs": breadcrumbs,
    },
    methods : {
        loading_start() {this.loading = true},
        loading_end(items) {
            this.breadcrumb_items = items;
            this.loading = false;
        }
    }
});

window.addEventListener('popstate', () => {
    app.currentRoute = window.location.pathname
})
