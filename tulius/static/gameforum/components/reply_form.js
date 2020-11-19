import reply_form_component from '../../forum/components/reply_form.vue'
import comment from '../../forum/snippets/comment.js'
import role_selector from './role_selector.js'
import avatar from './avatar.js'
import media_illustrations from './media/illustrations.js'


export default {
    props: {
    	thread: {type: Object},
    	comment: {type: Object, default: null,},
    	editor: {type: Boolean, default: false,}
    },
    components: {
        'forum_reply_form': reply_form_component,
        'game_forum_role_selector': role_selector,
        'game_forum_comment_avatar': avatar,
        'media_illustrations': media_illustrations,
        'forum_comment': comment,
    },
    computed: {
        variation: function() {return this.$parent.variation},
        urls: function() {return this.$parent.urls;},
    },
    methods: {
        hide() {this.$refs.reply_form.hide()},
        show() {this.$refs.reply_form.show()},
        cleanup_reply_form() {this.$refs.reply_form.cleanup_reply_form()},
        fast_reply(comment, component) {
            this.$refs.reply_form.fast_reply(comment, component)
        },
        reply_str(comment) {
            if (comment.user.sex == 1) {
                return comment.user.title + ' сказал:'
            } else if (comment.user.sex == 2) {
                return comment.user.title + ' сказала:'
            } else if (comment.user.sex == 3) {
                return comment.user.title + ' сказало:'
            } else if (comment.user.sex == 4) {
                return comment.user.title + ' сказали:'
            }
            return comment.user.title + ' сказал(а):';
		},
    }
}