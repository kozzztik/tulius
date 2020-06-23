import index from '../pages/index.js'
import room from '../pages/room.js'
import thread from '../pages/thread.js'
import edit_comment from '../pages/edit_comment.js'


export default [
    {path: '/forums/', component: index, name: 'forum_root'},
    {path: '/forums/room/:id(\\d+)/', component: room, name: 'forum_room'},
    {path: '/forums/thread/:id(\\d+)/', component: thread, name: 'forum_thread'},
    {path: '/forums/edit_comment/:id(\\d+)/', component: edit_comment, name: 'forum_edit_comment'},

]
