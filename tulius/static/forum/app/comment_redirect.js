import Vue from 'vue'
import APILoadMixin from '../../app/components/api_load_mixin.js'
import axios from '../../common/js/axios.min.js';


export default Vue.component('forum_comment_redirect', {
    mixins: [APILoadMixin,],
    template: '<div></div>',
    computed: {
        urls: function() {return this.$parent.urls;},
    },
    methods: {
        load_api(route) {
            return axios.get(
                this.urls.comment_api(route.params.id)
            ).then(response => {
                this.$router.push(this.urls.comment(response.data))
            })
        }
    }
});
