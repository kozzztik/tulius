import avatar from '../components/avatar.js'
import role_selector from '../components/role_selector.js'
import thread_actions from '../components/thread_actions.js'
import online_status from '../components/online_status.js'
import media_illustrations from '../components/media/illustrations.js'
import ThreadPage from '../../forum/pages/thread.vue'


export default {
    mixins: [ThreadPage,],
    components: {
        'game_forum_thread_actions': thread_actions,
        'game_forum_comment_avatar': avatar,
        'media_illustrations': media_illustrations,
        'game_forum_role_selector': role_selector,
        'game_forum_online_status': online_status,
    },
    computed: {
        variation: function() {return this.$parent.variation},
    },
    methods: {
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
    },
}
