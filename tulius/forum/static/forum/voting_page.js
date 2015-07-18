        $(document).ready(function() {
            var val = $("#id_voting")[0].checked
            
            if (val) {
                $("#tabs").tabs( "enable" , 2)
            } else {
                $("#tabs").tabs( "disable" , 2)
            }
                
            $("#id_voting").click(function() {
                if (this.checked) {
                    $("#tabs").tabs( "enable" , 2)
                } else {
                    $("#tabs").tabs( "disable" , 2) 
                }
            });
            
            $("#id_show_results").click(function() {
                var isChecked = $("#id_show_results")[0].checked
                
                if (isChecked==false) {
                    $("#id_preview_results").attr("checked", false);
                }
            });

            $("#id_preview_results").click(function() {
                var isChecked = $("#id_preview_results")[0].checked
                
                if (isChecked) {
                    $("#id_show_results").attr("checked", true);
                }
            });
        });