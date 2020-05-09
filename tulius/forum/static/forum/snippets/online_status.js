export default LazyComponent('forum_online_status', {
    template: '/static/forum/snippets/online_status.html',
    props: ['thread'],
    data: function () {
        return {
            loading: true,
            users: [],
        }
    },
    methods: {
        load_api(pk) {
            const url = '/api/forum/online_status/' + (pk ? pk + '/' : '');
            axios.get(url).then(response => {
                this.users = response.data.users;
            }).catch(error => this.$parent.$parent.add_message(error, "error"))
            .then(() => {
                this.loading = false;
            });
        },
    },
    mounted() {this.load_api(
        this.$route.params.id
    )},
    beforeRouteUpdate (to, from, next) {
        this.load_api(to.params.id);
        next();
    }
})
