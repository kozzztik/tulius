import {LazyComponent} from '../../common/js/vue-common.js'
import axios from '../../common/js/axios.min.js';


export default LazyComponent('forum_voting', {
    template: '/static/forum/components/voting.html',
    props: {
        comment: {
            type: Object,
        },
        editor: {
            type: Boolean,
            default: false,
        },
    },
    data: function () {
        return {
            loading: false,
            show_results: false,
            choice: null,
            menu_item: {},
            voting: null,
            add_form: {
                name: '',
                body: '',
                show_results: false,
                preview_results: false,
                choices: {
                    with_results: false,
                    items: [{name: ''}],
                },
            }
        }
    },
    computed: {
        user: function() {return this.$root.user;},
        media: function() {return this.comment.media},
    },
    watch: {
        media: function(newMedia, oldMedia) {return this.voting = newMedia.voting},
    },
    methods: {
        add_media() {
            this.$refs.modal.show();
        },
        do_vote() {
            if ((this.choice === null)||this.editor||(!this.comment.url))
                return;
            this.loading = true;
            axios.post(
                this.comment.url + 'voting/',
                {'choice': this.choice}
            ).then(response => {
                this.voting = response.data;
            }).catch(error => Vue.app_error_handler(error, "error")
            ).then(() => {
                this.loading = false;
            });
        },
        close_voting() {
            if (this.editor||(!this.comment.url))
                return;
            this.loading = true;
            axios.post(
                this.comment.url + 'voting/', {'close': true}
            ).then(response => {
                this.voting = response.data;
            }).catch(error => Vue.app_error_handler(error, "error")
            ).then(() => {
                this.loading = false;
            });
        },
        on_modal_submit() {
            this.voting = JSON.parse(JSON.stringify(this.add_form));
            this.comment.media.voting = this.voting;
            this.$refs.modal.hide();
            this.menu_item.disabled = true;
        },
        on_editor_delete() {
            this.voting = this.comment.media.voting = null;
            this.menu_item.disabled = false;
        },
        on_editor_edit() {
            this.add_form = JSON.parse(JSON.stringify(this.voting));
            this.$refs.modal.show();
        },
    },
    created() {
        if (this.comment.media.voting)
            this.voting = this.comment.media.voting;
        if (!this.editor)
            return
        this.menu_item = {
            label: "Добавить голосование",
            disabled: false,
            action: this.add_media,
        };
        this.$parent.media_actions.push(this.menu_item);
    },
    beforeDestroy() {
        if (!this.menu_item)
            return
        if (this.$parent.media_actions)
            this.$parent.media_actions = this.$parent.media_actions.filter(
                item => item != this.menu_item, this);
    },
})
