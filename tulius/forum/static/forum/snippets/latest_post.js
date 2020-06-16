export default LazyComponent('forum_latest_post', {
    template: '/static/forum/snippets/latest_post.html',
    props: {
        comment: {
            type: Object,
        },
    	comment_url: {
			type: Function,
			default: function(comment) {
			    return {
                    name: 'forum_thread',
                    params: { id: comment.parent_id },
                    query: { page: comment.page },
                    hash: '#' + comment.id,
                }
			}
		},
    },
    methods: {
        forum_datetime: (v) => forum_datetime(new Date(v)),
    },
})
