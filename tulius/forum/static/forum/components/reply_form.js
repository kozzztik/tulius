import ckeditor from '../../ckeditor4/components/tulius_ckeditor.js'


export default LazyComponent('forum_reply_form', {
    template: '/static/forum/components/reply_form.html',
    props: ['thread', 'user'],
    data: function () {
        return {
            show_preview: false,
            preview_comment: {},
            reply_comment_id: null,
            reply_text: '',
            loading: false,
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
        getSelectionText() {
            var text = "";
            if (window.getSelection) {
                text = window.getSelection().toString();
            } else if (document.selection && document.selection.type != "Control") {
                text = document.selection.createRange().text;
            }
            return text;
        },
        fast_reply(comment) {
            this.show_preview = false;
            var text = this.getSelectionText();
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
            this.reply_comment_id = this.thread.first_comment_id;
            this.show_preview = false;
            this.reply_text = '';
        },
        do_reply() {
            this.loading = true;
            axios.post(
                '/api/forum/thread/'+ this.thread.id + '/comments_page/',
                {body: this.reply_text, reply_id: this.reply_comment_id}
            ).then(response => {
                this.$parent.cleanup_reply_form();
                this.$parent.set_comments(comments);
                this.$parent.pagination = response.data.pagination;
            }).catch(error => {
                this.$root.add_message(error, "error");
            }).then(() => {
                this.loading = false;
            });
        },
        do_preview() {
            this.loading = true;
            axios.post(
                    '/api/forum/thread/'+ this.thread.id + '/comments_page/',
                    {body: this.reply_text, reply_id: this.reply_comment_id, preview: true}
            ).then(response => {
                this.preview_comment = response.data;
                this.preview_comment.title = "Предварительный просмотр сообщения";
                this.show_preview = true;
            }).catch(error => this.$parent.add_message(error, "error"))
            .then(() => {
                this.loading = false;
            });
        },
        fast_reply(comment) {
            this.show_preview = false;
            var text = this.getSelectionText();
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
    },
    mounted() {this.reply_comment_id = this.thread.first_comment_id;},
    beforeRouteUpdate (to, from, next) {
        this.cleanup_reply_form();
        next();
    },
})
