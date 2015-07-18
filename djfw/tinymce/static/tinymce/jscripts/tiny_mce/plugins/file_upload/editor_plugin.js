(function(tinymce) {
    tinymce.create('tinymce.plugins.FileUploadPlugin', {
        init : function(ed, url) {
            ed.addCommand('mceFileUpload', function() {
                ed.windowManager.open({
                    file : ed.getParam('fileupload_view_url',  
                        ed.getParam('base_dj_url', '/tinymce/') + 'uploaded_files/'),
                    width : 600,
                    height : 500,
                    inline : 1
                }, {
                    plugin_url : url,
                });
            });
            // Register buttons
            ed.addButton('file_upload', {cmd : 'mceFileUpload', image : url + '/img/icon.gif'});
        },
        getInfo : function() {
            return {
                longname : 'File uploads',
                author : 'kozzztik',
                authorurl : 'https://vk.com/kozzztik',
                infourl : '',
                version : tinymce.majorVersion + "." + tinymce.minorVersion
            };
        }
    });

    // Register plugin
    tinymce.PluginManager.add('file_upload', tinymce.plugins.FileUploadPlugin);
})(tinymce);