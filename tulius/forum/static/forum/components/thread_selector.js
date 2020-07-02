export default LazyComponent('thread_selector', {
    template: '/static/forum/components/thread_selector.html',
    props: {
        value: {
            type: Object,
        },
        on_choose: {
			type: Function,
			default: null,
	    },
	    room_only: {
			type: Boolean,
			default: false,
	    },
	    show_root: {
			type: Boolean,
			default: false,
	    },
	},
	data: () => ({
	    parents: [],
	    thread: null,
	    rooms: [],
	    threads: [],
	}),
	computed: {
        urls() {return this.$parent.urls},
    },
    methods: {
        set_thread(thread) {
            this.thread = thread;
            this.parents = thread.parents;
            this.rooms = thread.rooms || [];
            this.threads = thread.threads || [];
        },
        show() {
            this.set_thread(this.value);
            this.$refs.modal.show();
        },
        select_thread(thread) {
            this.$root.loading_start();
            axios.get(thread.url).then(response => {
                this.set_thread(response.data);
                this.$parent.loading_end();
            }).catch(error => this.$root.loading_end());
        },
        on_ok() {
            this.$emit('input', this.thread);
        },
        select_root() {
            this.$root.loading_start();
            axios.get(this.urls.root_api).then(response => {
                this.thread = null;
                this.parents = [];
                this.threads = []
                this.rooms = response.data.groups;
                this.$parent.loading_end();
            }).catch(error => this.$root.loading_end());
        }
    },
});