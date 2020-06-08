import ckeditor from '../../ckeditor4/components/tulius_ckeditor.js'


export default LazyComponent('forum_reply_form', {
    template: '/static/forum/components/reply_form.html',
    props: ['thread'],
    data: function () {
        return {
            show_preview: false,
            preview_comment: {},
            reply_comment_id: null,
            reply_text: '',
            loading: false,
            show_form: true,
            form_el: null,
        }
    },
    computed: {
        user: function() {return this.$root.user;}
    },
    methods: {
        hide() {this.show_form = false;},
        show() {
            this.show_form = true;
            this.reply_text = this.reply_text;  // on chrome resurrects editor
        },
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
        cleanup_reply_form() {
            if (this.form_el) {
                this.form_el.parentNode.removeChild(this.form_el);
                this.$refs.reply_form_parking.appendChild(this.form_el);
                this.form_el = null;
            }
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
                this.cleanup_reply_form();
                this.$parent.$refs.comments.update_to_comments(response.data);
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
        fast_reply(comment, component) {
            this.show_preview = false;
            var text = this.getSelectionText();
            if (text == "")
                text = comment.body;
            this.reply_text = this.reply_text +
                '<blockquote><font size="1">' +
                this.reply_str(comment) +
                '</font><br/>' +
                text + '</blockquote><p></p>';
            window.getSelection().removeAllRanges();
            this.reply_comment_id = comment.id;
            if (component) {
                if (!this.form_el)
                    this.form_el = this.$refs.reply_form;
                this.form_el.parentNode.removeChild(this.form_el);
                component.$el.parentNode.appendChild(this.form_el);
            }
        },
    },
    mounted() {this.reply_comment_id = this.thread.first_comment_id;},
    beforeRouteUpdate (to, from, next) {
        this.cleanup_reply_form();
        next();
    },
})
