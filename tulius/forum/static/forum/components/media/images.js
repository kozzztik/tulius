import baseMixin from './base.js'

export default LazyComponent('forum_images', {
    template: '/static/forum/components/media/images.html',
    mixins: [baseMixin],
    data: function () {
        return {
            user_images: null,
            images: null,
            add_as_attach: false,
            uploaded_file: null,
            selected: null,
            tiny_index: null,
            tiny_images: [],
        }
    },
    watch: {
        media: function(newMedia, oldMedia) {return this.images = newMedia.images},
        uploaded_file: function(newFile, oldFile) {
            if (!newFile)
                return;
            axios.put(
                    '/api/forum/images/', newFile,
                    {params: {
                        file_name: newFile.name,
                        content_type: newFile.type
                    }}
            ).then(response => {
                this.user_images.unshift(response.data);
                this.tiny_images.unshift(this.tiny_image(response.data))
                this.do_add(response.data);
            });
        },
        tiny_index: function(new_value, old_value) {
            if ((new_value === null) || (old_value === null))
                return
            this.selected = this.user_images[new_value];
        },
    },
    methods: {
        tiny_image: image => ({
            src: image.url,
            thumbnail: image.thumb,
            caption: image.file_name,
        }),
        add_media() {
            if (!this.user_images) {
                axios.get('/api/forum/images/').then(response => {
                    this.user_images = response.data.images;
                    this.tiny_images = [];
                    for (var image of this.user_images)
                        this.tiny_images.push(this.tiny_image(image))
                });
            }
            this.$refs.modal.show();
        },
        get_menu_item() {
            return {
                label: "Добавить изображение",
                disabled: false,
                action: this.add_media,
            }
        },
        do_add(data) {
            if (this.add_as_attach) {
            } else {
                this.comment.body += `<img src="${data.url}">`
            }
            this.$refs.modal.hide();
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

    },
    created() {
        if (this.comment.media.voting)
            this.images = this.comment.media.images;
    },
})
