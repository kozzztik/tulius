
export default LazyComponent('tulius_ckeditor', {
    template: '/static/ckeditor4/components/tulius_ckeditor.html',
    props: ['value'],
    data () {
        return {
            editorData: '',
            editorConfig: {
                language: 'ru',
                extraPlugins: 'autogrow,font,colorbutton,image,uploadimage,filebrowser',
                removePlugins: 'elementspath,stylescombo',
                removeButtons: 'Anchor,BGColor,Font,Format,Subscript,Superscript,HorizontalRule,Table',
                resize_enabled: false,
                contentsCss: '/static/forum/css/tulius-forum.css',
                autoGrow_minHeight: 50,
                stylesSet: false,
                toolbarGroups: [
                    { name: 'basicstyles', groups: [ 'basicstyles', 'cleanup' ] },
                    { name: 'paragraph',   groups: [ 'list', 'blocks', 'align' ] },
                    { name: 'styles', groups: [ 'FontSize' ] },
                    { name: 'colors' },
                    { name: 'links' },
                    { name: 'insert' },
                    { name: 'forms' },
                    { name: 'tools' },
                ],
                fontSize_sizes: "Маленький/85%;Нормальный/100%;Большой/150%;Огромный/200%",
                uploadUrl: '/api/ckeditor/images/',
            }
        }
    },
    mounted() {
        this.editorData = this.value;
        this.$refs.editor.instance.on('fileUploadRequest', function( evt ) {
            var xhr = evt.data.fileLoader.xhr;
            xhr.setRequestHeader("X-CSRFTOKEN", getCookie('csrftoken'));
        });
    },
    watch: {
		value(val) {
		    this.editorData = val;
        },
        editorData(val) {
            this.$emit( 'input', val );
        },
    },
});