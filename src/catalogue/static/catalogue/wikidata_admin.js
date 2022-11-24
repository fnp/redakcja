(function($) {
    $(function() {
    
        let model = $('body').attr('class').match(/model-([^\s]*)/)[1];
        $("#id_wikidata").each(show_wikidata_hints).on('change', show_wikidata_hints);

        function add_wikidata_hint($input, val) {
            if (val && val != $input.val()) {
                let already_set = false;
                let el = $('<span class="wikidata-hint">');

                if (val.wd) {
                    let iv = $input.val();
                    if (val.id) {
                        if (Array.isArray(iv)) {
                            if (iv.indexOf(val.id.toString()) != -1) {
                                already_set = true;
                            }
                        } else if (val.id == iv) {
                            already_set = true;
                        }
                    }

                    if (!already_set) {
                        // A representation of a WD Entity.
                        el.on('click', function() {
                            $(this).addClass('wikidata-processing');
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
                } else if (val.action == 'append') {
                    el.on('click', function() {
                        $input.val(
                            $input.val() + '\n' + val.value
                        );
                        $(this).remove();
                    });
                    el.text('+ ' + val.value);
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
        }
        
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

                            if (Array.isArray(val)) {
                                for (singleValue of val) {
                                    add_wikidata_hint($input, singleValue);
                                }
                            } else {
                                add_wikidata_hint($input, val);
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

            let req = new XMLHttpRequest();
            req.open("GET", url, true);
            req.responseType = "arraybuffer";
            req.onload = (event) => {
                let file = new File([req.response], filename);
                let container = new DataTransfer(); 
                container.items.add(file);
                $input[0].files = container.files;
                callback();
            };
            req.send(null);
        }
    });
})(jQuery);
