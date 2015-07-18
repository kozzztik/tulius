$(document).ready(function() {
    ;(function($) {
        $(".reqtooltip").each(function(index) {
            var t=$(this)[0];
            var request=(t.attributes['request'].nodeValue);
            var datacont=$("#req"+request);
            var data = datacont[0].innerHTML;
            $(this).popover({trigger: 'hover', content: data, placement: 'left', html: true});
            
        });
    })(jQuery);
});