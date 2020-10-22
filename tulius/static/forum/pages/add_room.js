import thread_access from '../components/thread_access.js'
import APILoadMixin from '../../app/components/api_load_mixin.js'


export default LazyComponent('forum_add_room_page', {
    mixins: [APILoadMixin,],
    props: {
        user_search: {
			type: Function,
			default: null,
		}
	},
    template: '/static/forum/pages/add_room.html',
    data: () => ({
        form: {
            room: true,
            title: '',
            body: '',
            default_rights: null,
            granted_rights: [],
        },
        thread_default_rights: [
            {value: null, text: "доступ не задан"},
            {value: 1+2, text: "свободный доступ"},
            {value: 1, text: "только чтение"},
            {value: 1+16, text: "только чтение(только в корне)"},
            {value: 0, text: "доступ только по списку"},
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
            this.default_rights = null;
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