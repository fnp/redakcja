(function($) {
    $(function() {


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
        });


    });
})(jQuery)

