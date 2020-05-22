function wysibb_image_load() {
    this.$modal.find("#imguploader").dragfileupload({
        url: this.strf(this.options.img_uploadurl,this.options),
        extraParams: {
            maxwidth: this.options.img_maxwidth,
            maxheight: this.options.img_maxheight
        },
        themePrefix: this.options.themePrefix,
        themeName: this.options.themeName,
        success: $.proxy(function(data) {
            this.$txtArea.insertImage(data.image_link,data.thumb_link);
            this.closeModal();
            this.updateUI();
         },this)
    });

    if (!$.support.htmlSerialize) {
        //ie not posting form by security reason, show default file upload
        $.log("IE not posting form by security reason, show default file upload");
        this.$modal.find("#nicebtn").hide();
        this.$modal.find("#fileupl").css("opacity",1);
    }

    this.$modal.find("#fileupl").bind("change",function() {
        $("#fupform").submit();
    });

    this.$modal.find("#fupform").bind("submit",$.proxy(function(e) {
        $(e.target).parents("#imguploader").hide().after('<div class="loader"><img src="'+this.options.themePrefix+'/'+this.options.themeName+'/img/loader.gif" /><br/><span>'+CURLANG.loading+'</span></div>').parent().css("text-align","center");
        this.$modal.find("#fupform").ajaxSubmit({
            url: this.strf(this.options.img_uploadurl,this.options),
            success: $.proxy(function(data) {
                this.$txtArea.insertImage(data.image_link,data.thumb_link);
                this.closeModal();
                this.updateUI();
            },this),
            dataType: 'json'
        });
    },this))
}

$.fn.insertFileLink = function(fileurl,filename) {
    var editor = this.data("wbb");
    var code = editor.getCodeByCommand('link',{url:fileurl,seltext: filename})
    this.insertAtCursor(code);
    return editor;
}

function wysibb_file_load() {
    this.$modal.find("#fupfileform").ajaxSubmit({
        url: "/wysibb/upload_file/",
        success: $.proxy(function(data) {
            this.$txtArea.insertFileLink(data.url,data.filename);
            this.closeModal();
            this.updateUI();
        },this),
        dataType: 'json'
    });
}
