import forum_routes from '../forum/app/routes.js'
import game_forum_routes from '../gameforum/app/routes.js'
import profiles_routes from '../profile/app/routes.js'
import debug_mail from '../debug_mail/routes.js'
import celery_status from '../pages/celery_status.js'


export default [
    ...forum_routes,
    ...game_forum_routes,
    ...profiles_routes,
    ...debug_mail,
    {path: '/celery_status/', component: celery_status, name: 'celery_status'},
];
