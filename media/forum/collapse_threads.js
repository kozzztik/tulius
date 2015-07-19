$(document).ready(function() {
    ;(function($) {
        $(".thread_collapse").each(function(index) {
            var status = $(this).attr('status');
            if (status=="0") {
                this.innerHTML = "-";
            } else {
                $(this).parent().children(".forum-thread-list").hide();
                $(this).parent().children(".forum-room-list").hide();
                this.innerHTML = "+";
            }
            $(this).click(function() {
                var status = $(this).attr('status');
                var url = $(this).attr('href');
                var data = {};
                var items = $(this).parent().children(".forum-room-list");
                var data_str = "";
                
                if (items.length) {
                    data_str = "rooms";
                } else {
                    data_str = "threads";
                    items = $(this).parent().children(".forum-thread-list");
                }
                
                if (status=="0") {
                    status = "1"
                    this.innerHTML = "+";
                    items.hide();
                } else {
                    status = "0"
                    this.innerHTML = "-";
                    items.show();
                }
                $(this).attr('status', status)
                data[data_str] = status;
                
                $.ajax({
                    mode: "abort",
                    port: url,
                    dataType: "json",
                    type : "POST",
                    url: url,
                    data: data,
                });
                return false;
            });
        });
    })(jQuery);
});