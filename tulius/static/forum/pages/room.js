import room_list from '../snippets/room_list.js'
import thread_list from '../snippets/thread_list.js'
import thread_actions from '../snippets/thread_actions.js'
import online_status from '../snippets/online_status.js'
import APILoadMixin from '../../app/components/api_load_mixin.js'
import {LazyComponent} from '../../common/js/vue-common.js'
import axios from '../../common/js/axios.min.js';


export default LazyComponent('forum_room_page', {
    template: '/static/forum/pages/room.html',
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
            return axios.get(this.urls.thread_api(route.params.id)
            ).then(response => {
                this.thread = response.data;
                this.breadcrumbs = this.$parent.thread_breadcrumbs(this.thread)
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
        loading_start() {this.$parent.loading_start()},
        loading_end(breadcrumbs) {this.$parent.loading_end(breadcrumbs)},
    },
})
