(function($) {
	var LEVEL_DEBUG = 1;
	var LEVEL_INFO = 2;
	var LEVEL_WARN = 3;
	var LOG_LEVEL = LEVEL_DEBUG;
	
        var standardLog = function() {
            if (window.console)
                console.log.apply(console, arguments);
        };
    
	var operaLog = function() {
		opera.postError(arguments.join(' '));
	};

        var msieLog = function() {
            var args = $.makeArray(arguments);
            var vals = $.map(args, function(n) {
                try {
                    return JSON.stringify(n);
                } catch(e) {
                    return ('' + n);
                }
            });

            if (window.console)
                console.log(vals.join(" "));
        };

	$.log = function() {
		return $.log.browserLog.apply(this, arguments);
	};

        if($.browser.opera)
            $.log.browserLog = operaLog;
        else if($.browser.msie)
            $.log.browserLog = msieLog;
        else
            $.log.browserLog = standardLog;

})(jQuery);
