(function($) {
	const LEVEL_DEBUG = 1;
	const LEVEL_INFO = 2;
	const LEVEL_WARN = 3;

	const LOG_LEVEL = LEVEL_DEBUG;

	var mozillaLog = function(msg) {
		if (console) console.log(msg);
	};

	var operaLog = function(msg) {
		opera.postError(msg);
	};

	var defaultLog = function(msg) { return false; };

	$.log = function(message, level) {
		if (level == null) level = LEVEL_INFO;
		if (message == null) message = 'TRACE';
		if (level < LOG_LEVEL)
			return false;

		return $.log.browserLog(message);
	};

	if ($.browser.mozilla || $.browser.safari)
		$.log.browserLog = mozillaLog;
	else if($.browser.opera)
		$.log.browserLog = operaLog
	else 
		$.log.browserLog = defaultLog;


})(jQuery);
