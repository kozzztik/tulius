import APILoadMixin from '../../app/components/api_load_mixin.js'

export default LazyComponent('forum_add_room_page', {
    mixins: [APILoadMixin,],
    template: '/static/forum/pages/add_room.html',
    data: () => ({
        loading: true,
        form: {
            room: true,
            title: '',
            body: '',
            access_type: 0,
            granted_rights: [],
        },
        access_types: [
            {value: 0, text: "доступ не задан"},
            {value: 1, text: "свободный доступ"},
            {value: 2, text: "только чтение"},
            {value: 3, text: "доступ только по списку"},
        ],
        parent_thread: {},
    }),
    computed: {
        urls() {return this.$parent.urls},
    },
    methods: {
        load_api(route) {
            this.title = '';
            this.body = '';
            this.access_type = 0;
            this.granted_rights = [];
            if (!route.params.id)
                return this.parent_thread = null;
            if (this.parent_thread.id == route.params.id)
                return;
            return axios.get(this.urls.thread_api(route.params.id)
            ).then(response => {
                this.parent_thread = response.data;
                this.breadcrumbs = this.$parent.thread_breadcrumbs(this.parent_thread);
                this.breadcrumbs.push({
                    title: "Добавить комнату",
                    url: this.$route,
                });
                this.loading = false;
            })
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
    }
})