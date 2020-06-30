export default LazyComponent('forum_thread_access', {
    template: '/static/forum/components/thread_access.html',
    props: ['thread'],
    props: {
        thread: {
            type: Object,
        },
        user_search: {
			type: Function,
	    },
	},
    data: function () {
        return {
            rights: [],
            add_form: {
                user: null,
                access_level: 3,
            },
            add_loading: false,
            thread_loading: false,
            access_levels: [
                {value: 1, text: "чтение"},
                {value: 3, text: "чтение и запись"},
                {value: 7, text: "чтение, запись и модерирование"},
                {value: 2, text: "только запись"},
                {value: 5, text: "чтение и модерирование"},
            ],
            access_types: [
                {value: 0, text: "доступ не задан"},
                {value: 1, text: "свободный доступ"},
                {value: 2, text: "только чтение"},
                {value: 3, text: "доступ только по списку"},
            ],
            user_options: [],
        }
    },
    computed: {
        user() {return this.$root.user},
        urls() {return this.$parent.urls},
    },
    methods: {
        show_dialog() {
            if (!this.thread.id) {
                this.rights = this.thread.granted_rights;
                this.$refs.modal.show();
            } else
                this.load_api();
        },
        do_search(query) {
            var res = (this.user_search||this.default_user_search)(
                query, this.rights);
            if (res && (typeof res.then === 'function')) {
                res.then(response => this.user_options = response);
                return res;
            }
            this.user_options = res || this.user_options;
        },
        default_user_search(query, rights) {
            if (query.length < 3)
                return
            var base_url = this.thread.url ? this.thread.url : this.urls.root_api;
            return axios.options(
                base_url + 'granted_rights/', {params: {query: query}}
            ).then(response => {
                var result = [];
                for (var user of response.data.users) {
                    var found = false;
                    for (var right of rights)
                        if (right.user.id == user.id) {
                            found = true;
                            break;
                        }
                    if (!found)
                        result.push(user);
                }
                return result;
            }).catch(error => this.$root.add_message(error, "error"))
        },
        load_api() {
            this.$root.loading_start();
            axios.get(this.thread.url + 'granted_rights/').then(response => {
                this.rights = []
                for (var right of response.data.granted_rights)
                    this._add_right(right);
                this.$refs.modal.show();
            }).catch(error => this.$root.add_message(error, "error"))
            .then(() => {
                this.$root.loading_end(null);
            });
        },
        change_right(right) {
            if (!right.url)
                return
            right.loading = true;
            axios.post(
                right.url, {'access_level': right.access_level}
            ).then(response => {
                right.loading = false;
            }).catch(error => this.$root.add_message(error, "error"))
            .then(() => {
                right.loading = false;
            });
        },
        _add_right(right) {
            right.loading = false;
            this.rights.push(right);
        },
        add_right() {
            if (!this.add_form.user)
                return;
            if (!this.thread.id) {
                this._add_right(JSON.parse(JSON.stringify(this.add_form)));
                this.add_form.user = null;
                return;
            }
            this.add_loading = true;
            axios.post(
                this.thread.url + 'granted_rights/', this.add_form
            ).then(response => {
                this._add_right(response.data);
                this.add_form.user = null;
            }).catch(error => this.$root.add_message(error, "error"))
            .then(() => {
                this.add_loading = false;
            });
        },
        delete_right(right) {
            if (!right.url) {
                this.rights = this.rights.filter(item => (item.user.id != right.user.id));
                return
            }
            right.loading = true;
            axios.delete(right.url).then(response => {
                this.rights = this.rights.filter(item => (item.url != right.url));
            }).catch(error => this.$root.add_message(error, "error"));
        },
        change_thread_type() {
            if (!this.thread.id)
                return;
            this.thread_loading = true;
            axios.put(
                this.thread.url + 'granted_rights/',
                {'access_type': this.thread.access_type}
            ).then(response => {}).catch(error => this.$root.add_message(error, "error"))
            .then(() => {
                this.thread_loading = false;
            });
        }
    },
})
