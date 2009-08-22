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
    
    $.fn.resizable = function(handle, options) {
        var settings = {
            minWidth: 0,
            maxWidth: $(window).width()
        }
        
        $.extend(settings, options);
        
        var element = $(this);
        
        $(handle, element).mousedown(function(event) {
            var position = element.position();
            $.resizable.settings = settings;
            $.resizable.element = {
                element: element,
                width: parseInt(element.css('width')) || element[0].scrollWidth || 0,
                mouseX: event.pageX,
            };
            $(document).mousemove($.resizable.drag).mouseup($.resizable.stop);
            $('body').css('cursor', 'col-resize');
        }).bind('dragstart', function(event) { event.preventDefault(); })
          .bind('drag', function(event) { event.preventDefault(); })
          .bind('draggesture', function(event) { event.preventDefault(); });
    };
})(jQuery);

