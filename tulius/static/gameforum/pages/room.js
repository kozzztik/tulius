import room_list from '../../forum/snippets/room_list.js'
import thread_list from '../../forum/snippets/thread_list.js'
import thread_actions from '../components/thread_actions.js'
import online_status from '../components/online_status.js'
import APILoadMixin from '../../app/components/api_load_mixin.js'
import {LazyComponent} from '../../common/js/vue-common.js'
import axios from '../../common/js/axios.min.js';


export default LazyComponent('game_room_page', {
    mixins: [APILoadMixin,],
    template: '/static/gameforum/pages/room.html',
    data: function () {
        return {
            loading: true,
            thread: { rooms: [], threads: []},
        }
    },
    computed: {
        urls: function() {return this.$parent.urls;},
        variation: function() {return this.$parent.variation},
    },
    methods: {
        load_api(route) {
            return axios.get(this.urls.thread_api(route.params.id)
            ).then(response => {
                this.thread = response.data;
                this.breadcrumbs = this.$parent.thread_breadcrumbs(this.thread);
                this.loading = false;
            })
        },
        role_with_link(role_id) {
            var role;
            for (role of this.variation.characters) {
                if (role.id == role_id)
                    return true;
            }
            return false;
        },
        show_role_modal(role_id) {
            this.$refs.thread_actions.show_char_modal(role_id);
        },
        mark_all_as_read() {
            this.$parent.loading_start();
            axios.post(
                this.urls.thread_api(this.thread.id) + 'read_mark/',
                {'comment_id': null}
            ).then(response => {
            }).catch().then(() => {
                this.$parent.loading_end();
                this.load_api(this.$route);
            });
        },
        loading_start() {this.$parent.loading_start()},
        loading_end(breadcrumbs) {this.$parent.loading_end(breadcrumbs)},
    },
})
