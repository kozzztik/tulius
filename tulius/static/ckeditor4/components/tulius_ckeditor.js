import {LazyComponent} from '../../common/js/vue-common.js'
import axios from '../../common/js/axios.min.js';

var cached_smiley_response = {data: null};

export default LazyComponent('tulius_ckeditor', {
    template: '/static/ckeditor4/components/tulius_ckeditor.html',
    props: {
        value: {
            type: String
        },
        reply_form: {
            type: Boolean,
            default: false,
        },
    },
    data () {
        var data = {
            editorData: this.value,
            editorConfig: {
                language: 'ru',
                extraPlugins: 'autogrow,font,colorbutton,image,uploadimage,filebrowser,smiley,divarea',
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
        if (this.reply_form) {
            data.editorConfig.extraPlugins += ',replyformmax';
            data.editorConfig.removePlugins += ',maximize';
        }
        return data;
    },
    methods: {
        build_editor() {
            //this.editorData = this.value;
            this.editorConfig.smiley_path = cached_smiley_response.data.base_url;
            var file_names = [];
            var texts = [];
            var smile;
            for (smile of cached_smiley_response.data.smiles) {
                file_names.push(smile.file_name)
                texts.push(smile.text);
            }
            this.editorConfig.smiley_images = file_names;
            this.editorConfig.smiley_descriptions = texts;
            this.$refs.editor.build_editor();
            this.$refs.editor.instance.on('fileUploadRequest', function( evt ) {
                var xhr = evt.data.fileLoader.xhr;
                xhr.setRequestHeader("X-CSRFTOKEN", getCookie('csrftoken'));
            });
        }
    },
    mounted() {
        if (cached_smiley_response.data === null) {
            axios.get('/api/ckeditor/smiles/').then(response => {
                cached_smiley_response.data = response.data;
                this.build_editor();
            }).catch(error => this.$root.add_message(error, "error"));
        } else {
            this.build_editor();
        }
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