        $(document).ready(function() {
            $("#id_delete_voting").click(function() {
                if (this.checked) {
                    var t = $("#voting_container")[0];
                    $("#voting_container")[0].hidden = true
                } else {
                    var t = $("#voting_container")[0];
                    $("#voting_container")[0].hidden = false
                }
            });
        });