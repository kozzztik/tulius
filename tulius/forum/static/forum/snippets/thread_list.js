import latest_post from './latest_post.js'

export default LazyComponent('forum_thread_list', {
    template: '/static/forum/snippets/thread_list.html',
    props: {
    	threads: {
    	    type: Array,
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
		thread_url: {
			type: Function,
			default: function(thread, page) {
			    return {
                    name: 'forum_thread',
                    params: { id: thread.id },
                    query: { page: page },
                }
			}
		},
    }
})
