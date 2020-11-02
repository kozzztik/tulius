import {LazyComponent} from '../../common/js/vue-common.js'


export default LazyComponent('game_search_results', {
    template: '/static/gameforum/pages/search_results.html',
    data: function () {
        return {}
    },
    computed: {
        urls() {return this.$parent.urls},
        variation: function() {return this.$parent.variation},
    },
    methods: {
        loading_start() {this.$parent.loading_start()},
        loading_end(breadcrumbs) {this.$parent.loading_end(breadcrumbs)},
        thread_breadcrumbs(thread) {return this.$parent.thread_breadcrumbs(thread)},
    },
    beforeRouteUpdate (to, from, next) {
        this.$refs.search._load_api(to);
        next();
    },
})
