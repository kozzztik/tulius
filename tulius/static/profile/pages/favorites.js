import favorites from '../../forum/components/favorites.js'
import game_favorites from '../../gameforum/components/favorite_comment.js'
import APILoadMixin from '../../app/components/api_load_mixin.js'
import {LazyComponent} from '../../common/js/vue-common.js'


export default LazyComponent('profile_favorites', {
    mixins: [APILoadMixin,],
    template: '/static/profile/pages/favorites.html',
    props: ['url'],
    data: () => ({
        breadcrumbs: [{
            title: 'Избранное',
            url: {name: 'favorites'}
        }],
    }),
    methods: {
        loading_start() {this.$root.loading_start()},
        loading_end(breadcrumbs) {this.$root.loading_end(breadcrumbs)},
        load_api(route) {
            this.$root.loading_start();
            this.$root.loading_end(this.breadcrumbs);
        },
    },
});