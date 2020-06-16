import ckeditor from '../../ckeditor4/components/tulius_ckeditor.js'


export default LazyComponent('forum_reply_form', {
    template: '/static/forum/components/reply_form.html',
    props: {
    	thread: {
    	    type: Object,
    	},
    	extended_form_url: {
			type: Function,
			default: function(reply_comment_id) {
			    return '/forums/add_comment/' + reply_comment_id + '/';
			}
		},
        reply_str: {
			type: Function,
			default: function(comment) {
                if (comment.user.sex == 1) {
                    return comment.user.title + ' сказал:'
                } else if (comment.user.sex == 2) {
                    return comment.user.title + ' сказала:'
                }
                return comment.user.title + ' сказал(а):';
            }
		},
    },
    data: function () {
        return {
            show_preview: false,
            preview_comment: {},
            reply_comment_id: null,
            reply_text: '',
            loading: false,
            show_form: true,
            form_el: null,
            form: {
                body: '',
                reply_id: null,
            }
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
            this.form.body = '';
        },
        do_reply() {
            if (this.form.body == '')
                return;
            this.loading = true;
            axios.post(
                this.thread.url + 'comments_page/', this.form
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
            if (this.form.body == '')
                return;
            this.loading = true;
            const data = JSON.parse(JSON.stringify(this.form))
            data.preview = true;
            axios.post(
                this.thread.url + 'comments_page/', data
            ).then(response => {
                this.preview_comment = response.data;
                this.preview_comment.title = "Предварительный просмотр сообщения";
                this.show_preview = true;
            }).catch(error => this.$root.add_message(error, "error"))
            .then(() => {
                this.loading = false;
            });
        },
        fast_reply(comment, component) {
            this.show_preview = false;
            var text = this.getSelectionText();
            if (text == "")
                text = comment.body;
            this.form.body = this.form.body +
                '<blockquote><font size="1">' +
                this.reply_str(comment) +
                '</font><br/>' +
                text + '</blockquote><p></p>';
            window.getSelection().removeAllRanges();
            this.form.reply_id = comment.id;
            if (component) {
                if (!this.form_el)
                    this.form_el = this.$refs.reply_form;
                this.form_el.parentNode.removeChild(this.form_el);
                component.$el.parentNode.appendChild(this.form_el);
            }
        },
    },
    mounted() {
        this.form.reply_id = this.thread.first_comment_id;
    },
    beforeRouteUpdate (to, from, next) {
        this.cleanup_reply_form();
        next();
    },
})
