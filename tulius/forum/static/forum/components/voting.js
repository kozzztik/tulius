export default LazyComponent('forum_voting', {
    template: '/static/forum/components/voting.html',
    props: {
        comment: {
            type: Object,
        },
        editor: {
            type: Boolean,
            default: false,
        },
    },
    data: function () {
        return {
            loading: false,
            show_results: false,
            choice: null,
            add_media_label: "Добавить голосование"
        }
    },
    computed: {
        user: function() {return this.$root.user;},
        can_add_media: function() {return !this.comment.media.voting},
        voting: function() {return this.comment.media.voting},
    },
    methods: {
        add_media() {
            this.$refs.modal.show();
        },
        do_add_media() {
        },
        do_vote() {
            if (!this.choice) {
                return;
            }
            this.loading = true;
            axios.post(
                comment.url + 'voting/',
                {'choice': this.choice}
            ).then(response => {
                this.voting = response.data;
            }).catch(error => Vue.app_error_handler(error, "error")
            ).then(() => {
                this.loading = false;
            });
        }
    },
})
