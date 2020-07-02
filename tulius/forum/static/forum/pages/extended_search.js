import APILoadMixin from '../../app/components/api_load_mixin.js'


export default LazyComponent('forum_extended_search_page', {
    props: {
        user_search: {
			type: Function,
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
            return axios.get(this.urls.thread_api(route.params.id)
            ).then(response => {
                this.thread = response.data;
                this.breadcrumbs = this.$parent.thread_breadcrumbs(this.thread);
                this.breadcrumbs.push({
                    'title': 'Поиск',
                    'url': route
                })
                //cleanup form
                form.text = '';
                form.date_from = null;
                form.date_to = null;
                form.users = [];
                form.not_users = [];
            })
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
            this.$router.push(
                this.urls.search_results(this.thread.id, form));
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
                this.thread.url + 'granted_rights/', {params: {query: query}}
            ).then(response => response.data.users)
        },
    },
})
