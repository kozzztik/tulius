import latest_post from './latest_post.js'

export default LazyComponent('forum_room_list', {
    template: '/static/forum/snippets/room_list.html',
    props: ['rooms'],
    computed: {
        urls() {return this.$parent.urls},
    }
})
