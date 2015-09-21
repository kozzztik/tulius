$(document).ready(function() {
    $('.menu-background').on('click', function() {
        $('.menu-background').hide();
        $('.sub-menu').hide();
        $('.menu-list > li > a').removeClass('active')
    });

    $('ul.menu-list > li > a').on('click', function() {
         $('.menu-background').show();
         $('.sub-menu').hide();
         $('.menu-list > li > a').removeClass('active')
         var selector = this.attributes['data-toggle'].nodeValue;
         $(selector).show();
         $(this).addClass('active');
    });

    $('.scroll-up').click(function(){
       $('html, body').animate({scrollTop:0}, 800);
   });
    $('.scroll-down').click(function(){
        var $elem = $('body');
        $('html, body').animate({scrollTop: $elem.height()}, 800);
   });
});