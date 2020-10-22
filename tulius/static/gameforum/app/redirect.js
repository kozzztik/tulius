import axios from '../../common/js/axios.min.js';


export default Vue.component('game_thread_redirect', {
    template: '<div></div>',
    data: function () {
        return {}
    },
    methods: {
        load_api(pk) {
            this.$root.loading_start();
            axios.get('/api/game_forum/thread_redirrect/'+ pk + '/').then(response => {
                const api_response = response.data;
                const params =  {
                    variation_id: api_response.variation_id,
                    thread_id: pk,
                }
                if (api_response.room)
                    this.$router.push({name: 'game_room', params: params })
                else
                    this.$router.push({name: 'game_thread', params: params });
            }).catch(error => this.$parent.add_message(error, "error"))
            .then(() => {
                this.$root.loading_end([]);
            });

        }
    },
    mounted() {this.load_api(this.$route.params.id)},
    beforeRouteUpdate (to, from, next) {
        this.load_api(to.params.id);
        next();
    }
});
