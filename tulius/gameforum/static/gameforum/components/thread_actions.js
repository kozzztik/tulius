export default LazyComponent('game_forum_thread_actions', {
    template: '/static/gameforum/components/thread_actions.html',
    props: ['variation', 'thread', 'user'],
    data: function () {
        return {
            csrftoken: getCookie('csrftoken'),
            delete_comment: '',
        }
    },
    computed: {
        delete_title: function() {
            if (this.thread.room)
                return 'Удалить эту комнату?'
            else
                return 'Удалить эту тему?';
        }
    },
    methods: {
        mark_not_readed() {
            this.$parent.mark_all_not_readed();
        },
        delete_thread(bvModalEvt) {
            axios.delete(
                    '/api/forum/thread/' + this.thread.id+ '/',
                    {params: {comment: this.delete_comment}}
            ).then(response => {
                if (response.data['result'] == 'success') {
                    if (this.thread.room)
                        this.$root.add_message("Комната успешно удалена", "warning");
                    else
                        this.$root.add_message("Тема успешно удалена", "warning");
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
