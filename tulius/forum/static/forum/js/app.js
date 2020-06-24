export default Vue.component('forum_app', {
    template: '<router-view></router-view>',
    data: function () {
        return {
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
            for (var item of this.thread.parents)
                this.breadcrumbs.push({
                    title: item.title,
                    url: {
                        name: 'forum_room',
                        params: {id: item.id},
                    },
                });
            this.breadcrumbs.push({
                title: this.thread.title,
                url: {
                    name: thread.room ? 'forum_room' : 'forum_thread'
                    params: {id: this.thread.id},
                },
            });
            return breadcrumbs;
        }
    },

})
