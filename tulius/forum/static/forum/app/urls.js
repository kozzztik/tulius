export default {
    room: room_id => ({name: 'forum_room', params: {id: room_id},}),
    deleted_threads: room_id => ({name: 'forum_deleted_threads', params: {id: room_id},}),
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
    thread_restore_api: pk => `/api/forum/thread/${pk}/restore/`,
    thread_fix_api: pk => `/api/forum/thread/${pk}/fix/`,
    forum_fix_api: pk => `/api/forum/fix/`,
    comment_api: pk => `/api/forum/comment/${pk}/`,
    root_api: '/api/forum/',
    search_api: '/api/forum/search/',
    search_results: query => ({
        name: 'forum_search_results',
        query: query,
    }),
    extended_search: query => ({
        name: 'forum_extended_search',
        query: query,
	}),
	elastic_reindex_all_api: '/api/forum/elastic/reindex/all/',
	elastic_reindex_forum_api: '/api/forum/elastic/reindex/forum_all/',
	elastic_reindex_thread_api: pk => `/api/forum/elastic/reindex/thread/${pk}/`,
}
