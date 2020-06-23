import reply_form_component from '../../forum/components/reply_form.js'


export default LazyComponent('game_forum_edit_comment_page', {
    template: '/static/gameforum/pages/edit_comment.html',
       data: function () {
        return {
            breadcrumbs: [],
            loading: true,
            thread: {online_ids: [], id: null},
            comment: {},
        }
    },
    computed: {
        user: function() {return this.$root.user;},
        variation: function() {return this.$parent.variation},
    },
    methods: {
        load_api(pk) {
            if (this.comment.id == pk)
                return;
            this.$root.loading_start();
            axios.get(this.variation.url + 'comment/'+ pk + '/').then(response => {
                this.comment = response.data;
                this.thread = this.comment.thread
                this.thread.online_ids = []
                this.breadcrumbs = []
                for (var item of this.thread.parents)
                    this.breadcrumbs.push({
                        title: item.title,
                        url: {
                            name: 'game_room',
                            params: {id: item.id, variation_id: this.variation.id},
                        },
                    });
                this.breadcrumbs.push({
                    title: this.thread.title,
                    url: {
                        name: 'game_thread',
                        params: {id: this.thread.id, variation_id: this.variation.id},
                    },
                });
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
        comment_url(comment) {
            return {
                name: 'game_thread',
                params: {
                    id: this.thread.id,
                    variation_id: this.variation.id
                },
                query: { page: comment.page },
                hash: '#' + comment.id,
            }
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