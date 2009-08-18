(function($) {
    $.fn.autoscroll = function(synchronizeWith, options) {
        var self = $(this);
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

        synchronizeWithContainer.data('autoscroll.lastCheckedScrollTop', synchronizeWithContainer.scrollTop());
        
        eventContainer.scroll(function() {
            var distanceScrolled = synchronizeWithContainer.scrollTop() - synchronizeWithContainer.data('autoscroll:lastCheckedScrollTop');
            var percentScrolled = distanceScrolled / synchronizeWith.height();
            selfContainer.scrollTop(selfContainer.scrollTop() + percentScrolled * self.height());
            synchronizeWithContainer.data('autoscroll:lastCheckedScrollTop', synchronizeWithContainer.scrollTop());
        });
    };
})(jQuery);

