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
        loading: false,
        loading_counter: 0,
        show_footer: false,
        footer_content: '',
        messages: [],
        user: {},
    },
    methods: {
        loading_start() {
            this.loading_counter = this.loading_counter + 1;
            this.loading = (this.loading_counter > 0)
        },
        loading_end(items) {
            this.breadcrumb_items = items;
            this.loading_counter = this.loading_counter - 1;
            this.loading = (this.loading_counter > 0)
        },
        update_footer(show, content) {
            this.show_footer = show;
            this.footer_content = content;
        },
        add_message(message, tag) {
            this.messages.push({'tag': tag, 'text': message})
        }
    },
    created () {
        this.loading_start();
        axios.get('/api/profile').then(response => {
            this.user = response.data;
        }).catch(error => this.add_message(error, "error"))
        .then(() => {
            this.loading_end(this.breadcrumbs);
        });
    }
});
