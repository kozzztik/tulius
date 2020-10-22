import baseMixin from './base.js'
import {LazyComponent} from '../../../common/js/vue-common.js'
import axios from '../../../common/js/axios.min.js';


export default LazyComponent('forum_images', {
    template: '/static/forum/components/media/images.html',
    mixins: [baseMixin],
    data: function () {
        return {
            images: [],
            user_images: null,
            add_as_attach: true,
            uploaded_file: null,
            selected: null,
            tiny_index: null,
            tiny_images: [],
            tiny_media_index: null,
        }
    },
    computed: {
        tiny_media_images: function() {
            var result = [];
            for (var image of (this.comment.media.images || []) )
                result.push(this.tiny_image(image));
            return result
        },
    },
    watch: {
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
        media: function(new_value, old_value) {
            this.images = new_value.images || [];
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
                if (this.images.length == 0)
                    this.comment.media.images = this.images = [];
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
        this.images = this.comment.media.images || [];
    },
})
