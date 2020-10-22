import add_room from '../../forum/pages/add_room.js'
import {LazyComponent} from '../../common/js/vue-common.js'


export default LazyComponent('game_forum_add_room_page', {
    template: '/static/gameforum/pages/add_room.html',
    data: () => ({}),
    computed: {
        variation: function() {return this.$parent.variation},
        urls() {return this.$parent.urls},
    },
    methods: {
        loading_start() {this.$parent.loading_start()},
        loading_end(breadcrumbs) {this.$parent.loading_end(breadcrumbs)},
        thread_breadcrumbs(thread) {return this.$parent.thread_breadcrumbs(thread)},
        right_user_search(query, rights) {
            var result = [];
            for (var c of this.variation.characters) {
                var found = false;
                for (var right of rights)
                    if (right.user.id == c.id) {
                        found = true;
                        break;
                    }
                if (!found)
                    result.push({'id': c.id, 'title': c.title});
            }
            return result;
        },
    }
})