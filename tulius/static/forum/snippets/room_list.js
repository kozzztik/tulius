import latest_post from './latest_post.vue'
import {LazyComponent} from '../../common/js/vue-common.js'
import axios from '../../common/js/axios.min.js';


export default LazyComponent('forum_room_list', {
    template: '/static/forum/snippets/room_list.html',
    props: ['rooms'],
    computed: {
        urls() {return this.$parent.urls},
    },
    methods: {
        to_comment(pk) {
            this.$parent.loading_start();
            axios.get(this.urls.comment_api(pk)).then(response => {
                this.$parent.loading_end()
                this.$router.push(this.urls.comment(response.data));
            })
        }
    },
})
