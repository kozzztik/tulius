export default LazyComponent('forum_latest_post', {
    template: '/static/forum/snippets/latest_post.html',
    props: ['comment'],
    computed: {
        urls() {return this.$parent.urls},
    },
    methods: {
        forum_datetime: (v) => forum_datetime(new Date(v)),
    },
})
