import latest_post from './latest_post.js'

export default LazyComponent('forum_thread_list', {
    template: '/static/forum/snippets/thread_list.html',
    props: ['threads'],
})
