(function($) {
    $(function() {
    
        let model = $('body').attr('class').match(/model-([^\s]*)/)[1];
        $("#id_wikidata").each(show_wikidata_hints).on('change', show_wikidata_hints);

        function show_wikidata_hints() {
            $(".wikidata-hint").remove();
            $wdinput = $(this);
            let qid = $wdinput.val();
            if (!qid) return;
            $wdinput.addClass('wikidata-processing');
            $.ajax(
                '/catalogue/wikidata/' + model + '/' + qid,
                {
                    success: function(result) {
                        for (att in result) {
                            let val = result[att];
                            let $input = $("#id_" + att);
                            if (val && val != $input.val()) {
                                let already_set = false;
                                let el = $('<span class="wikidata-hint">');

                                if (val.wd) {
                                    if (val.id && val.id == $input.val()) {
                                        already_set = true;
                                    } else {
                                        // A representation of a WD Entity.
                                        el.on('click', function() {
                                            set_value_from_wikidata_id(
                                                $input, val.model, val.wd,
                                                () => {$(this).remove();}
                                            );
                                        });
                                        el.text(val.label);
                                    }
                                } else if (val.img) {
                                    // A downloadable remote image.
                                    let img = $('<img height="32">');
                                    img.attr('src', val.img);
                                    el.append(img);
                                    el.on('click', function() {
                                        set_file_from_url(
                                            $input, val.download,
                                            () => {$(this).remove();}
                                        );
                                    });
                                } else {
                                    // A plain literal.
                                    el.on('click', function() {
                                        $input.val(val);
                                        $(this).remove();
                                    });
                                    el.text(val);
                                }
                                if (!already_set) {
                                    $input.parent().append(el);
                                }
                            }
                        };

                    },
                    complete: function() {
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
                    $input.append($('<option>').attr('value', result.id).text(result.__str__));                   
                    $input.val(result.id).trigger('change');
                    callback();
                },
            })
        }

        function set_file_from_url($input, url, callback) {
            filename = decodeURIComponent(url.match(/.*\/(.*)/)[1]);
            $.ajax({
                url: url,
                success: function(content) {
                    let file = new File([content], filename);
                    let container = new DataTransfer(); 
                    container.items.add(file);
                    $input[0].files = container.files;
                    callback()
                }
            });
        }
    });
})(jQuery);
