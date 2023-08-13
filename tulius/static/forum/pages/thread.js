import thread_actions from '../snippets/thread_actions.js'
import online_status from '../snippets/online_status.js'
import comments_component from '../components/comments.js'
import reply_form_component from '../components/reply_form.vue'
import APILoadMixin from '../../app/components/api_load_mixin.js'
import axios from '../../common/js/axios.min.js';


export default {
    mixins: [APILoadMixin,],
    data: function () {
        return {
            loading: true,
            thread: {online_ids: [], id: null},
            comments_page: 1,
        }
    },
    components: {
        'forum_thread_actions': thread_actions,
        'forum_thread_comments': comments_component,
        'forum_reply_form': reply_form_component,
        'forum_online_status': online_status,
    },
    computed: {
        urls() {return this.$parent.urls},
    },
    methods: {
        load_api(route) {
            this.comments_page = route.query['page'] || 1;
            if (this.thread.id == route.params.id)
                return;
            return axios.get(this.urls.thread_api(route.params.id)
            ).then(response => {
                response.data.online_ids = this.thread.online_ids;
                this.thread = response.data;
                this.breadcrumbs = this.$parent.thread_breadcrumbs(this.thread);
                this.loading = false;
            })
        },
    },
}
