import thread_actions from '../snippets/thread_actions.js'
import online_status from '../snippets/online_status.js'
import comment_component from '../snippets/comment.js'


export default LazyComponent('forum_thread_page', {
    template: '/static/forum/pages/thread.html',
    data: function () {
        return {
            breadcrumbs: [],
            loading: true,
            thread: {},
            comments: [],
            pagination: {},
            comments_page: 1,
            user: {},
        }
    },
    methods: {
        load_api(pk) {
            this.$parent.loading_start();
            axios.get('/api/forum/thread/'+ pk).then(response => {
                const api_response = response.data;
                this.breadcrumbs = [{"url": "/forums/", "title": "Форумы"}]
                api_response.parents.forEach(
                    (item, i, arr) => this.breadcrumbs.push(
                        {"url": item.url, "title": item.title}
                    ));
                this.breadcrumbs.push(
                    {"url": api_response.url, "title": api_response.title});
                this.thread = api_response;
                this.user = this.$parent.user;
                this.$parent.loading_start();
                axios.get('/api/forum/thread/'+ pk + '/comments_page/' + this.comments_page + '/').then(response => {
                    this.comments = response.data.comments;
                    this.pagination = response.data.pagination;
                }).catch(error => this.$parent.add_message(error, "error")).then(() => {
                    this.loading = false;
                    this.$parent.loading_end(this.breadcrumbs);
                });
            }).catch(error => this.$parent.add_message(error, "error"))
            .then(() => {
                this.$parent.loading_end(this.breadcrumbs);
            });
        },
    },
    mounted() {this.load_api(this.$route.params.id)},
    beforeRouteUpdate (to, from, next) {
        this.load_api(to.params.id);
        next();
    }
})
