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

            tutorial = $.makeArray($('[data-toggle="tutorial"]').sort(
                function(a, b) {return $(a).attr('data-tutorial') < $(b).attr('data-tutorial') ? -1 : 1}
            ));

            if (first_reset) {
                $.each(tutorial, function(i, e) {
                    var but = (i < tutorial.length - 1) ? '>>' : 'OK';
                    $(e).popover({
                        title: 'Tutorial',
                        trigger: 'focus',
                        template: '<div class="popover" role="tooltip"><div class="arrow"></div><h3 class="popover-title"></h3><div class="popover-content"></div><div><a class="btn btn-default tutorial-off" href="#-" id="tutoff'+i+'">&times;</a><a style="float:right" class="btn btn-default tutorial-next" href="#-" id="nt'+i+'">' + but + '</a></div></div>'
                    }).on('shown.bs.popover', function () {
                        if (!$(e).data('tut-yet')) {
                            $("#tutoff"+i).on('click', tutoff);
                            $("#nt"+i).on('click', tut);
                            $(e).data('tut-yet', 'yes');
                        }
                    });
                    //$(start).on('hide.bs.popover', tut);
                });
                first_reset = false;
            }
        }
        
        function tuton() {
            sessionStorage.setItem("tutorial", "on");
            tutreset();
            $('#tutModal').modal('show');
            return false;
        }
        function tutoff() {
            if (start) $(start).popover('hide');
            start = null;
            sessionStorage.removeItem("tutorial");
            return false;
        }
        function tut() {
            if (start) $(start).popover('hide');
            if (tutorial.length) {
                start = tutorial.shift();
                $(start).popover('show');
                //~ if (!$(start).data('tut-yet')) {
                    //~ $(".popover .tutorial-off").on('click', tutoff);
                    //~ $(".popover .tutorial-next").on('click', tut);
                    //~ $(start).data('tut-yet', 'yes');
                //~ }
            }
            else {
                start = null;
            }
            return false;
        }
        $('#tutModal').on('hidden.bs.modal', tut);
        
        if (sessionStorage.getItem("tutorial") == "on" && $("#tuton").length == 0) {
            tutreset();
            tut();
        }
        $("#tuton").on('click', tuton);


    });
})(jQuery);

