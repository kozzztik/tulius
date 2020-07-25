import thread_actions from '../snippets/thread_actions.js'
import online_status from '../snippets/online_status.js'
import comments_component from '../components/comments.js'
import reply_form_component from '../components/reply_form.js'
import APILoadMixin from '../../app/components/api_load_mixin.js'


export default LazyComponent('forum_thread_page', {
    mixins: [APILoadMixin,],
    template: '/static/forum/pages/thread.html',
    data: function () {
        return {
            loading: true,
            thread: {online_ids: [], id: null},
            comments_page: 1,
        }
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
        mark_all_not_readed() {
            axios.delete(this.thread.url + 'read_mark/').then(response => {
                this.thread.last_read_id = response.data.last_read_id;
                this.thread.not_read_comment = response.data.not_read_comment;
            });
        },
    },
})
