import {LazyComponent} from '../../common/js/vue-common.js'
import axios from '../../common/js/axios.min.js';


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
            if (thread) {
                this.parents = thread.parents;
                this.rooms = thread.rooms || [];
                this.threads = thread.threads || [];
            } else {
                this.parents = [];
                this.rooms = [];
                this.threads = [];
            }
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
            if (this.on_choose)
                this.on_choose(this.thread);
        },
        select_root() {
            this.$root.loading_start();
            axios.get(this.urls.root_api).then(response => {
                this.set_thread(null);
                this.rooms = response.data.groups;
                this.$parent.loading_end();
            }).catch(error => this.$root.loading_end());
        }
    },
    watch: {
		value(val) {
            if (val && !val.parents)
                this.select_thread(val)
            else
                this.set_thread(val);
        },
    },
});