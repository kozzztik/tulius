import room_list from '../snippets/room_list.js'


export default LazyComponent('forum_room_page', {
    template: '/static/forum/pages/room.html',
    data: function () {
        return {
            breadcrumbs: [],
            loading: true,
            thread: { rooms: [], threads: []},
        }
    },
    methods: {
        load_api(pk) {
            this.$parent.loading_start();
            axios
                .get('/api/forum/thread/'+ pk)
                .then(response => {
                    const api_response = response.data;
                    this.breadcrumbs = [{"url": "/forums/", "title": "Форумы"}]
                    api_response.parents.forEach(
                        (item, i, arr) => this.breadcrumbs.push(
                            {"url": item.url, "title": item.title}
                        ));
                    this.breadcrumbs.push(
                        {"url": api_response.url, "title": api_response.title});
                    this.thread = api_response
                    this.loading = false;
                }).catch(error => this.$parent.add_message(error, "error"))
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
