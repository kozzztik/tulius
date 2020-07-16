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
        }
    },
    computed: {
        urls() {return this.$parent.urls},
    },
    methods: {
        load_api(route) {
            return axios.post(
                this.urls.search_api(route.params.id),
                route.query,
            ).then(response => {
                this.thread = response.data.thread;
                this.conditions = response.data.conditions;
                for (var entry of response.data.results)
                    entry.thread.online_ids = [];
                this.results = response.data.results;
                this.breadcrumbs = this.$parent.thread_breadcrumbs(this.thread);
                this.breadcrumbs.push({
                    'title': 'Результаты поиска',
                    'url': route
                })
            })
        },
    },
})
