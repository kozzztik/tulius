import index from '../pages/index.js'
import room from '../pages/room.js'
import thread from '../pages/thread.js'


export default [
    {path: '/forums/', component: index},
    {path: '/forums/room/:id(\\d+)/', component: room},
    {path: '/forums/thread/:id(\\d+)/', component: thread},
]
