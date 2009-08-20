(function($){
    $.resizable = {
        element: {},
        drag: function(event) {
            $.resizable.element.element.css({
                width: Math.max(event.pageX - $.resizable.element.mouseX + $.resizable.element.width, 0)
            })
            $.resizable.element.element.trigger('resizable:resize');
            return false;
        },
        stop: function() {
            $.resizable.element.element.trigger('resizable:stop');
            $().unbind('mousemove', $.resizable.drag).unbind('mouseup', $.resizable.stop);
            return false;
        }
    };
    
    $.fn.resizable = function(handle) {
        var element = $(this);
        $(handle, element).mousedown(function(event) {
            var position = element.position();
            $.resizable.element = {
                element: element,
                width: parseInt(element.css('width')) || element[0].scrollWidth || 0,
                mouseX: event.pageX,
            };
            $().mousemove($.resizable.drag).mouseup($.resizable.stop);
        });
    };
})(jQuery);

