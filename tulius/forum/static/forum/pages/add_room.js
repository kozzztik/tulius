import thread_access from '../components/thread_access.js'
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
            if (!route.params.id) {
                this.parent_thread = {};
                this.$parent.loading_end([{
                    title: "Добавить комнату",
                    url: this.$route,
                }]);
                return
             }
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
            axios.put(
                this.parent_thread.url || this.urls.root_api, this.form
            ).then(response => {
                this.$router.push(this.urls.room(response.data.id));
            }).catch().then(() => {
                this.$root.loading_end(this.breadcrumbs);
            });
        }
    }
})