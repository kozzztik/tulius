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

function production_url() {
    var schema = window.location.protocol == 'https:' ? 'wss://' : 'ws://';
    return schema + window.location.host + '/api/ws/';
}

var websockets_url = production_url();

Vue.use(VueNativeSock.default, websockets_url, {
    reconnection: true,
    reconnectionDelay: 3000,
    format: 'json'
});

var app = new Vue({
    el: '#vue_app',
    router: router,
    data: {
        debug: false,
        breadcrumb_items: [],
        loading: true,
        loading_counter: 0,
        show_footer: false,
        footer_content: '',
        messages: [],
        user: {},
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
            if (items) {
                if (items.length > 0)
                    document.title = items[items.length - 1].title;
                this.breadcrumb_items = items;
            }
            this.loading_counter = this.loading_counter - 1;
            if (this.loading_counter < 0)
                this.loading_counter = 0;
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
            if (tag == 'error') tag = 'danger';
            this.messages.push({'tag': tag, 'text': message})
        }
    },
    mounted() {
        axios.get('/api/app_settings/').then(response => {
            this.debug = response.data.debug;
            this.user = response.data.user;
            this.loading = false;
        })
    },
});

Vue.app_error_handler = (message, tag) => app.add_message(message, tag);


// Add a request interceptor
axios.interceptors.request.use(
    config => config,
    error => {
        Vue.app_error_handler(error, "error")
        return Promise.reject(error);
    }
);

// Add a response interceptor
axios.interceptors.response.use(
    response => response,
    error => {
        Vue.app_error_handler(error, "error")
        return Promise.reject(error);
    }
);