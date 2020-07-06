import baseMixin from './base.js'

export default LazyComponent('forum_html_media', {
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
            this.menu_item.disabled = (this.html_data != '');
        },
    },
    computed: {
        user: function() {return this.$root.user;},
    },
    methods: {
        add_media() {
            this.$refs.modal.show();
        },
        get_menu_item() {
            if (this.user.superuser)
                return {
                    label: "Добавить HTML код",
                    disabled: false,
                    action: this.add_media,
                }
            return null;
        },
        do_add() {
            this.comment.media.html = this.html_data;
            this.menu_item.disabled = (this.html_data != '');
            this.$refs.modal.hide();
        },
        on_editor_delete() {
            this.html_data = '';
            this.media.html = '';
            this.menu_item.disabled = false;
        },

    },
    created() {
        this.html_data = this.comment.media.html || '';
    },
})
