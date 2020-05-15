import thread_actions from '../snippets/thread_actions.js'
import online_status from '../snippets/online_status.js'
import comment_component from '../snippets/comment.js'
import pagination_component from '../components/pagination.js'
import '../js/jquery.selection.js'
import ckeditor from '../../ckeditor4/components/tulius_ckeditor.js'


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
            show_preview: false,
            preview_comment: {},
            reply_comment_id: null,
            reply_text: '',
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
            this.show_preview = false;
            $("#" + comment.id).after($('#replyformroot'));
            var selection = $.selection().get();
            var text = selection.html;
            if (text != "") {
                this.reply_text = this.reply_text +
                    '<blockquote><font size="1">' +
                    this.reply_str(comment) +
                    '</font><br/>' +
                    text + '</blockquote><p></p>';
            }
            window.getSelection().removeAllRanges();
            this.reply_comment_id = comment.id;
        },
        cleanup_reply_form() {
            $('#replyform_placement').append($('#replyformroot')); // park form
            this.reply_comment_id = this.thread.first_comment_id;
            this.show_preview = false;
            this.reply_text = '';
        },
        update_comments() {
            this.loading = true;
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
            }).catch(error => this.$parent.add_message(error, "error"))
            .then(() => {
                this.$parent.loading_end(this.breadcrumbs);
            });
        },
        do_reply() {
            this.loading = true;
            this.$parent.loading_start();
            axios.post(
                '/api/forum/thread/'+ this.thread.id + '/comments_page/',
                {body: this.reply_text, reply_id: this.reply_comment_id}
            ).then(response => {
                this.cleanup_reply_form();
                this.comments = response.data.comments;
                this.pagination = response.data.pagination;
            }).catch(error => this.$parent.add_message(error, "error"))
            .then(() => {
                this.loading = false;
                this.$parent.loading_end(this.breadcrumbs);
            });
        },
        do_preview() {
            axios.post(
                    '/api/forum/thread/'+ this.thread.id + '/comments_page/',
                    {body: this.reply_text, reply_id: this.reply_comment_id, preview: true}
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
})
