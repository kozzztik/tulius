import reply_form_component from '../components/reply_form.vue'
import APILoadMixin from '../../app/components/api_load_mixin.js'
import {LazyComponent} from '../../common/js/vue-common.js'
import axios from '../../common/js/axios.min.js';


export default LazyComponent('forum_edit_comment_page', {
    mixins: [APILoadMixin,],
    template: '/static/forum/pages/edit_comment.html',
       data: function () {
        return {
            loading: true,
            thread: {online_ids: [], id: null},
            comment: {},
        }
    },
    components: {
        'forum_reply_form': reply_form_component,
    },
    computed: {
        urls() {return this.$parent.urls},
    },
    methods: {
        load_api(route) {
            if (this.comment.id == route.params.id)
                return;
            return axios.get(this.urls.comment_api(route.params.id)).then(response => {
                this.comment = response.data;
                this.thread = this.comment.thread
                this.thread.online_ids = []
                this.breadcrumbs = this.$parent.thread_breadcrumbs(this.thread);
                this.breadcrumbs.push({
                    title: "Редактировать сообщение",
                    url: this.$route,
                });
                this.loading = false;
            });
        },
    },
})