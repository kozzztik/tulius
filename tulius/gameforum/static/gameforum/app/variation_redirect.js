import APILoadMixin from '../../app/components/api_load_mixin.js'
import urls from './urls.js'

export default Vue.component('variation_redirect', {
    mixins: [APILoadMixin,],
    template: '<div></div>',
    methods: {
        load_api(route) {
            return axios.get(
                    '/api/game_forum/variation/'+ route.params.id + '/'
            ).then(response => {
                this.$router.push(
                    urls(response.data.id).room(response.data.thread_id));
            });
        }
    },
});
