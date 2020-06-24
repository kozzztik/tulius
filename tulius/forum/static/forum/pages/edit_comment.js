import reply_form_component from '../components/reply_form.js'


export default LazyComponent('forum_edit_comment_page', {
    template: '/static/forum/pages/edit_comment.html',
       data: function () {
        return {
            breadcrumbs: [],
            loading: true,
            thread: {online_ids: [], id: null},
            comment: {},
        }
    },
    computed: {
        user: function() {return this.$root.user;}
    },
    methods: {
        load_api(pk) {
            if (this.comment.id == pk)
                return;
            this.$parent.loading_start();
            axios.get('/api/forum/comment/' + pk + '/').then(response => {
                this.comment = response.data;
                this.thread = this.comment.thread
                this.thread.online_ids = []
                this.breadcrumbs = this.$parent.thread_breadcrumbs(this.thread);
                this.breadcrumbs.push({
                    title: "Редактировать сообщение",
                    url: this.$route,
                });
                this.loading = false;
            }).catch(error => this.$root.add_message(error, "error"))
            .then(() => {
                this.$parent.loading_end(this.breadcrumbs);
            });
        },
    },
    mounted() {
        this.load_api(this.$route.params.id)
    },
    beforeRouteUpdate (to, from, next) {
        this.load_api(to.params.id);
        next();
    },
})