import room_list from '../snippets/room_list.js'


export default LazyComponent('forum_index_page', {
    template: '/static/forum/pages/index.html',
    data: function () {
        return {
            loading: true,
            index: {groups: []},
            user: {is_anonymous: true},
            breadcrumbs: [
                {"url": "/forums/", "title": "Форумы"}
            ],
        }
    },
    methods: {
        load_api() {
            this.$parent.loading_start();
            axios.get('/api/forum/').then(response => {
                var api_response = response.data;
                for (var group of api_response['groups'])
                    group['collapsed'] = false;
                this.index = api_response;
                if (this.$parent.user.authenticated) {
                    axios.get('/api/forum/collapse/').then(response => {
                        for (var key in response.data)
                            for (var group of this.index.groups)
                                if (group.id == key) {
                                    group.collapsed = response.data[key];
                                    break;
                                }
                    });
                }
            }).catch(error => this.$parent.add_message(error, "error"))
            .then(() => {
                this.$parent.loading_end(this.breadcrumbs);
                this.loading = false;
            });
        },
        collapse: function (event) {
            var group_id = event.target.attributes.groupid.nodeValue;
            for (var num in this.index.groups) {
                if (this.index.groups[num].id == group_id) {
                    var value = !this.index.groups[num].collapsed;
                    this.index.groups[num].collapsed = value;
                    axios.post(
                        '/api/forum/collapse/' + group_id, {'value': value})
                    break;
                }
            }
        },
        mark_all_as_readed() {
            this.$parent.loading_start();
            axios.post('/api/forum/read_mark/', {'comment_id': null}
            ).then(response => {
            }).catch(error => this.$parent.add_message(error, "error"))
            .then(() => {
                this.$parent.loading_end(this.breadcrumbs);
                this.load_api();
            });
        },
    },
    mounted() {
        this.user = this.$parent.user;
        this.load_api()
    },
    beforeRouteUpdate (to, from, next) {
        this.load_api();
        next();
    }
})
