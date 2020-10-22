export default LazyComponent('move_thread', {
    template: '/static/forum/components/move_thread.html',
    props: {
        thread: {
            type: Object,
        },
	    show_root: {
			type: Boolean,
			default: false,
	    },
	},
	data: () => ({
	    parent: null,
	}),
	computed: {
        urls() {return this.$parent.urls},
    },
    methods: {
        show() {
            this.parent = null;
            if (this.thread.parents.length > 0)
                this.parent = this.thread.parents[
                    this.thread.parents.length - 1];
            this.$refs.selector.show();
        },
        on_ok(parent) {
            if (!parent)
                return this.$bvModal.msgBoxOk(
                    'Нельзя перемещать в корень форума', {centered: true});
            for (var thread of parent.parents)
                if ((thread.id == this.thread.id)||(parent.id ==  this.thread.id))
                    return this.$bvModal.msgBoxOk(
                        'Нельзя переместить комнату внутрь себя', {
                            centered: true,
                        });
            var l = this.thread.parents.length;
            if ((l > 0) && (this.thread.parents[l- 1].id == parent.id))
                return
            this.$refs.modal.show();
        },
        on_confirm() {
            this.$root.loading_start();
            axios.put(
                this.urls.thread_move_api(this.thread.id),
                {'parent_id': this.parent.id}
            ).then(response => {
                this.$root.loading_end()
                window.location.reload(false);
            }).catch(error => this.$root.loading_end());
        }
    },
});