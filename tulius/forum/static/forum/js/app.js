import routes from './routes.js'
import breadcrumbs from '/static/common/components/breadcrumbs.js'

const NotFound = { template: '<p>Страница не найдена</p>' }

const router = new VueRouter({
    mode: 'history',
    routes: routes,
})

var app = new Vue({
    el: '#content-center',
    router: router,
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
