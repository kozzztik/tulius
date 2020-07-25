import avatar from '../components/avatar.js'
import role_selector from '../components/role_selector.js'
import thread_actions from '../components/thread_actions.js'
import online_status from '../components/online_status.js'
import comments_component from '../../forum/components/comments.js'
import reply_form_component from '../../forum/components/reply_form.js'
import APILoadMixin from '../../app/components/api_load_mixin.js'
import media_illustrations from '../components/media/illustrations.js'


export default LazyComponent('gameforum_thread_page', {
    mixins: [APILoadMixin,],
    template: '/static/gameforum/pages/thread.html',
    data: function () {
        return {
            loading: true,
            thread: {online_ids: [], id: null},
            comments_page: 1,
        }
    },
    computed: {
        urls: function() {return this.$parent.urls;},
        variation: function() {return this.$parent.variation},
    },
    methods: {
        load_api(route) {
            this.comments_page = route.query['page'] || 1;
            if (this.thread.id == route.params.id)
                return;
            return axios.get(this.urls.thread_api(route.params.id)).then(response => {
                response.data.online_ids = this.thread.online_ids;
                this.thread = response.data;
                this.breadcrumbs = this.$parent.thread_breadcrumbs(this.thread);
                this.loading = false;
            });
        },
        mark_all_not_readed() {
            axios.delete(this.thread.url + 'read_mark/').then(response => {
                this.thread.last_read_id = response.data.last_read_id;
                this.thread.not_read_comment = response.data.not_read_comment;
            });
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
    },
})
