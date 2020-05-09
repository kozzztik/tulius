export default LazyComponent('forum_online_status', {
    template: '/static/forum/snippets/online_status.html',
    props: ['thread'],
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
            const url = '/api/forum/online_status/' + (pk ? pk + '/' : '');
            axios.get(url).then(response => {
                this.users = response.data.users;
            }).catch(error => this.$parent.$parent.add_message(error, "error"))
            .then(() => {
                this.loading = false;
            });
        },
    },
})
