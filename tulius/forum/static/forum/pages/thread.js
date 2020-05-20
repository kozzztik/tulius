import thread_actions from '../snippets/thread_actions.js'
import online_status from '../snippets/online_status.js'
import comment_component from '../snippets/comment.js'
import pagination_component from '../components/pagination.js'
import reply_form_component from '../components/reply_form.js'


export default LazyComponent('forum_thread_page', {
    template: '/static/forum/pages/thread.html',
    data: function () {
        return {
            breadcrumbs: [],
            loading: true,
            thread: {},
            comments: [],
            pagination: {},
            comments_page: 1,
            user: {},
            online_ids: null,
        }
    },
    methods: {
        subscribe_comments() {
            if (this.thread.id)
                this.$socket.sendObj({action: 'subscribe_comments', id: this.thread.id});
        },
        unsubscribe_comments() {
            if (this.thread.id) {
                this.$socket.sendObj({action: 'unsubscribe_comments', id: this.thread.id})
            }
            delete this.$options.sockets.onmessage
        },
        websock_message(msg) {
            var data = JSON.parse(msg.data);
            if ((data['.namespaced'] != 'thread_comments') || (data.thread_id != this.thread.id)) return;
            console.log(msg);
        },
        fast_reply(comment) {
            var component;
            for (component of this.$refs.comments) {
                if (component.comment.id == comment.id) {
                    var el = this.$refs.reply_form.$el;
                    el.parentNode.removeChild(el);
                    component.$el.parentNode.appendChild(el);
                    break;
                }
            }
            this.$refs.reply_form.fast_reply(comment);
        },
        update_likes() {
            var comment;
            var comment_ids = []
            for (comment of this.comments) {
                comment.is_liked = null;
                comment_ids.push(comment.id);
            }
            if (!this.user.is_anonymous) {
                axios.get('/api/forum/likes/', {params: {ids: comment_ids.join(',')}}
                ).then(response => {
                    var likes = response.data;
                    for (comment of this.comments) {
                        comment.is_liked = likes[comment.id];
                    }
                    for (comment of this.$refs.comments) {
                        comment.update_like();
                    }
                }).catch(error => this.$parent.add_message(error, "error"));
            }
        },
        update_comments() {
            this.loading = true;
            this.$parent.loading_start();
            axios.get('/api/forum/thread/'+ this.thread.id + '/comments_page/' + this.comments_page + '/').then(response => {
                this.comments = response.data.comments;
                this.$options.sockets.onmessage = this.websock_message;
                this.subscribe_comments();
                this.pagination = response.data.pagination;
                this.update_online_users()
            }).catch(error => this.$parent.add_message(error, "error")).then(() => {
                this.loading = false;
                this.$parent.loading_end(this.breadcrumbs);
                this.update_likes();
            });
        },
        load_api(pk, page) {
            this.unsubscribe_comments();
            this.$parent.loading_start();
            this.comments_page = page;
            axios.get('/api/forum/thread/'+ pk).then(response => {
                const api_response = response.data;
                this.breadcrumbs = [{"url": "/forums/", "title": "Форумы"}]
                api_response.parents.forEach(
                    (item, i, arr) => this.breadcrumbs.push(
                        {"url": item.url, "title": item.title}
                    ));
                this.breadcrumbs.push(
                    {"url": api_response.url, "title": api_response.title});
                this.thread = api_response;
                this.user = this.$parent.user;
                this.update_comments()
            }).catch(error => this.$parent.add_message(error, "error"))
            .then(() => {
                this.$parent.loading_end(this.breadcrumbs);
            });
        },
        cleanup_reply_form() {
            var el = this.$refs.reply_form.$el;
            this.$refs.reply_form.cleanup_reply_form();
            el.parentNode.removeChild(el);
            this.$refs.reply_form_parking.appendChild(el);
        },
        on_online_ids_loaded(user_ids) {
            this.online_ids = user_ids;
            this.update_online_users();
        },
        update_online_users() {
            var comment;
            for (comment of this.comments) {
                if (this.online_ids.indexOf(comment.user.id) != -1) comment.user.online_status = 'here';
            }
        }
    },
    mounted() {
        this.$options.sockets.onopen = this.subscribe_comments;
        this.load_api(this.$route.params.id, this.$route.query['page'] || 1)
    },
    beforeRouteUpdate (to, from, next) {
        this.cleanup_reply_form();
        this.load_api(to.params.id, to.query['page'] || 1);
        next();
    },
    beforeDestroy() {
        this.unsubscribe_comments();
    },
})
