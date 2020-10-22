export default LazyComponent('game_forum_online_status', {
    template: '/static/gameforum/components/online_status.html',
    props: ['variation', 'thread'],
    data: function () {
        return {
            loading: true,
            users: [],
        }
    },
    watch: {
        thread: function (val, oldVal) {
          this.load_api(val.id);
        },
    },
    methods: {
        load_api(pk) {
            axios.get(
                '/api/game_forum/variation/'+ this.variation.id + '/thread/' + this.thread.id + '/online_status/',
            ).then(response => {
                if (this.thread.rights.strict_read === null)
                    this.users = response.data.users
                else {
                    var users = []
                    for (var user of response.data.users)
                        if (this.thread.rights.strict_read.indexOf(user.id) != -1)
                            users.push(user);
                    this.users = users;
                }
                var user_ids = [];
                var user;
                for(user of this.users) {
                    user_ids.push(user.id);
                }
                if (this.thread)
                    this.thread.online_ids = user_ids;
            }).catch(error => this.$parent.$parent.add_message(error, "error"))
            .then(() => {
                this.loading = false;
            });
        },
        role_with_link(role_id) {
            for (var role of this.variation.characters)
                if (role.id == role_id)
                    return true;
            return false;
        },
        show_role_modal(role_id) {this.$parent.show_role_modal(role_id)}
    },
    mounted() {
        if (this.thread.id)
            this.load_api(this.thread.id)
    },
})
