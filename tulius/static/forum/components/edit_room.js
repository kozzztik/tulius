export default LazyComponent('forum_edit_room', {
    props: {
        page: {type: Object},
        thread: {type: Object},
        extra_fields: {
			type: Array,
			default: () => [],
		}
	},
    template: '/static/forum/components/edit_room.html',
    data: () => ({
        fields: ['title', 'body'],
        form: {},
    }),
    methods: {
        show() {
            this.form = {}
            for (var key of [...this.fields, ...this.extra_fields])
                this.form[key] = this.thread[key];
            this.$refs.modal.show();
        },
        on_submit() {
            axios.post(this.thread.url, this.form).then(response => {
                this.page.thread = response.data;
                this.page.breadcrumbs = this.page.$parent.thread_breadcrumbs(this.page.thread);
                this.page.$parent.loading_end(this.page.breadcrumbs);
                this.$refs.modal.hide();
            });
        }
    }
})