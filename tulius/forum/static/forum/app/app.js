var urls = {
    room: room_id => ({name: 'forum_room', params: {id: room_id},}),
    add_room: room_id => room_id ? {name: 'forum_add_room', params: {id: room_id}
        } : {name: 'forum_add_root_room'},
    thread: (thread_id, page) => ({
        name: 'forum_thread',
        params: {id: thread_id},
        query: { page: page },
    }),
    comment: comment => ({
        name: 'forum_thread',
        params: { id: comment.thread.id, },
        query: { page: comment.page },
        hash: '#' + comment.id,
    }),
    edit_thread: thread_id => `/forums/edit_thread/${thread_id}/`,
	edit_comment: comment_id => ({
        name: 'forum_edit_comment',
        params: { id: comment_id },
	}),
    thread_api: pk => `/api/forum/thread/${pk}/`,
    comment_api: pk => `/api/forum/comment/${pk}/`,
    root_api: '/api/forum/',
}

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
        }
    },

})
