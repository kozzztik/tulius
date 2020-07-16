import thread_access from '../components/thread_access.js'
import APILoadMixin from '../../app/components/api_load_mixin.js'

function cleanup_form(target, source) {
    for (const [key, value]  of Object.entries(source))
        if (typeof value === 'function')
            target[key] = value()
        else
            target[key] = value;
}

export default LazyComponent('forum_edit_thread_page', {
    mixins: [APILoadMixin,],
    props: {
        extra_fields: {
			type: Object,
			default: () => ({}),
		},
        user_search: {
			type: Function,
			default: null,
		},
	},
    template: '/static/forum/pages/edit_thread.html',
    data() {
        var data = {
            fields: {
                room: false,
                title: '',
                body: '',
                important: false,
                access_type: 0,
                granted_rights: () => [],
                media: () => ({}),
                closed: false,
            },
            form: {},
            access_types: [
                {value: 0, text: "доступ не задан"},
                {value: 1, text: "свободный доступ"},
                {value: 2, text: "только чтение"},
                {value: 3, text: "доступ только по списку"},
            ],
            parent_thread: {},
            thread: {},
            rights: {},
            media_actions: [],
            preview_comment: {},
            show_preview: false,
        }
        for (const [key, value] of Object.entries(this.extra_fields))
            data.fields[key] = value;
        cleanup_form(data.form, data.fields)
        return data
    },
    computed: {
        urls() {return this.$parent.urls},
    },
    methods: {
        load_api(route) {
            if (route.params.parent_id) {
                cleanup_form(this.form, this.fields);
                return axios.get(this.urls.thread_api(route.params.parent_id)
                    ).then(response => {
                        this.parent_thread = response.data;
                        this.parent_thread.online_ids = [];
                        this.rights = this.parent_thread.rights;
                        this.breadcrumbs = this.$parent.thread_breadcrumbs(this.parent_thread);
                        this.breadcrumbs.push({
                            title: "Добавить тему",
                            url: this.$route,
                        });
                    })
            }
            return axios.get(this.urls.thread_api(route.params.id)
                ).then(response => {
                    this.thread = response.data;
                    this.thread.online_ids = [];
                    this.rights = this.thread.rights;
                    this.breadcrumbs = this.$parent.thread_breadcrumbs(this.thread);
                    this.breadcrumbs.push({
                        title: "Редактировать",
                        url: this.$route,
                    });
                    cleanup_form(this.form, this.thread);
                })
        },
        on_submit() {
            this.$root.loading_start();
            axios({
                method: this.thread.url ? 'post' : 'put',
                url: this.thread.url || this.parent_thread.url,
                data: this.form,
            }).then(response => {
                this.$router.push(this.urls.thread(response.data.id));
                this.$root.loading_end();
            }).catch(() => {
                this.$root.loading_end();
            });
        },
        do_preview() {
            if (this.form.body == '')
                return;
            this.$root.loading_start();
            const data = JSON.parse(JSON.stringify(this.form))
            data.preview = true;
            axios({
                method: this.thread.url ? 'post' : 'put',
                url: this.thread.url || this.parent_thread.url,
                data: data
            }).then(response => {
                this.preview_comment = response.data;
                this.preview_comment.thread = this.thread;
                this.preview_comment.create_time = Date();
                this.show_preview = true;
                this.$root.loading_end();
            }).catch(() => {
                this.$root.loading_end();
            });
        },
    }
})