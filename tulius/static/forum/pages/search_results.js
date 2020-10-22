import thread_actions from '../snippets/thread_actions.js'
import comment from '../snippets/comment.js'
import APILoadMixin from '../../app/components/api_load_mixin.js'


export default LazyComponent('forum_search_results', {
    mixins: [APILoadMixin,],
    template: '/static/forum/pages/search_results.html',
    data: function () {
        return {
            thread: {online_ids: [], id: null},
            conditions: [],
            results: [],
            page: 1,
            pagination: {},
        }
    },
    computed: {
        urls() {return this.$parent.urls},
    },
    methods: {
        load_api(route) {
            var query = JSON.parse(JSON.stringify(route.query));
            if (query.users && !Array.isArray(query.users))
                query.users = [query.users];
            if (query.not_users && !Array.isArray(query.not_users))
                query.not_users = [query.not_users];
            return axios.post(this.urls.search_api, query).then(response => {
                this.page = response.data.page;
                this.thread = response.data.thread;
                this.pagination = response.data.pagination;
                this.conditions = response.data.conditions;
                for (var entry of response.data.results)
                    entry.thread.online_ids = [];
                this.results = response.data.results;
                this.breadcrumbs = [];
                if (this.thread)
                    this.breadcrumbs = this.$parent.thread_breadcrumbs(this.thread);
                this.breadcrumbs.push({
                    'title': 'Результаты поиска',
                    'url': route
                })
            })
        },
    },
})
