import ckeditor from '../../ckeditor4/components/tulius_ckeditor.js'
import voting from './voting.js'
import images from './media/images.js'
import html_editor from './media/html.js'


export default LazyComponent('forum_reply_form', {
    template: '/static/forum/components/reply_form.html',
    props: {
    	thread: {
    	    type: Object,
    	},
    	comment: {
    	    type: Object,
    	    default: null,
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
            loading: false,
            show_form: true,
            form_el: null,
            media_actions: [],
            form: this.comment || {
                title: 'Re: ' + this.thread.title,
                body: '',
                reply_id: this.thread.first_comment_id,
                media: {},
                url: this.thread.url + 'comments_page/',
            }
        }
    },
    computed: {
        urls: function() {return this.$parent.urls;},
        user: function() {return this.$root.user;},
    },
    methods: {
        hide() {this.show_form = false;},
        show() {this.show_form = true;},
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
            this.form.title = 'Re: ' + this.thread.title;
            this.form.body = '';
            this.form.media = {};
            document.getElementById("reply_form").classList.remove("reply_form_max");
            document.getElementById("content-center").classList.remove("reply_form_only");
        },
        do_reply() {
            if (this.form.body == '')
                return;
            this.loading = true;
            axios.post(this.form.url, this.form).then(response => {
                if (this.comment)
                    this.$router.push(this.urls.comment(this.comment))
                else {
                    this.cleanup_reply_form();
                    this.$parent.$refs.comments.update_to_comments(response.data);
                }
            }).catch(error => {this.$root.add_message(error, "error");
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
            axios.post(this.form.url, data).then(response => {
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
    beforeRouteUpdate (to, from, next) {
        if (!this.comment)
            this.cleanup_reply_form();
        next();
    },
})
