export default LazyComponent('forum_elastic_reindex_all', {
    template: '/static/forum/elastic_search/reindex_all.html',
    data: function () {
        return {
            finished: false,
            results: {},
        }
    },
    computed: {
        urls() {return this.$parent.urls},
    },
    methods: {
        load_api(route) {
            return axios.post(this.urls.elastic_reindex_all_api).then(response => {
                this.results = response.data.result;
                this.finished = false;
                this.$parent.loading_end([{
                    title: 'Переиндексация ElasticSearch',
                    url: '',
                }]);
            }).catch(error => {this.finished = true;})
        },
        websock_message(msg) {
            var data = JSON.parse(msg.data);
            if ((data['.namespaced'] == 'task_update')&(data['.action'] == 'index_all_elastic_search')) {
                this.finished = data.finished;
                this.results = data.counters;
            }
        },
    },
    mounted() {
        this.load_api(this.$route);
        this.$options.sockets.onmessage = this.websock_message;
    },
    beforeRouteUpdate (to, from, next) {
        this.load_api(to);
        next();
    },
})
