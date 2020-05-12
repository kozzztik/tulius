import thread_actions from '../snippets/thread_actions.js'
import online_status from '../snippets/online_status.js'
import comment_component from '../snippets/comment.js'
import pagination_component from '../components/pagination.js'
import '../js/jquery.selection.js'


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
            reply_comment_id: null,
        }
    },
    methods: {
        reply_str(comment) {
            if (comment.user.sex == 1) {
                return comment.user.title + ' сказал:'
            } else if (comment.user.sex == 2) {
                return comment.user.title + ' сказала:'
            } else {
                return comment.user.title + ' сказал(а):'
            }
        },
        fast_reply(comment) {
            $("#" + comment.id).after($('#replyformroot'));
            var selection = $.selection().get();
            var text = selection.html;
            if (text != "") {
                var data = $("textarea").htmlcode();
                $("textarea").htmlcode(
                    $("textarea").htmlcode() +
                    '<div class="quote"><font size="1">' +
                    this.reply_str(comment) +
                    '</font><br/>' +
                    text + '</div>');
            }
            window.getSelection().removeAllRanges();
            this.reply_comment_id = comment.id;
        },
        cleanup_reply_form() {
            $('#replyform_placement').append($('#replyformroot')); // park form
            this.reply_comment_id = this.thread.first_comment_id;
            this.show_preview = false;
            $('#id_body')[0].value = '';
        },
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
                this.reply_comment_id = this.thread.first_comment_id;
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
            axios.post(
                '/api/forum/thread/'+ this.thread.id + '/comments_page/',
                {body: reply_text, reply_id: this.reply_comment_id}
            ).then(response => {
                this.cleanup_reply_form();
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
                    {body: reply_text, reply_id: this.reply_comment_id, preview: true}
            ).then(response => {
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
        this.cleanup_reply_form();
        this.load_api(to.params.id, to.query['page'] || 1);
        next();
    },
    updated: function () {
        this.$nextTick(function () {
            $("textarea").wysibb(this.wysibb_options);
        });
    }
})
