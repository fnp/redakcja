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
                },
            }).on('changeDate', function(ev) {
                checkout.hide();
            }).data('datepicker');
        });


        $("select").change(function() {
            var helpdiv = $(this).next();
            if (helpdiv.hasClass('help-text')) {
                var helptext = $("option:selected", this).attr('data-help');
                helpdiv.html($("option:selected", this).attr('data-help') || '');
            }
        });



        // tutorial mode
        var tutorial;
        var start;

        var first_reset = true;
        function tutreset() {
            if (start) $(start).popover('hide');
            start = null;
            var all_tutorial = $('[data-toggle="tutorial"]');

            function sortKey(a) {
                return parseInt($(a).attr('data-tutorial'));
            }
            tutorial = $.makeArray(all_tutorial.sort(
                function(a, b) {return sortKey(a) < sortKey(b) ? -1 : 1}
            ));

            console.log($(tutorial[0]).data('popover'));
            console.log($(tutorial[16]).data('popover'));
            if (first_reset) {
                $.each(tutorial, function(i, e) {
                    var but = (i < tutorial.length - 1) ? '>>' : 'OK';
                    $(e).popover({
                        title: '<a class="btn btn-default tutorial-off" href="#-" id="tutoff'+i+'" style="float:right; padding:0 8px 4px 8px; position:relative; top:-6px; right:-10px;">&times;</a>Tutorial',
                        trigger: 'focus',
                        html: 'true',
                        template: '<div class="popover" role="tooltip"><div class="arrow"></div><h3 class="popover-title"></h3><div class="popover-content"></div><div><a style="float:right" class="btn btn-default tutorial-next" href="#-" id="nt'+i+'">' + but + '</a></div></div>'
                    });
                });
                first_reset = false;
            } else {
                all_tutorial.popover('enable');
            }
        }
        
        function tuton() {
            sessionStorage.setItem("tutorial", "on");
            tutreset();
            var $tutModal = $('#tutModal');
            if($tutModal.length === 0) {
                tut();
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
        function tut() {
            if (start) {
                $(start).popover('hide').popover('disable');
            }
            if (tutorial.length) {
                start = tutorial.shift();
                $(start).popover('show');
            }
            else {
                start = null;
            }
            return false;
        }
        $('#tutModal').on('hidden.bs.modal', tut);

        if (sessionStorage.getItem("tutorial") == "on" && $('#tuton').length == 0) {
            tutreset();
            tut();
        }
        $(document).on('click', '#tuton', tuton);
        $(document).on('click', '.tutorial-off', tutoff);
        $(document).on('click', '.tutorial-next', tut);
    });
})(jQuery);

