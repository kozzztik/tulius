import latest_post from './latest_post.js'

export default LazyComponent('forum_room_list', {
    template: '/static/forum/snippets/room_list.html',
    props: {
    	rooms: {
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
		room_url: {
			type: Function,
			default: function(thread) {
			    return {
                    name: 'forum_room',
                    params: { id: thread.id },
                }
			}
		},
    }
})
