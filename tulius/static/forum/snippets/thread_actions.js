import thread_access from '../components/thread_access.js'
import edit_room from '../components/edit_room.js'
import move_thread from '../components/move_thread.js'
import {LazyComponent} from '../../common/js/vue-common.js'
import axios from '../../common/js/axios.min.js';


export default LazyComponent('forum_thread_actions', {
    template: '/static/forum/snippets/thread_actions.html',
    props: ['thread'],
    data: function () {
        return {
            delete_comment: '',
            search_text: '',
        }
    },
    computed: {
        user: function() {return this.$root.user;},
        urls() {return this.$parent.urls},
        delete_title: function() {
            return this.thread.room ? 'Удалить эту комнату?' : 'Удалить эту тему?';
        }
    },
    methods: {
        mark_not_read() {
            axios.delete(this.thread.url + 'read_mark/').then(response => {
                this.thread.not_read = response.data.not_read;
            });
        },
        mark_all_as_readed() {
            this.$parent.mark_all_as_readed();
        },
        delete_thread(bvModalEvt) {
            axios.delete(this.thread.url, {params: {comment: this.delete_comment}}
            ).then(response => {
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
            }).catch(error => this.$root.add_message(error, "error"))
            .then(() => {});
        },
        search_submit() {
            var parents = this.thread.parents;
            var pk = parents.length > 0 ? parents[0].id : this.thread.id;
            this.$router.push(
                this.urls.search_results({
                    thread_id: pk,
                    text: this.search_text}
                )
            );
        }
    }
})
