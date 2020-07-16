import APILoadMixin from '../../app/components/api_load_mixin.js'
import urls from './urls.js'


export default LazyComponent('gameforum_app', {
    mixins: [APILoadMixin,],
    template: '/static/gameforum/app/app.html',
    data: function () {
        return {
            loading: true,
            variation: {id: null},
            urls: null,
        }
    },
    methods: {
        load_api(route) {
            if (route.params.variation_id == this.variation.id)
                return;
            this.urls = urls(route.params.variation_id);
            return axios.get(
                '/api/game_forum/variation/'+ route.params.variation_id + '/'
            ).then(response => {
                this.variation = response.data;
                this.loading = false;
            })
        },
        loading_start() {this.$root.loading_start()},
        loading_end(breadcrumbs) {
            if (!breadcrumbs)
                return this.$root.loading_end(breadcrumbs);
            const updated_breadcrumbs = [];
            if (this.variation.game)
                updated_breadcrumbs.push({
                    'title': 'Игра',
                    'url': '/games/game/' + this.variation.game.id + '/',
                    'old_style': true,
                })
            else
                updated_breadcrumbs.push({
                    'title': 'Вариация',
                    'url': '/stories/variation/' + this.variation.id + '/main/',
                    'old_style': true,
                })
            this.$root.loading_end([...updated_breadcrumbs, ...breadcrumbs]);
        },
        thread_breadcrumbs(thread) {
            var breadcrumbs = []
            for (var item of thread.parents)
                breadcrumbs.push({
                    title: item.title,
                    url: this.urls.room(item.id),
                });
            breadcrumbs.push({
                title: thread.title,
                url: thread.room ? this.urls.room(thread.id) : this.urls.thread(thread.id),
            });
            return breadcrumbs;
        }
    },
})
