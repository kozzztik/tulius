import latest_post from './latest_post.js'

export default LazyComponent('forum_thread_list', {
    template: '/static/forum/snippets/thread_list.html',
    props: ['threads'],
    computed: {
    	urls() {return this.$parent.urls}
    },
    methods: {
        to_comment(pk) {
            this.$parent.loading_start();
            axios.get(this.urls.comment_api(pk)).then(response => {
                this.$parent.loading_end()
                this.$router.push(this.urls.comment(response.data));
            })
        }
    },
})
