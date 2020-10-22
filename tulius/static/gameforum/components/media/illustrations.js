import baseMixin from '../../../forum/components/media/base.js'

export default LazyComponent('media_illustrations', {
    template: '/static/gameforum/components/media/illustrations.html',
    props: ['variation'],
    mixins: [baseMixin],
    data: function () {
        return {
            images: [],
            add_as_attach: true,
            selected: null,
            tiny_index: null,
            tiny_media_index: null,
        }
    },
    computed: {
        tiny_media_images: function() {
            var result = [];
            for (var image of (this.comment.media.illustrations || []) )
                result.push(this.tiny_image(image));
            return result
        },
        tiny_images: function() {
            var result = [];
            for (var image of this.variation.illustrations)
                result.push(this.tiny_image(image));
            return result
        },
    },
    watch: {
        tiny_index: function(new_value, old_value) {
            if ((new_value === null) || (old_value === null))
                return
            this.selected = this.variation.illustrations[new_value];
        },
        media: function(new_value, old_value) {
            this.images = new_value.illustrations || [];
        },
    },
    methods: {
        tiny_image: image => ({
            src: image.url,
            thumbnail: image.thumb,
            caption: image.title,
        }),
        add_media() {this.$refs.modal.show();},
        get_menu_item() {
            return {
                label: "Добавить иллюстрацию",
                disabled: false,
                action: this.add_media,
            }
        },
        do_add(data) {
            if (this.add_as_attach) {
                if (this.images.length == 0)
                    this.comment.media.illustrations = this.images = [];
                this.images.push(data)
            } else {
                this.comment.body += `<img src="${data.url}">`
            }
            this.$refs.modal.hide();
        },
        on_editor_delete(index) {
            this.images.splice(index, 1);
        },

    },
    created() {
        this.images = this.comment.media.illustrations || [];
    },
})
