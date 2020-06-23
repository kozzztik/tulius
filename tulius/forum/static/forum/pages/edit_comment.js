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
            this.$root.loading_start();
            axios.get('/api/forum/comment/'+ pk + '/').then(response => {
                this.comment = response.data;
                this.thread = this.comment.thread
                this.thread.online_ids = []
                this.breadcrumbs = [{"url": "/forums/", "title": "Форумы"}]
                for (var item of this.thread.parents)
                    this.breadcrumbs.push({
                        title: item.title,
                        url: {
                            name: 'forum_room',
                            params: {id: item.id},
                        },
                    });
                this.breadcrumbs.push({
                    title: this.thread.title,
                    url: {
                        name: 'forum_thread',
                        params: {id: this.thread.id},
                    },
                });
                this.breadcrumbs.push({
                    title: "Редактировать сообщение",
                    url: this.$route,
                });
                this.loading = false;
            }).catch(error => this.$root.add_message(error, "error"))
            .then(() => {
                this.$root.loading_end(this.breadcrumbs);
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