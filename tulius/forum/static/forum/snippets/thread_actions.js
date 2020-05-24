export default LazyComponent('forum_thread_actions', {
    template: '/static/forum/snippets/thread_actions.html',
    props: ['thread', 'user'],
    data: function () {
        return {
            csrftoken: getCookie('csrftoken'),
            delete_comment: '',
        }
    },
    methods: {
        mark_not_readed() {
            this.$parent.mark_all_not_readed();
        },
        deleteRoom(bvModalEvt) {
            axios.delete(
                    '/api/forum/thread/' + this.thread.id+ '/',
                    {params: {comment: this.delete_comment}}
            ).then(response => {
                if (response.data['result'] == 'success') {
                    this.$root.add_message("Комната успешно удалена", "warning");
                    if (this.thread.parents.length > 0) {
                        this.$router.push({
                            name: 'forum_room',
                            params: { id: this.thread.parents[this.thread.parents.length - 1].id }
                        })
                    } else {
                        this.$router.push({ name: 'forum_root'})
                    }
                } else {
                    this.$root.add_message(response.data['error_text'], "error");
                }
            }).catch(error => this.$root.add_message(error, "error"))
            .then(() => {});
        },
    }
})
