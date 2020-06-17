import room_list from '../snippets/room_list.js'
import thread_list from '../snippets/thread_list.js'
import thread_actions from '../snippets/thread_actions.js'
import online_status from '../snippets/online_status.js'


export default LazyComponent('forum_room_page', {
    template: '/static/forum/pages/room.html',
    data: function () {
        return {
            breadcrumbs: [],
            loading: true,
            thread: { rooms: [], threads: []},
        }
    },
    computed: {
        user: function() {return this.$root.user;}
    },
    methods: {
        load_api(pk) {
            this.$parent.loading_start();
            axios.get('/api/forum/thread/'+ pk).then(response => {
                const api_response = response.data;
                this.breadcrumbs = [{"url": "/forums/", "title": "Форумы"}]
                api_response.parents.forEach(
                    (item, i, arr) => this.breadcrumbs.push({
                        title: item.title,
                        url: {
                            name: 'forum_room',
                            params: {id: item.id},
                        },
                    }));
                this.breadcrumbs.push({
                    title: api_response.title,
                    url: {
                        name: 'forum_room',
                        params: {id: api_response.id},
                    },
                });
                this.thread = api_response;
                this.loading = false;
            }).catch(error => this.$parent.add_message(error, "error"))
            .then(() => {
                this.$parent.loading_end(this.breadcrumbs);
                this.loading = false;
            });
        },
        mark_all_as_readed() {
            this.$parent.loading_start();
            axios.post(
                '/api/forum/thread/'+ this.thread.id + '/read_mark/',
                {'comment_id': null}
            ).then(response => {
            }).catch(error => this.$parent.add_message(error, "error"))
            .then(() => {
                this.$parent.loading_end(this.breadcrumbs);
                this.load_api(this.thread.id);
            });
        },
    },
    mounted() {this.load_api(this.$route.params.id)},
    beforeRouteUpdate (to, from, next) {
        this.load_api(to.params.id);
        next();
    }
})
