import forum_routes from '../forum/app/routes.js'
import game_forum_routes from '../gameforum/app/routes.js'
import profiles_routes from '../profile/app/routes.js'

export default [
    ...forum_routes,
    ...game_forum_routes,
    ...profiles_routes,
];
