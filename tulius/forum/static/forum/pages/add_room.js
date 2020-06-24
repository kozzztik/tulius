export default LazyComponent('forum_add_room_page', {
    template: '/static/forum/pages/edit_comment.html',
       data: function () {
        return {
            breadcrumbs: [],
            loading: true,
            form: {
                room: true,
                title: '',
                body: '',
                access_type: 0,
                granted_rights: [],
            }
            parent_thread: null,
        }
    },
    methods: {
        load_api(pk) {
            this.title = '';
            this.body = '';
            this.access_type = 0;
            this.granted_rights = [];
            if (this.parent_thread.id == pk)
                return;
            if (!pk) {
                this.parent_thread = null;
                return
            }
            this.$parent.loading_start();
            axios.get('/api/forum/thread/' + pk + '/').then(response => {
                this.parent_thread = response.data;
                this.breadcrumbs = this.$parent.thread_breadcrumbs(this.parent_thread);
                this.breadcrumbs.push({
                    title: "Добавить комнату",
                    url: this.$route,
                });
                this.loading = false;
            }).catch(error => this.$root.add_message(error, "error"))
            .then(() => {
                this.$parent.loading_end(this.breadcrumbs);
            });
        },
        on_submit() {
            var submit_url = '/api/forum/';
            if (this.parent_thread)
                submit_url = this.parent_thread.url;
            axios.put(submit_url, this.form).then(response => {

            }).catch(error => this.$root.add_message(error, "error"))
            .then(() => {
                this.$root.loading_end(this.breadcrumbs);
            });
        }
    },
    mounted() {
        this.load_api(this.$route.params.id)
    },
    beforeRouteUpdate (to, from, next) {
        this.load_api(to.params.id);
        next();
    },
})