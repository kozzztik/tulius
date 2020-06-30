import app from './app.js'
import index from '../pages/index.js'
import room from '../pages/room.js'
import thread from '../pages/thread.js'
import edit_comment from '../pages/edit_comment.js'
import add_room from '../pages/add_room.js'
import edit_thread from '../pages/edit_thread.js'


export default [
    {path: '/forums/', component: app,
        children: [
            {path: '', component: index, name: 'forum_root'},
            {path: 'room/:id(\\d+)/', component: room, name: 'forum_room'},
            {path: 'thread/:id(\\d+)/', component: thread, name: 'forum_thread'},
            {path: 'edit_comment/:id(\\d+)/', component: edit_comment, name: 'forum_edit_comment'},
            {path: 'add_room/', component: add_room, name: 'forum_add_root_room'},
            {path: 'add_room/:id(\\d+)/', component: add_room, name: 'forum_add_room'},
            {path: 'add_thread/:parent_id(\\d+)/', component: edit_thread, name: 'forum_add_thread'},
            {path: 'edit_thread/:id(\\d+)/', component: edit_thread, name: 'forum_edit_thread'},
        ],
    }
]
