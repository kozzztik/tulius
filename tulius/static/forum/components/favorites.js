import comment_component from '../snippets/comment.js'
import APILoadMixin from '../../app/components/api_load_mixin.js'
import urls from '../app/urls.js'


export default LazyComponent('forum_favorites', {
    mixins: [APILoadMixin,],
    template: '/static/forum/components/favorites.html',
    props: ['url'],
    data: () => ({
        groups: [],
        urls: urls,
    }),
    computed: {
    },
    methods: {
        load_api(route) {
            return axios.get(this.url).then(response => {
                for (var group of response.data.groups) {
                    group.show = false;
                    for (var item of group.items)
                        item.thread.online_ids = [];
                }
                this.groups = response.data.groups;
            })
        },
    },
});