import {LazyComponent} from '../../common/js/vue-common.js'
import axios from '../../common/js/axios.min.js';


export default LazyComponent('forum_fix_counters', {
    template: '/static/forum/pages/fix_counters.html',
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
            this.$parent.loading_end([{
                title: 'Перерасчет счетчиков',
                url: '',
            }]);
            if (route.params.id)
                var url = this.urls.thread_fix_api(route.params.id)
            else
                var url = '/api/forum/fix/';
            axios.post(url).then(response => {
                this.results = response.data.result;
                this.finished = true;
            }).catch(error => {this.finished = true;})
        },
        websock_message(msg) {
            var data = JSON.parse(msg.data);
            if (data['.namespaced'] != 'fixes_update')  return;
            this.results = data.data;
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
