export default LazyComponent('gameforum_app', {
    template: '/static/gameforum/app/app.html',
    data: function () {
        return {
            loading: true,
            variation: {id: null},
            user: {},
        }
    },
    methods: {
        load_api(pk) {
            if (pk == this.variation.id)
                return;
            this.loading = true;
            this.$root.loading_start();
            axios.get('/api/game_forum/variation/'+ pk + '/').then(response => {
                this.variation = response.data;
                this.user = this.$root.user;
            }).catch(error => this.$parent.add_message(error, "error"))
            .then(() => {
                this.loading = false;
                this.$root.loading_end([]);
            });
        },
        loading_start() {this.$root.loading_start()},
        loading_end(breadcrumbs) {
            const updated_breadcrumbs = [];
            if (this.variation.game)
                updated_breadcrumbs.push({
                    'title': 'Игра',
                    'url': '/games/game/' + this.variation.game.id + '/',
                })
            else
                updated_breadcrumbs.push({
                    'title': 'Вариация',
                    'url': '/stories/variation/' + this.variation.id + '/main/',
                })
            this.$root.loading_end([...updated_breadcrumbs, ...breadcrumbs]);
        }
    },
    mounted() {this.load_api(this.$route.params.variation_id)},
    beforeRouteUpdate (to, from, next) {
        this.load_api(to.params.variation_id);
        next();
    }
})
