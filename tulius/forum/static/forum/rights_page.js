        $(document).ready(function() {
            var val = $("#id_access_type")[0].value
            
            if ((val==0)||(val==1)) {
                $("#tabs").tabs( "disable" , 1)
            } else {
                $("#tabs").tabs( "enable" , 1)
            }
                
            $("#id_access_type").click(function() {
                if ((this.value==0)||(this.value==1)) {
                    $("#tabs").tabs( "disable" , 1)
                } else {
                    $("#tabs").tabs( "enable" , 1)
                }
            });
        });