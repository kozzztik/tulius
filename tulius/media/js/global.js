// lightbox for every image link
//$(function () {
//    $('a[rel*=lightbox]')
//        .lightBox(
//        {
//            fixedNavigation:    true,
//            imageLoading:	    '/media/jquery-lightbox/images/lightbox-ico-loading.gif',
//            imageBtnPrev:		'/media/jquery-lightbox/images/lightbox-btn-prev.gif',
//            imageBtnNext:		'/media/jquery-lightbox/images/lightbox-btn-next.gif',
//            imageBtnClose:		'/media/jquery-lightbox/images/lightbox-btn-close.gif',
//            imageBlank:			'/media/jquery-lightbox/images/lightbox-blank.gif'
//        }
//    );
//});

//// catalog widget categories extending/collapsing
//$(function () {
//	$('.catalog_widget ul li.extendable.collapsing_toggler').click(function () {
//		var $li = $(this);
//		$li.toggleClass('extended').toggleClass('collapsed');
//		return false;
//	}).find('a').click(function (event) {
//		event.stopPropagation();
//	});
//});

$(function () {
    if ($('#flatpages-dropdown li').size()) {
        $('#flatpages-dropdown-toggler').attr('href', '#');
    }
    $('#auth-dropdown-toggler').attr('href', '#');
});

$(function() {
    $('#theme_selection_modal select').bind('change', function () {
        var $select = $(this);
        var selected_theme = $select.val();
        var $css_link = $('#theme_css_link');
        $css_link.attr('href', $css_link.attr('data-theming_url') + selected_theme + '/main.css');
        $.cookie('theme', selected_theme, { expires: 7, path: '/' });
    });
});

//$(function() {
//    if (jQuery.fn.wysihtml5) {
//        $('.extended_wysiwyg').find('textarea').wysihtml5()
//    }
//});

//$(function () {
//    $(".multiselect").twosidedmultiselect();
//});