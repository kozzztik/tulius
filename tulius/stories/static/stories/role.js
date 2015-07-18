        $(document).ready(function() {
            $("#id_character").click(function() {
                if (this.value!="") {
                    $("#id_name")[0].value = this.options[this.selectedIndex].label
                }
            });
        });