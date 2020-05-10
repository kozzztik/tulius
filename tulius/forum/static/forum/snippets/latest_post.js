export default LazyComponent('forum_latest_post', {
    template: '/static/forum/snippets/latest_post.html',
    props: ['comment'],
    methods: {
        forum_datetime(v) {
            return forum_datetime(new Date(v));
        }
    },
})
