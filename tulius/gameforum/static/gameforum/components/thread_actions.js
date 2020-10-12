import edit_room from '../../forum/components/edit_room.js'
import move_thread from '../../forum/components/move_thread.js'


export default LazyComponent('game_forum_thread_actions', {
    template: '/static/gameforum/components/thread_actions.html',
    props: ['variation', 'thread', 'upper'],
    data: function () {
        return {
            delete_comment: '',
            modal_role: {},
            image_index: null,
            search_text: '',
        }
    },
    computed: {
        urls: function() {return this.$parent.urls;},
        user: function() {return this.$root.user;},
        delete_title: function() {
            if (this.thread.room)
                return 'Удалить эту комнату?'
            else
                return 'Удалить эту тему?';
        },
        images: function() {
            var result = [];
            for (var image of this.variation.illustrations)
                result.push({
                    src: image.url,
                    thumbnail: image.thumb,
                    caption: image.title,
                });
            return result;
        }
    },
    methods: {
        mark_all_as_read() {
            this.$parent.mark_all_as_read();
        },
        mark_not_readed() {
            this.$parent.mark_all_not_readed();
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
                        name: 'game_room',
                        params: {
                            id: this.thread.parents[this.thread.parents.length - 1].id,
                            variation_id: this.variation.id,
                        }
                    })
                } else {
                    this.$router.push({ name: 'forum_root'})
                }
            }).catch(error => this.$root.add_message(error, "error"))
            .then(() => {});
        },
        show_char_modal(char_id) {
            var char;
            for (char of this.variation.characters) {
                if (char.id == char_id) {
                    this.modal_role = char;
                       this.$bvModal.show('characterModal' + this.upper);
                    break;
                }
            }
        },
        role_with_link(role_id) {
            var role;
            for (role of this.variation.characters) {
                if (role.id == role_id)
                    return true;
            }
            return false;
        },
        right_user_search(query, rights) {
            var result = [];
            for (var c of this.variation.characters) {
                var found = false;
                for (var right of rights)
                    if (right.user.id == c.id) {
                        found = true;
                        break;
                    }
                if (!found)
                    result.push({'id': c.id, 'title': c.title});
            }
            return result;
        },
        search_submit() {
            var parents = this.thread.parents;
            var pk = parents.length > 0 ? parents[0].id : this.thread.id;
            this.$router.push(
                this.urls.search_results({
                    thread_id: pk,
                    text: this.search_text
                })
            );
        }
    },
})
