import Vue from 'vue'
import routes from './routes.js'
import breadcrumbs from '../common/components/breadcrumbs.js'
import main_menu from '../common/components/main_menu.js'
import CKEditor from '../ckeditor4/ckeditor4-vue/index.js';
import axios from '../common/js/axios.min.js';
import VueLoading from '../common/js/vue-loading-overlay.js';
import Tinybox from '../common/js/vue-tinybox.js';
import VueMultiselect from '../common/components/vue-multiselect.min.js';
import VueRouter from '../common/js/vue-router.js';
import VueNativeSock from '../common/js/vue-native-websocket.js';
import BootstrapVue from '../common/bootstrap-vue/bootstrap-vue.min.js'
import IconsPlugin from '../common/bootstrap-vue/bootstrap-vue-icons.min.js'
import popper from '../common/bootstrap-vue/popper.min.js'

axios.defaults.xsrfCookieName = 'csrftoken';
axios.defaults.xsrfHeaderName = "X-CSRFTOKEN";

Vue.use(VueRouter)
Vue.use(BootstrapVue)
Vue.use(IconsPlugin)
Vue.use( CKEditor );
Vue.use(VueLoading);
Vue.component('loading', VueLoading)
Vue.component('Tinybox', Tinybox);
Vue.component('multiselect', VueMultiselect.default)

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

Vue.use(VueNativeSock, websockets_url, {
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
        app.add_message(error, "error")
        return Promise.reject(error);
    }
);

// Add a response interceptor
axios.interceptors.response.use(
    response => response,
    error => {
        app.add_message(error, "error")
        return Promise.reject(error);
    }
);

export default app;