/*
 * Toolbar plugin.
 */
(function($) {

    $.fn.toolbarize = function(options) {
        var $toolbar = $(this);
        var $container = $('.button_group_container', $toolbar);

        $('.button_group button', $toolbar).click(function(event){
            event.preventDefault();

            var params = eval("(" + $(this).attr('data-ui-action-params') + ")");

            scriptletCenter.callInteractive({
                action: $(this).attr('data-ui-action'),
                context: options.actionContext,
                extra: params
            });
        });

        $('select', $toolbar).change(function(event){
            var slug = $(this).val();
            $container.scrollLeft(0);
            $('*[data-group]').hide().filter('[data-group="' + slug + '"]').show();
        }).change();

        $('button.next', $toolbar).click(function() {
            var $current_group = $('.button_group:visible', $toolbar);
            var scroll = $container.scrollLeft();

            var $hidden = $("li", $current_group).filter(function() {
                return ($(this).position().left + $(this).outerWidth()) > $container.width();
            }).first();

            if($hidden.length > 0) {
                scroll = $hidden.position().left + scroll + $hidden.outerWidth() - $container.width() + 1;
                $container.scrollLeft(scroll);
            };
        });

        $('button.prev', $toolbar).click(function() {
            var $current_group = $('.button_group:visible', $toolbar);
            var scroll = $container.scrollLeft();

            /* first not visible element is: */
            var $hidden = $("li", $current_group).filter(function() {
                return $(this).position().left < 0;
            }).last();

            if( $hidden.length > 0)
            {
                scroll = scroll + $hidden.position().left;
                $container.scrollLeft(scroll);
            };
        });

    };

})(jQuery);
