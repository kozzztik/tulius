import APILoadMixin from '../../app/components/api_load_mixin.js'
import thread_selector from '../components/thread_selector.js'
import {LazyComponent} from '../../common/js/vue-common.js'
import axios from '../../common/js/axios.min.js';


export default LazyComponent('forum_extended_search_page', {
    props: {
        user_search: {
			type: Function,
	    },
        show_root: {
			type: Boolean,
			default: true,
	    },
	},
    mixins: [APILoadMixin,],
    template: '/static/forum/pages/extended_search.html',
    data: function () {
        return {
            thread: {id: null},
            user_options: [],
            form: {
                users: [],
                not_users: [],
                date_from: null,
                date_to: null,
                text: '',
            },
        }
    },
    computed: {
        urls() {return this.$parent.urls},
    },
    methods: {
        load_api(route) {
            //cleanup form
            this.form.text = route.query.text || '';
            this.form.date_from = route.query.date_from || null;
            this.form.date_to = route.query.date_to || null;
            this.form.users = [];
            if (route.query.users) {
                var pks = route.query.users;
                if (!Array.isArray(pks))
                    pks = [pks];
                if (pks.length > 0)
                    axios.options(
                        this.urls.search_api, {'params': {'pks': pks.join()}}
                    ).then(response => this.form.users = response.data.users)
            }
            this.form.not_users = [];
            if (route.query.not_users) {
                var pks = route.query.not_users;
                if (!Array.isArray(pks))
                    pks = [pks];
                if (pks.length > 0)
                    axios.options(
                        this.urls.search_api, {'params': {'pks': pks.join()}}
                    ).then(response => this.form.not_users = response.data.users)
            }
            this.thread = null;
            if (route.query.thread_id)
                return axios.get(this.urls.thread_api(route.query.thread_id)
                ).then(response => {
                    this.thread = response.data;
                    this.breadcrumbs = this.$parent.thread_breadcrumbs(this.thread);
                    this.breadcrumbs.push({
                        'title': 'Поиск',
                        'url': route
                    })
                })
            else {
                this.breadcrumbs = [{
                    'title': 'Поиск',
                    'url': route
                }]
            }
        },
        form_submit() {
            var users = [];
            var not_users = [];
            for (var user of this.form.users)
                users.push(user.id);
            for (var user of this.form.not_users)
                not_users.push(user.id);
            var form = JSON.parse(JSON.stringify(this.form));
            form.users = users;
            form.not_users = not_users;
            form.thread_id = null;
            if (this.thread && this.thread.id)
                form.thread_id = this.thread.id;
            this.$router.push(
                this.urls.search_results(form));
        },
        do_search(query) {
            var res = (this.user_search||this.default_user_search)(query);
            if (res && (typeof res.then === 'function')) {
                res.then(response => this.user_options = response);
                return res;
            }
            this.user_options = res || this.user_options;
        },
        default_user_search(query) {
            if (query.length < 3)
                return
            return axios.options(
                this.urls.search_api, {params: {query: query}}
            ).then(response => response.data.users)
        },
    },
})
