import urls from './urls.js'

export default Vue.component('forum_app', {
    template: '<router-view></router-view>',
    data: function () {
        return {
            urls: urls,
        }
    },
    methods: {
        loading_start() {this.$root.loading_start()},
        loading_end(breadcrumbs) {
            if (!breadcrumbs)
                return this.$root.loading_end(breadcrumbs);
            this.$root.loading_end([{
                title: "Форумы",
                url: {name: 'forum_root',},
            }, ...breadcrumbs]);
        },
        thread_breadcrumbs(thread) {
            var breadcrumbs = []
            for (var item of thread.parents)
                breadcrumbs.push({
                    title: item.title,
                    url: this.urls.room(item.id),
                });
            breadcrumbs.push({
                title: thread.title,
                url: thread.room ? this.urls.room(thread.id) : this.urls.thread(thread.id),
            });
            return breadcrumbs;
        },
    },

})
