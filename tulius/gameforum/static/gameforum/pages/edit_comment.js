import reply_form_component from '../../forum/components/reply_form.js'
import APILoadMixin from '../../app/components/api_load_mixin.js'


export default LazyComponent('game_forum_edit_comment_page', {
    mixins: [APILoadMixin,],
    template: '/static/gameforum/pages/edit_comment.html',
       data: function () {
        return {
            loading: true,
            thread: {online_ids: [], id: null},
            comment: {},
        }
    },
    computed: {
        urls: function() {return this.$parent.urls;},
        variation: function() {return this.$parent.variation},
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