import thread_actions from '../snippets/thread_actions.js'
import online_status from '../snippets/online_status.js'
import comment_component from '../snippets/comment.js'
import pagination_component from '../components/pagination.js'


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
            wysibb_options: null,
            show_preview: false,
            preview_comment: {},
        }
    },
    methods: {
        update_comments() {
            this.$parent.loading_start();
            axios.get('/api/forum/thread/'+ this.thread.id + '/comments_page/' + this.comments_page + '/').then(response => {
                this.comments = response.data.comments;
                this.pagination = response.data.pagination;
            }).catch(error => this.$parent.add_message(error, "error")).then(() => {
                this.loading = false;
                this.$parent.loading_end(this.breadcrumbs);
            });
        },
        load_api(pk, page) {
            this.$parent.loading_start();
            this.comments_page = page;
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
                this.update_comments()
                if (this.wysibb_options === null) {
                    this.$parent.loading_start();
                    axios.get('/wysibb/options/').then(response => {
                        this.wysibb_options = response.data;
                        this.wysibb_options.allButtons.myfile.modal.onSubmit = wysibb_file_load;
                    }).catch(error => this.$parent.add_message(error, "error")).then(() => {
                        this.loading = false;
                        this.$parent.loading_end(this.breadcrumbs);
                    });
                }
            }).catch(error => this.$parent.add_message(error, "error"))
            .then(() => {
                this.$parent.loading_end(this.breadcrumbs);
            });
        },
        do_reply() {
            $("#replyform textarea").sync();
            var reply_text = $('#id_body')[0].value;
            $("#replyform textarea").destroy();
            this.$parent.loading_start();
            axios.post('/api/forum/thread/'+ this.thread.id + '/comments_page/', {body: reply_text}).then(response => {
                $('#id_body')[0].value = '';
                this.show_preview = false;
                this.comments = response.data.comments;
                this.pagination = response.data.pagination;
            }).catch(error => this.$parent.add_message(error, "error"))
            .then(() => {
                this.$parent.loading_end(this.breadcrumbs);
            });
        },
        do_preview() {
            $("#replyform textarea").sync();
            var reply_text = $('#id_body')[0].value;
            axios.post(
                    '/api/forum/thread/'+ this.thread.id + '/comments_page/',
                    {body: reply_text, preview: true}).then(response => {
                this.preview_comment = response.data;
                this.preview_comment.title = "Предварительный просмотр сообщения";
                this.show_preview = true;
            }).catch(error => this.$parent.add_message(error, "error"))
            .then(() => {
            });
        }
    },
    mounted() {this.load_api(this.$route.params.id, this.$route.query['page'] || 1)},
    beforeRouteUpdate (to, from, next) {
        this.load_api(to.params.id, to.query['page'] || 1);
        next();
    },
    updated: function () {
        this.$nextTick(function () {
            $("textarea").wysibb(this.wysibb_options);
        });
    }
})
