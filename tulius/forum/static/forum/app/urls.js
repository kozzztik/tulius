export default {
    room: room_id => ({name: 'forum_room', params: {id: room_id},}),
    add_room: room_id => room_id ? {name: 'forum_add_room', params: {id: room_id}
        } : {name: 'forum_add_root_room'},
    thread: (thread_id, page) => ({
        name: 'forum_thread',
        params: {id: thread_id},
        query: { page: page },
    }),
    comment: comment => ({
        name: 'forum_thread',
        params: { id: comment.thread.id, },
        query: { page: comment.page },
        hash: '#' + comment.id,
    }),
    add_thread: thread_id => ({
        name: 'forum_add_thread',
        params: {parent_id: thread_id},
    }),
    edit_thread: thread_id => ({
        name: 'forum_edit_thread',
        params: {id: thread_id},
    }),
	edit_comment: comment_id => ({
        name: 'forum_edit_comment',
        params: { id: comment_id },
	}),
	thread_fix: thread_id => ({
        name: 'fix_counters',
        params: { id: thread_id },
    }),
    likes_api: '/api/forum/likes/',
    thread_api: pk => `/api/forum/thread/${pk}/`,
    thread_move_api: pk => `/api/forum/thread/${pk}/move/`,
    thread_fix_api: pk => `/api/forum/thread/${pk}/fix/`,
    forum_fix_api: pk => `/api/forum/fix/`,
    comment_api: pk => `/api/forum/comment/${pk}/`,
    root_api: '/api/forum/',
    search_api: pk => `/api/forum/thread/${pk}/search/`,
    search_results: (thread_id, query) => ({
        name: 'forum_search_results',
        params: { id: thread_id },
        query: query,
    }),
    extended_search: pk => ({
        name: 'forum_extended_search',
        params: { id: pk },
	}),
}
