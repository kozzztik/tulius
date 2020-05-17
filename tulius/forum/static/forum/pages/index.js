import room_list from '../snippets/room_list.js'


export default LazyComponent('forum_index_page', {
    template: '/static/forum/pages/index.html',
    data: function () {
        return {
            loading: true,
            index: {},
        }
    },
    methods: {
        load_api() {
            this.$parent.loading_start();
            axios.get('/api/forum/').then(response => {
                var api_response = response.data;
                for (var num in api_response['groups']) {
                    api_response.groups[num]['collapsed'] = false;
                }
                this.index = api_response;
                //this.$parent.update_footer(true, 'online users')
                if (this.$parent.user.authenticated) {
                    axios.get('/api/forum/collapse/').then(response => {
                        for (var key in response.data) {
                            for (var num in this.index.groups) {
                                if (this.index.groups[num].id == key) {
                                    this.index.groups[num].collapsed = response.data[key];
                                    break;
                                }
                            }
                        }
                    });
                }
            }).catch(error => this.$parent.add_message(error, "error"))
            .then(() => {
                this.$parent.loading_end([
                    {"url": "/forums/", "title": "Форумы", 'old': true}
                ]);
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
        }
    },
    mounted() {this.load_api()},
    beforeRouteUpdate (to, from, next) {
        this.load_api();
        next();
    }
})
