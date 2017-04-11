(function($) {
    $(function() {


        $('.filter').change(function() {
            document.filter[this.name].value = this.value;
            document.filter.submit();
        });

        $('.check-filter').change(function() {
            document.filter[this.name].value = this.checked ? '1' : '';
            document.filter.submit();
        });

        $('.text-filter').each(function() {
            var inp = this;
            $(inp).parent().submit(function() {
                document.filter[inp.name].value = inp.value;
                document.filter.submit();
                return false;
            });
        });


        $('.autoslug-source').change(function() {
            $('.autoslug').attr('value', slugify(this.value));
        });


        var nowTemp = new Date();
        var now = new Date(nowTemp.getFullYear(), nowTemp.getMonth(), nowTemp.getDate(), 0, 0, 0, 0);

        $('.datepicker-field').each(function() {
            var checkout = $(this).datepicker({
                format: 'yyyy-mm-dd',
                weekStart: 1,
                onRender: function(date) {
                    return date.valueOf() < now.valueOf() ? 'disabled' : '';
                }
            }).on('changeDate', function() {
                checkout.hide();
            }).data('datepicker');
        });


        $("select").change(function() {
            var helpdiv = $(this).next();
            if (helpdiv.hasClass('help-text')) {
                var helptext = $("option:selected", this).attr('data-help');
                helpdiv.html(helptext || '');
            }
        });

        $('.chosen-select').chosen().each(function() {
            var widget = $(this.nextSibling), $t = $(this);
            $.each($.merge([], this.attributes), function() {
                if (this.name.substr(0, 5) === 'data-') {
                    $t.removeAttr(this.name);
                    widget.attr(this.name, this.value);
                }
            });
        });



        // tutorial mode
        var tutorial, tutorial_no;
        var start;

        var first_reset = true;
        function tutreset() {
            if (start) $(start).popover('hide');
            start = null;
            tutorial_no = null;
            var all_tutorial = $('[data-toggle="tutorial"]');

            function sortKey(a) {
                return parseInt($(a).attr('data-tutorial'));
            }
            tutorial = $.makeArray(all_tutorial.sort(
                function(a, b) {return sortKey(a) < sortKey(b) ? -1 : 1}
            ));

            if (first_reset) {
                $.each(tutorial, function(i, e) {
                    var but = (i < tutorial.length - 1) ? '>>' : 'OK',
                        but_prev_html = i === 0 ? '' : '<a class="btn btn-default tutorial-prev" href="#-" id="pv'+i+'">&lt;&lt;</a></div></div>';
                    $(e).popover({
                        title: '<a class="btn btn-default tutorial-off" href="#-" id="tutoff'+i+'" style="float:right; padding:0 8px 4px 8px; position:relative; top:-6px; right:-10px;">&times;</a>Tutorial',
                        trigger: 'focus',
                        html: 'true',
                        template: '<div class="popover" role="tooltip"><div class="arrow"></div><h3 class="popover-title"></h3><div class="popover-content"></div><div><a style="float:right" class="btn btn-default tutorial-next" href="#-" id="nt'+i+'">' + but + '</a>' + but_prev_html + '</div></div>'
                    });
                    $(e).popover('disable');
                });
                first_reset = false;
            }
        }
        
        function tuton() {
            sessionStorage.setItem("tutorial", "on");
            tutreset();
            var $tutModal = $('#tutModal');
            if($tutModal.length === 0) {
                tutnext();
            } else {
                $tutModal.modal('show');
            }
            return false;
        }
        function tutoff() {
            $(this).popover('hide');
            if (start) $(start).popover('hide');
            start = null;
            sessionStorage.removeItem("tutorial");
            $('[data-toggle="tutorial"]').popover('disable');
            return false;
        }
        function tut(next) {
            if (start) {
                $(start).popover('hide').popover('disable');
            }
            if (tutorial_no === null)
                tutorial_no = 0;
            else if (next)
                tutorial_no++;
            else
                tutorial_no--;
            if (tutorial_no < tutorial.length && tutorial_no >= 0) {
                start = tutorial[tutorial_no];
                $(start).popover('enable').popover('show');
            }
            else {
                tutorial_no = null;
                start = null;
            }
            return false;
        }
        function tutnext() {
            tut(true);
        }
        function tutprev() {
            tut(false);
        }
        $('#tutModal').on('hidden.bs.modal', tutnext);

        if (sessionStorage.getItem("tutorial") === "on" && $('#tuton').length === 0) {
            tutreset();
            tutnext();
        }
        $(document).on('click', '#tuton', tuton);
        $(document).on('click', '.tutorial-off', tutoff);
        $(document).on('click', '.tutorial-next', tutnext);
        $(document).on('click', '.tutorial-prev', tutprev);
    });
})(jQuery);

