//import room_list from '../snippets/room_list.js'
//import thread_actions from '../snippets/thread_actions.js'
//import online_status from '../snippets/online_status.js'


export default LazyComponent('game_room_page', {
    template: '/static/gameforum/pages/room.html',
    data: function () {
        return {
            breadcrumbs: [],
            loading: true,
            thread: { rooms: [], threads: []},
            user: {},
        }
    },
    methods: {
        load_api(pk) {
            this.$parent.loading_start();
            const variation = this.$parent.variation
            axios.get('/api/game_forum/variation/'+ variation.id + '/thread/' + pk + '/'
            ).then(response => {
                const api_response = response.data;
                this.breadcrumbs = [{"url": "/forums/", "title": "Форумы"}]
                api_response.parents.forEach(
                    (item, i, arr) => this.breadcrumbs.push(
                        {"url": item.url, "title": item.title}
                    ));
                this.breadcrumbs.push(
                    {"url": api_response.url, "title": api_response.title});
                this.thread = api_response;
                this.user = this.$parent.user;
                this.loading = false;
            }).catch(error => this.$root.add_message(error, "error"))
            .then(() => {
                this.$parent.loading_end(this.breadcrumbs);
                this.loading = false;
            });
        },
    },
    mounted() {this.load_api(this.$route.params.id)},
    beforeRouteUpdate (to, from, next) {
        this.load_api(to.params.id);
        next();
    }
})
