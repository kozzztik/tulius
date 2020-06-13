import room_list from '../../forum/snippets/room_list.js'
import thread_list from '../../forum/snippets/thread_list.js'
import thread_actions from '../components/thread_actions.js'
import online_status from '../components/online_status.js'


export default LazyComponent('game_room_page', {
    template: '/static/gameforum/pages/room.html',
    data: function () {
        return {
            breadcrumbs: [],
            loading: true,
            thread: { rooms: [], threads: []},
        }
    },
    computed: {
        user: function() {return this.$root.user;},
        variation: function() {return this.$parent.variation},
    },
    methods: {
        load_api(pk) {
            this.$parent.loading_start();
            axios.get('/api/game_forum/variation/'+ this.variation.id + '/thread/' + pk + '/'
            ).then(response => {
                const api_response = response.data;
                this.breadcrumbs = []
                api_response.parents.forEach(
                    (item, i, arr) => this.breadcrumbs.push(
                        {"url": item.url, "title": item.title}
                    ));
                this.breadcrumbs.push(
                    {"url": api_response.url, "title": api_response.title});
                this.thread = api_response;
                this.loading = false;
            }).catch(error => this.$root.add_message(error, "error"))
            .then(() => {
                this.$parent.loading_end(this.breadcrumbs);
                this.loading = false;
            });
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
                '/api/game_forum/variation/'+ this.variation.id + '/thread/' + this.thread.id + '/read_mark/',
                {'comment_id': null}
            ).then(response => {
            }).catch(error => this.$root.add_message(error, "error"))
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
