(function($){

    class DiffPerspective extends $.wiki.Perspective {
        constructor(options) {
	    var old_callback = options.callback || function() {};

            options.callback = function() {
	        var self = this;
		self.base_id = options.base_id;
		old_callback.call(this);
	    };
	    super(options);
        }

        freezeState() {
            // must
        };

	destroy() {
            $.wiki.switchToTab('#HistoryPerspective');
            $('#' + this.base_id).remove();
            $('#' + this.perspective_id).remove();
	}
    }
    $.wiki.DiffPerspective = DiffPerspective;

})(jQuery);

