(function($) {
	const LEVEL_DEBUG = 1;
	const LEVEL_INFO = 2;
	const LEVEL_WARN = 3;

	const LOG_LEVEL = LEVEL_DEBUG;

	var mozillaLog = function() {
		if (window.console) console.log.apply(this, arguments);
	};

	var operaLog = function() {
		opera.postError.(arguments.join(' '));
	};

	var defaultLog = function() { return false; };

	$.log = function( ) {
		return $.log.browserLog.apply(this, arguments);
	};

	if ($.browser.mozilla || $.browser.safari)
		$.log.browserLog = mozillaLog;
	else if($.browser.opera)
		$.log.browserLog = operaLog
	else 
		$.log.browserLog = defaultLog;


})(jQuery);
