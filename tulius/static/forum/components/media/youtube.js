import baseMixin from './base.js'
import {LazyComponent} from '../../../common/js/vue-common.js'


export default LazyComponent('forum_youtube_media', {
    template: '/static/forum/components/media/youtube.html',
    mixins: [baseMixin],
    data: function () {
        return {
            video: null,
            preview_video: null,
            search: '',
        }
    },
    watch: {
        media: function(new_value, old_value) {
            this.video = new_value.youtube || null;
            this.menu_item.disabled = !(this.video === null);
        },
        search: function(new_value, old_value) {
            var result = new_value.match(/http(?:s?):\/\/(?:www\.)?youtu(?:be\.com\/watch\?v=|\.be\/)([\w\-\_]*)(&(amp;)?‌​[\w\?‌​=]*)?/);
            if (result)
                this.preview_video = result[1];
        }
    },
    methods: {
        add_media() {
            this.preview_video = this.video;
            this.search = '';
            this.$refs.modal.show();
        },
        get_menu_item() {
            return {
                label: "Добавить Youtube видео",
                disabled: false,
                action: this.add_media,
            }
        },
        do_add() {
            if (!this.preview_video)
                return;
            this.comment.media.youtube = this.preview_video;
            this.video = this.preview_video;
            this.menu_item.disabled = !(this.video === null);
            this.$refs.modal.hide();
        },
        on_editor_delete() {
            this.video = null;
            this.media.youtube = null;
            this.menu_item.disabled = false;
        },

    },
    created() {
        this.video = this.comment.media.youtube || null;
    },
})
