(function($) {
    $(function() {

        $(".admin-woblink").on("select2:open", function(e) {
            console.log("TRIGGER", e);
            let $input = $(".select2-container--open input");
            let fname = $("#id_first_name_pl").val() || '';
            let lname = $("#id_last_name_pl").val() || '';
            $input.val(
                (fname + ' ' + lname).trim()
            ).trigger('input');
        });

        $(".admin-woblink").on("select2:select", function(e) {
            $('.fieldBox.field-woblink_link div').empty().append($('<a href="https://woblink.com/autor/-' + e.params.data.id + '" target="_blank">Podgląd</a>'));

        });


    });
})(jQuery);
