import avatar from '../snippets/avatar.js'
import voting from '../components/voting.js'


export default LazyComponent('forum_comment', {
    template: '/static/forum/snippets/comment.html',
    props: {
        comment: {
            type: Object,
        },
        user: {
            type: Object,
        },
        thread: {
            type: Object,
        },
        preview: {
            type: Boolean,
            default: false,
        },
    },
    methods: {
        forum_datetime(v) {
            return forum_datetime(new Date(v));
        }
    },
})
