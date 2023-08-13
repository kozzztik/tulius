import thread_actions from '../components/thread_actions.js'
import online_status from '../components/online_status.js'
import reply_form from '../components/reply_form.vue'
import ThreadPage from '../../forum/pages/thread.vue'


export default {
    mixins: [ThreadPage,],
    components: {
        'game_forum_thread_actions': thread_actions,
        'game_forum_online_status': online_status,
        'forum_reply_form': reply_form,
    },
    computed: {
        variation: function() {return this.$parent.variation},
    },
}
