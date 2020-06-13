import app from './app.js'
import room from '../pages/room.js'
import thread from '../pages/thread.js'
import redirect from './redirect.js'


export default [
    {path: '/play/thread/:id(\\d+)/', component: redirect, name: 'game_thread_redirrect'},
    {path: '/play/room/:id(\\d+)/', component: redirect, name: 'game_room_redirrect'},
    {path: '/play/:variation_id(\\d+)', component: app,
        children: [
            {path: 'room/:id(\\d+)/', component: room, name: 'game_room'},
            {path: 'thread/:id(\\d+)/', component: thread, name: 'game_thread'},
      ]
    },
]