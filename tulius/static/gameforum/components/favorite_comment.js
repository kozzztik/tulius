import urls from '../app/urls.js'
import {LazyComponent} from '../../common/js/vue-common.js'


export default LazyComponent('game_forum_favorite_comment', {
    template: '/static/gameforum/components/favorite_comment.html',
    props: ['group', 'item'],
    data: function() {
        return {
            urls: urls(this.group.variation_id),
        }
    },
    methods: {},
})
