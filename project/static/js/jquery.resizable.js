(function($){
    $.resizable = {
        settings: {},
        element: {},
        drag: function(event) {
            $.resizable.element.element.css({
                width: Math.max(event.pageX - $.resizable.element.mouseX + $.resizable.element.width, 
                    $.resizable.settings.minWidth)
            })
            $.resizable.element.element.trigger('resizable:resize');
            return false;
        },
        stop: function(event) {
            $.resizable.element.element.trigger('resizable:stop');
            $(document).unbind('mousemove', $.resizable.drag).unbind('mouseup', $.resizable.stop)
            $('body').css('cursor', 'auto');
            return false;
        }
    };
    
    $.fn.resizable = function(options) {
        var settings = {
            minWidth: 0,
            maxWidth: $(window).width()
        }
        
        $.extend(settings, options);
        
        var element = $(this);
		var handle = $('.panel-slider', element)
        
        handle.mousedown(function(event) {
            var position = element.position();
			console.log('Mouse down on position: ' + position);
			/* from this point on, the panel should resize events */

            /* $.resizable.settings = settings;
            $.resizable.data = {
                element: element,
                width: parseInt(element.css('width')) || element[0].scrollWidth || 0,
                mouseX: event.pageX,
            }; */

            $(document).mousemove($.resizable.ondrag, element).mouseup($.resizable.stop, element);
            /* $('body').css('cursor', 'col-resize'); */
        });

		/* stop drag events */
		handle.bind('dragstart', function(event) { event.preventDefault(); })
          .bind('drag', function(event) { event.preventDefault(); })
          .bind('draggesture', function(event) { event.preventDefault(); });
    };
})(jQuery);

