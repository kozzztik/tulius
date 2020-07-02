export default LazyComponent('game_extended_search', {
    template: '/static/gameforum/pages/extended_search.html',
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
        user_search(query) {
            return this.variation.characters;
        },
    },
})
