(function($) {
    $(function() {
    
        let model = $('body').attr('class').match(/model-([^\s]*)/)[1];
        $("#id_wikidata").each(show_wikidata_hints).on('change', show_wikidata_hints);

        function show_wikidata_hints() {
            $(".wikidata-hint").remove();
            $wdinput = $(this);
            let qid = $wdinput.val();
            $wdinput.addClass('wikidata-processing');
            $.ajax(
                '/catalogue/wikidata/' + model + '/' + qid,
                {
                    success: function(result) {
                        for (att in result) {
                            let val = result[att];
                            let $input = $("#id_" + att);
                            if (val && val != $input.val()) {
                                let el = $('<span class="wikidata-hint">');
                                if (val.wd) {
                                    el.on('click', function() {
                                        set_value_from_wikidata_id(
                                            $input, val.model, val.wd,
                                            function() {
                                                $(this).remove();
                                            }
                                        );
                                    });
                                    el.text(val.label);
                                } else {
                                    el.on('click', function() {
                                        $input.val(val);
                                        $(this).remove();
                                    });
                                    el.text(val);
                                }
                                $input.parent().append(el);
                            }
                        };

                        $wdinput.removeClass('wikidata-processing');
                    },
                }
            );
        }

        function set_value_from_wikidata_id($input, model, wikidata_id, callback) {
            $.post({
                url: '/catalogue/wikidata/' + model + '/' + wikidata_id,
                data: {
                    csrfmiddlewaretoken: $('[name=csrfmiddlewaretoken]').val(),
                },
                success: function(result) {
                    $input.val(result.id);
                    callback();
                },
            })
        }
    });
})(jQuery);
