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
            axios.get('/api/forum/thread/'+ pk + '/').then(response => {
                this.thread = response.data;
                this.breadcrumbs = this.$parent.thread_breadcrumbs(this.thread)
                this.loading = false;
            }).catch(error => this.$root.add_message(error, "error"))
            .then(() => {
                this.$parent.loading_end(this.breadcrumbs);
                this.loading = false;
            });
        },
        mark_all_as_readed() {
            this.$parent.loading_start();
            axios.post(
                this.thread.url + 'read_mark/', {'comment_id': null}
            ).then(response => {
            }).catch(error => this.$parent.add_message(error, "error"))
            .then(() => {
                this.$parent.loading_end(null);
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
