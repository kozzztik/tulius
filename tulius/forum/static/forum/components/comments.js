import comment_component from '../snippets/comment.js'
import pagination_component from '../components/pagination.js'


export default LazyComponent('forum_thread_comments', {
    template: '/static/forum/components/comments.html',
    props: ['thread', 'value'],
    data: function () {
        return {
            pagination: {},
            comments: [],
            mark_read_func: null,
            mark_read_id: null,
            delete_comment_obj: null,
            delete_comment_message: '',
        }
    },
    computed: {
        urls: function() {return this.$parent.urls;},
        user: function() {return this.$root.user;},
    },
    watch: {
        thread: function (val, oldVal) {
            this.load_api(val.id, this.$route.query['page'] || 1);
        },
        value: function (val, oldVal) {
            this.load_api(this.thread.id, val || 1);
        }
    },
    methods: {
        subscribe_comments() {
            if (this.thread.id)
                this.$root.$socket.sendObj({action: 'subscribe_comments', id: this.thread.id});
        },
        unsubscribe_comments() {
            if (this.thread.id) {
                this.$root.$socket.sendObj({action: 'unsubscribe_comments', id: this.thread.id})
            }
            delete this.$options.sockets.onmessage
        },
        websock_message(msg) {
            var data = JSON.parse(msg.data);
            if ((data['.namespaced'] != 'thread_comments') || (data.parent_id != this.thread.id)) return;
            if (data.page > this.pagination.pages_count) {
                this.pagination.pages_count = this.pagination.pages_count + 1;
                this.pagination.pages.push(this.pagination.pages_count);
                this.pagination.is_paginated = true;
            }
            if (data.page != this.value)
                return;
            axios.get(data.url).then(response => {
                var new_comment = response.data;
                new_comment.is_liked = false;
                for (var comment of this.comments)
                    if (comment.id == new_comment.id)
                        return;
                this.comments.push(new_comment);
                if (!this.thread.not_read_comment)
                    this.thread.not_read_comment = {
                        id: new_comment.id, page_num: new_comment.page, count: 0}
                this.thread.not_read_comment.count += 1;
            }).catch().then(() => {});
        },
        fast_reply(comment) {
            var component;
            for (var ref of this.$refs.comments) {
                component = ref.childNodes[0].__vue__;
                if (component.comment.id == comment.id) {
                    this.$parent.$refs.reply_form.fast_reply(comment, component);
                    break;
                }
            }
        },
        update_likes() {
            var comment_ids = []
            for (var comment of this.comments)
                comment_ids.push(comment.id);
            if (!this.user.is_anonymous && (comment_ids.length > 0)) {
                axios.get(this.urls.likes_api, {params: {ids: comment_ids.join(',')}}
                ).then(response => {
                    for (comment of this.comments)
                        comment.is_liked = response.data[comment.id];
                }).catch(error => this.$root.add_message(error, "error"));
            }
        },
        update_to_comments(data) {
            if (data.pagination.page_num != this.value) {
                this.$router.push({path: this.$router.path, query: {page: data.pagination.page_num}});
                return
            }
            this.set_new_comments(data.comments);
            this.pagination = data.pagination;
        },
        set_new_comments(comments) {
            for (var comment of comments)
                comment.is_liked = null;
            this.comments = comments;
            this.update_likes();
        },
        load_api(pk, page) {
            this.unsubscribe_comments();
            this.cleanup_reply_form();
            if (this.$parent.$refs.reply_form)
                this.$parent.$refs.reply_form.hide();
            this.$root.loading_start();
            axios.get(this.thread.url + 'comments_page/', {params: {page: this.value}}).then(response => {
                this.set_new_comments(response.data.comments);
                this.pagination = response.data.pagination;
                this.subscribe_comments();
                if (this.$route.hash)
                    Vue.nextTick( () => {
                        this.scroll_to_comment(this.$route.hash.replace('#', ''), 0);
                    });
            }).catch(error => this.$root.add_message(error, "error")).then(() => {
                this.$root.loading_end(null);
                if (this.$parent.$refs.reply_form)
                    this.$parent.$refs.reply_form.show();
            });
        },
        cleanup_reply_form() {
            if (this.$parent.$refs.reply_form)
                this.$parent.$refs.reply_form.cleanup_reply_form();
        },
        mark_as_read(comment) {
            if (this.user.is_anonymous)
                return;
            if (comment.id <= this.thread.last_read_id)
                return;
            if (this.mark_read_id)
                return;
            // console.log('поставили таймер')
            this.mark_read_id = comment.id;
            this.mark_read_func = setTimeout(this.do_mark_mark_as_read, 1000, comment.id);
        },
        cancel_mark_as_read(comment) {
            if (this.mark_read_id == comment.id) {
                // console.log('отменили таймер');
                clearTimeout(this.mark_read_func);
                this.mark_read_id = null;
            }
        },
        do_mark_mark_as_read(comment_id) {
            // console.log('пошел запрос');
            axios.post(this.thread.url + 'read_mark/', {'comment_id': comment_id}).then(response => {
                this.thread.last_read_id = response.data.last_read_id;
                this.thread.not_read_comment = response.data.not_read_comment;
            }).catch(error => this.$root.add_message(error, "error")).then(() => {
                this.mark_read_id = null;
                this.mark_read_func = null;
            });
        },
        delete_comment(comment) {
            this.delete_comment_obj = comment;
            this.$bvModal.show('commentDelete');
        },
        do_delete_comment() {
            this.$root.loading_start();
            axios.delete(
                this.delete_comment_obj.url,
                {params: {comment: this.delete_comment_message}}
            ).then(response => {
                if (response.data.pages_count < this.comments_page)
                    this.$router.push({path: this.$router.path, query: {page: data.pagination.page_num}});
                else
                    this.load_api(this.thread_id, this.value);
            }).catch(error => this.$root.add_message(error, "error")).then(() => {
                 this.$root.loading_end(null);
            });
        },
        to_not_read_comment() {
            if (!this.thread.not_read_comment)
                return;
            if (this.thread.not_read_comment.page_num != this.value)
                this.$router.push({
                    path: this.$router.path,
                    query: {page: this.thread.not_read_comment.page_num},
                    hash: '#' + this.thread.not_read_comment.id})
            else
                this.scroll_to_comment(this.thread.not_read_comment.id, 0);
        },
        scroll_to_comment(comment_id, retry) {
            var found = null;
            for (var ref of this.$refs.comments)
                if (ref.parentElement.id == comment_id) {
                    ref.scrollIntoView(false);
                    return
                }
            if (retry > 10) {
                console.log('Scroll not found ref');
                return
            }
            setTimeout(this.scroll_to_comment, 200, comment_id, retry + 1);
        },
    },
    mounted() {
        this.$parent.$options.sockets.onopen = this.subscribe_comments;
        this.$parent.$options.sockets.onmessage = this.websock_message;
        this.load_api(this.thread.id, this.$route.query['page'] || 1)
    },
    beforeDestroy() {
        this.unsubscribe_comments();
    },
})
