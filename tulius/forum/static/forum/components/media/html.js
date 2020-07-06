import baseMixin from './base.js'

export default LazyComponent('forum_images', {
    template: '/static/forum/components/media/html.html',
    mixins: [baseMixin],
    data: function () {
        return {
            html_data: '',
            uploaded_file: null,
        }
    },
    watch: {
        uploaded_file: function(newFile, oldFile) {
            if (!newFile)
                return;
            axios.put(
                    '/api/forum/uploaded_files/', newFile,
                    {params: {
                        file_name: newFile.name,
                        content_type: newFile.type
                    }}
            ).then(response => {
                this.html_data += response.data.url;
            });
        },
        media: function(new_value, old_value) {
            this.html_data = new_value.html || '';
        },
    },
    methods: {
        add_media() {
            this.$refs.modal.show();
        },
        get_menu_item() {
            return {
                label: "Добавить HTML код",
                disabled: false,
                action: this.add_media,
            }
        },
        do_add(data) {
            this.comment.html = this.html_data;
            this.$refs.modal.hide();
        },
        on_editor_delete(index) {
            this.html_data = '';
            this.media.html = '';
        },

    },
    created() {
        this.html_data = this.comment.media.html || '';
    },
})
