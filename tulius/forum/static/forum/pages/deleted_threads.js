import room_list from '../snippets/room_list.js'
import thread_list from '../snippets/thread_list.js'
import thread_actions from '../snippets/thread_actions.js'
import online_status from '../snippets/online_status.js'
import APILoadMixin from '../../app/components/api_load_mixin.js'


export default LazyComponent('forum_room_page_deleted', {
    template: '/static/forum/pages/deleted_threads.html',
    mixins: [APILoadMixin,],
    data: () => ({
        loading: true,
        thread: { rooms: [], threads: []},
    }),
    computed: {
        urls() {return this.$parent.urls},
    },
    methods: {
        load_api(route) {
            return axios.get(this.urls.thread_api(route.params.id) + '?deleted=1'
            ).then(response => {
                this.thread = response.data;
                this.breadcrumbs = this.$parent.thread_breadcrumbs(this.thread)
                this.breadcrumbs.push({
                    title: "Удаленное",
                    url: this.urls.deleted_threads(route.params.id)})
                this.loading = false;
            })
        },
        mark_all_as_readed() {
            this.$parent.loading_start();
            axios.post(
                this.thread.url + 'read_mark/', {'comment_id': null}
            ).then(response => {}).then(() => {
                this.$parent.loading_end(null);
                this._load_api(this.$route);
            });
        },
    },
})
