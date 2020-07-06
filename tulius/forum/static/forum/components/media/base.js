export default {
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
            menu_item: {},
        }
    },
    computed: {
        media: function() {return this.comment.media},
    },
    created() {
        if (!this.editor)
            return
        this.menu_item = this.get_menu_item();
        if (this.menu_item)
            this.$parent.media_actions.push(this.menu_item);
    },
    beforeDestroy() {
        if (!this.menu_item)
            return
        if (this.$parent.media_actions)
            this.$parent.media_actions.filter(item => item != this.menu_item);
    }
}