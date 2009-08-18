(function($) {
    $.fn.autoscroll = function(synchronizeWith, options) {
        var $this = $(this);
        var self = $this;
        var selfContainer = self.parent();
        var synchronizeWith = $(synchronizeWith);
        var synchronizeWithContainer = synchronizeWith.parent();
        var eventContainer = synchronizeWithContainer;

        // Hack for iframes
        if (self.is('iframe')) {
            selfContainer = $('body', $('iframe').contents());
            self = selfContainer;
        }
        
        if (synchronizeWith.is('iframe')) {
            eventContainer = synchronizeWith.contents();
            synchronizeWithContainer = $('body', eventContainer);
            synchronizeWith = synchronizeWithContainer;
        }
        
        $this.data('autoscroll:enabled', true);
        synchronizeWithContainer.data('autoscroll:lastCheckedScrollTop', synchronizeWithContainer.scrollTop());
        
        eventContainer.scroll(function() {
            if ($this.data('autoscroll:enabled')) {
                var distanceScrolled = synchronizeWithContainer.scrollTop() - synchronizeWithContainer.data('autoscroll:lastCheckedScrollTop');
                var percentScrolled = distanceScrolled / synchronizeWith.height();
                selfContainer.scrollTop(selfContainer.scrollTop() + percentScrolled * self.height());
            }
            synchronizeWithContainer.data('autoscroll:lastCheckedScrollTop', synchronizeWithContainer.scrollTop());
        });
    },
    
    $.fn.enableAutoscroll = function() {
        $(this).data('autoscroll:enabled', true);
    },
        
    $.fn.disableAutoscroll = function() {
        $(this).data('autoscroll:enabled', false);
    },
    
    $.fn.toggleAutoscroll = function() {
        $(this).data('autoscroll:enabled', !$(this).data('autoscroll:enabled'));
    }
})(jQuery);

