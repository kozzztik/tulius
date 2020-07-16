export default function(variation_id) {
    return {
        room: room_id => ({
            name: 'game_room',
            params: {
                id: room_id,
                variation_id: variation_id
            },
        }),
        add_room: room_id => ({
            name: 'game_add_room',
            params: {id: room_id, variation_id: variation_id}
        }),
        thread: (thread_id, page) => ({
            name: 'game_thread',
            params: {
                id: thread_id,
                variation_id: variation_id
            },
            query: { page: page },
        }),
        comment: comment => ({
            name: 'game_thread',
            params: {
                id: comment.thread.id,
                variation_id: variation_id
            },
            query: { page: comment.page },
            hash: '#' + comment.id,
        }),
        add_thread: thread_id => ({
            name: 'game_add_thread',
            params: {parent_id: thread_id, variation_id: variation_id},
        }),
        edit_thread: thread_id => ({
            name: 'game_edit_thread',
            params: {id: thread_id, variation_id: variation_id},
        }),
        edit_comment: comment_id => ({
            name: 'game_edit_comment',
            params: { id: comment_id, variation_id: variation_id },
        }),
        thread_api: pk => `/api/game_forum/variation/${variation_id}/thread/${pk}/`,
        thread_move_api: pk => `/api/game_forum/variation/${variation_id}/thread/${pk}/move/`,
        comment_api: pk => `/api/game_forum/variation/${variation_id}/comment/${pk}/`,
        root_api: '/api/forum/',
        search_api: pk => `/api/game_forum/variation/${variation_id}/thread/${pk}/search/`,
        search_results: (thread_id, query) => ({
            name: 'game_search_results',
            params: { id: thread_id, variation_id: variation_id },
            query: query,
        }),
        extended_search: pk => ({
            name: 'game_extended_search',
            params: { id: pk, variation_id: variation_id },
        }),
	}
}