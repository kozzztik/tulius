import index from '../pages/index.js'
import room from '../pages/room.js'


export default [
    {path: '/forums/', component: index},
    {path: '/forums/room/:id(\\d+)/', component: room},
]