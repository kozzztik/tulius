import app from './app.js'
import room from '../pages/room.js'
import thread from '../pages/thread.js'
import redirect from './redirect.js'
import edit_comment from '../pages/edit_comment.js'
import add_room from '../pages/add_room.js'
import edit_thread from '../pages/edit_thread.js'


export default [
    {path: '/play/thread/:id(\\d+)/', component: redirect, name: 'game_thread_redirrect'},
    {path: '/play/room/:id(\\d+)/', component: redirect, name: 'game_room_redirrect'},
    {path: '/play/:variation_id(\\d+)', component: app,
        children: [
            {path: 'room/:id(\\d+)/', component: room, name: 'game_room'},
            {path: 'thread/:id(\\d+)/', component: thread, name: 'game_thread'},
            {path: 'edit_comment/:id(\\d+)/', component: edit_comment, name: 'game_edit_comment'},
            {path: 'add_room/:id(\\d+)/', component: add_room, name: 'game_add_room'},
            {path: 'add_thread/:parent_id(\\d+)/', component: edit_thread, name: 'game_add_thread'},
            {path: 'edit_thread/:id(\\d+)/', component: edit_thread, name: 'game_edit_thread'},
      ]
    },
]