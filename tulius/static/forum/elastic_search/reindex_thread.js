import {LazyComponent} from '../../common/js/vue-common.js'
import axios from '../../common/js/axios.min.js';


export default LazyComponent('forum_elastic_reindex_thread', {
    template: '/static/forum/elastic_search/reindex_thread.html',
    data: function () {
        return {
            finished: false,
            threads: 0,
            comments: 0,
            pk: null,
        }
    },
    computed: {
        urls() {return this.$parent.urls},
    },
    methods: {
        load_api(route) {
            if (route.params.id)
                var url = this.urls.elastic_reindex_thread_api(route.params.id)
            else
                var url = this.urls.elastic_reindex_forum_api;
            this.pk = route.params.id;
            return axios.post(url).then(response => {
                this.results = response.data.result;
                this.finished = false;
                this.threads = 0;
                this.comments = 0;
                this.$parent.loading_end([{
                    title: 'Переиндексация ElasticSearch',
                    url: '',
                }]);
            }).catch(error => {this.finished = true;})
        },
        websock_message(msg) {
            var data = JSON.parse(msg.data);
            if ((data['.namespaced'] == 'task_update')&(data['.action'] == 'index_forum_elastic_search')) {
                this.finished = data.finished;
                this.threads = data.threads;
                this.comments = data.comments;
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
