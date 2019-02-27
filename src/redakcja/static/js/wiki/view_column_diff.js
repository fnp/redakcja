(function($){

	function DiffPerspective(options) {
		var old_callback = options.callback || function() {};
		var self = this;

        options.callback = function(){
			self.base_id = options.base_id;
			old_callback.call(this);
		};

		$.wiki.Perspective.call(this, options);
    };

    DiffPerspective.prototype = new $.wiki.Perspective();

    DiffPerspective.prototype.freezeState = function(){
        // must
    };

	DiffPerspective.prototype.destroy = function() {
        $.wiki.switchToTab('#HistoryPerspective');
		$('#' + this.base_id).remove();
		$('#' + this.perspective_id).remove();
	};

	DiffPerspective.prototype.onEnter = function(success, failure){
		$.wiki.Perspective.prototype.onEnter.call(this);
		console.log("Entered diff view");
	};

	$.wiki.DiffPerspective = DiffPerspective;

})(jQuery);

