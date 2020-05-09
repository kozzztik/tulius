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
        loading_end(items) {this.$parent.loading_end(items)},
        update_footer(show, content) {this.$parent.update_footer(show, content)},
        update_route(route) {
            this.loading_end([]);
            this.update_footer(false, '');
            this.currentRoute = route;
        }
    }
})

var app = new Vue({
    el: '#content-center',
    data: {
        breadcrumb_items: [],
        loading: true,
        show_footer: false,
        footer_content: '',
    },
    methods : {
        loading_start() {this.loading = true},
        loading_end(items) {
            this.breadcrumb_items = items;
            this.loading = false;
        },
        update_footer(show, content) {
            this.show_footer = show;
            this.footer_content = content;
        }
    }
});

window.addEventListener('popstate', () => {
    forum_app.currentRoute = window.location.pathname
})
