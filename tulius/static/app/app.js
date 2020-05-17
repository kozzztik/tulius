import routes from './routes.js'
import breadcrumbs from '/static/common/components/breadcrumbs.js'
import main_menu from '/static/common/components/main_menu.js'
import CKEditor from '/static/ckeditor4/ckeditor4-vue/index.js';

Vue.use( CKEditor );

const NotFound = { template: '<p>Страница не найдена</p>' }

const router = new VueRouter({
    mode: 'history',
    routes: routes,
})

var app = new Vue({
    el: '#vue_app',
    router: router,
    data: {
        breadcrumb_items: [],
        loading: false,
        loading_counter: 0,
        show_footer: false,
        footer_content: '',
        messages: [],
        user: {
            'authenticated': false,
            'anonymous': true,
            'superuser': false,
        },
    },
    methods: {
        loading_start() {
            this.loading_counter = this.loading_counter + 1;
            const new_loading = (this.loading_counter > 0);
            if (this.loading != new_loading) {
                this.loading = new_loading;
            }
        },
        loading_end(items) {
            if (items && items.length > 0) {
                document.title = items[items.length - 1].title;
            }
            this.breadcrumb_items = items;
            this.loading_counter = this.loading_counter - 1;
            const new_loading = (this.loading_counter > 0);
            if (this.loading != new_loading) {
                this.loading = new_loading;
            }
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

Vue.app_error_handler = (message, tag) => app.add_message(message, tag);
