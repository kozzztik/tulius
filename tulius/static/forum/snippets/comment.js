import avatar from '../snippets/avatar.js'
import voting from '../components/voting.js'
import {LazyComponent} from '../../common/js/vue-common.js'
import axios from '../../common/js/axios.min.js';
import {forum_datetime} from '../../common/js/vue-common.js'


export default LazyComponent('forum_comment', {
    template: '/static/forum/snippets/comment.html',
    props: {
        comment: {
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
    computed: {
        urls: function() {return this.$parent.urls;},
        user: function() {return this.$root.user;},
        like_img: function() {
            if (this.comment.is_liked === null) return null;
            return '/static/forum/img/' +
                (this.comment.is_liked ? 'like.gif' : 'unlike.gif');
        },
        is_read: function() {
            if (this.user.is_anonymous)
                return true;
            if (this.comment.user.id == this.user.id)
                return true;
            if (!this.thread.not_read)
                return true;
            return (this.thread.not_read.id > this.comment.id);
        },
    },
    methods: {
        forum_datetime(v) {
            return forum_datetime(new Date(v));
        },
        do_like() {
            var old_value = this.comment.is_liked;
            this.comment.is_liked = null;
            axios.post(this.urls.likes_api,
                {id: this.comment.id, value: !old_value}
            ).then(response => {
                old_value = response.data.value;
            }).catch(error => this.$root.add_message(error, "error")
            ).then(() => {
                this.comment.is_liked = old_value;
            });
        },
        delete_comment() {
            this.$parent.delete_comment(this.comment);
        },
        scroll_up() {
            window.scrollTo({left: 0, top: 0, behavior: 'smooth'});
        },
    }
})
