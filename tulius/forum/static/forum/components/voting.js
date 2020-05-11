export default LazyComponent('forum_voting', {
    template: '/static/forum/components/voting.html',
    props: ['comment', 'user'],
        data: function () {
        return {
            loading: true,
            show_results: false,
            voting: {},
            choice: null,
        }
    },
    methods: {
        load_api(pk) {
            this.loading = true;
            axios.get('/api/forum/comment/' + pk + '/voting/').then(response => {
                this.voting = response.data
            }).catch(
                error => Vue.app_error_handler(error, "error")
            )
            .then(() => {
                this.loading = false;
            });
        },
        do_vote() {
            if (!this.choice) {
                return;
            }
            this.loading = true;
            axios.post(
                '/api/forum/comment/' + this.comment.id + '/voting/',
                {'choice': this.choice}
            ).then(response => {
                this.voting = response.data;
            }).catch(
                error => Vue.app_error_handler(error, "error")
            )
            .then(() => {
                this.loading = false;
            });

        }
    },
    mounted() {this.load_api(this.comment.id)},
})
