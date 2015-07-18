tinyMCEPopup.requireLangPack();

var FileUploadDialog = {
    addKeyboardNavigation: function(){
        var tableElm, cells, settings;
            
        cells = tinyMCEPopup.dom.select("a.file_link", "#files_table");
            
        settings ={
            root: "files_table",
            items: cells
        };
        cells[0].tabindex=0;
        tinyMCEPopup.dom.addClass(cells[0], "mceFocus");
        if (tinymce.isGecko) {
            cells[0].focus();       
        } else {
            setTimeout(function(){
                cells[0].focus();
            }, 100);
        }
        tinyMCEPopup.editor.windowManager.createInstance('tinymce.ui.KeyboardNavigation', settings, tinyMCEPopup.dom);
    }, 
    init : function(ed) {
        tinyMCEPopup.resizeToInnerSize();
        this.addKeyboardNavigation();
    },

    insert : function(file_path, isImage, filename) {
        var ed = tinyMCEPopup.editor;
        if (isImage) {
            tinyMCEPopup.execCommand('mceInsertContent', false, '<img src="' + file_path +
                '" alt="' + filename + '" />');
        } else {
            tinyMCEPopup.execCommand('mceInsertContent', false, '<a href="'+ file_path +
                '>' + filename + '</a>');
            
        }
        tinyMCEPopup.close();
    }
};

tinyMCEPopup.onInit.add(FileUploadDialog.init, FileUploadDialog);
