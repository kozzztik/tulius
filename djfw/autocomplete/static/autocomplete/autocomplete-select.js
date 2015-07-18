;(function($) {
    
$.fn.extend({
    autocomplete_original_input: function() {
        var t = $(this);
        var id = t[0].attributes['id'].nodeValue;
        var new_id = id.replace(/_autocomplete/g, "");
        var orig = $('[id=' + new_id + ']');
        return orig[0];
    },
    autocomplete_select: function(event, ui) {
        var orig = $(this).autocomplete_original_input();
        orig.value=ui.item.real_value;
    },
    autocomplete_change: function( event, ui ) {
        if ( !ui.item ) {
            // remove invalid value, as it didn't match anything
            $(this)[0].value="";
            var orig = $(this).autocomplete_original_input();
            orig.value="";
            return false;
        }
    },

});

})(jQuery);