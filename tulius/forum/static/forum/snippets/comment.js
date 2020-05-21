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
        }
    },
    computed: {
        like_img: function() {
            if (this.comment.is_liked === null) return null;
            return '/static/forum/img/' +
                (this.comment.is_liked ? 'like.gif' : 'unlike.gif');
        }
    },
    methods: {
        forum_datetime(v) {
            return forum_datetime(new Date(v));
        },
        do_like() {
            var new_value = !this.comment.is_liked;
            this.comment.is_liked = null;
            axios.post('/api/forum/likes/',
                {id: this.comment.id, value: new_value}
            ).then(response => {
                this.comment.is_liked = response.data.value;
            }).catch(error => this.$parent.add_message(error, "error"));
        },
    }
})
