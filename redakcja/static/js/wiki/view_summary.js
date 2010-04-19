(function($){

	function SummaryPerspective(options) {
		var old_callback = options.callback;
		var self = this;

        options.callback = function(){
			$('#publish_button').click(function() {
				$.blockUI({message: "Oczekiwanie na odpowiedź serwera..."});
				self.doc.publish({
					success: function(doc, data) {
						$.blockUI({message: "Udało się.", timeout: 2000});
					},
					failure: function(doc, message) {
						$.blockUI({
							message: message,
							timeout: 5000
						});
					}

				});
			});

			old_callback.call(this);
		};

		$.wiki.Perspective.call(this, options);
    };

    SummaryPerspective.prototype = new $.wiki.Perspective();

    SummaryPerspective.prototype.freezeState = function(){
        // must
    };

	SummaryPerspective.prototype.onEnter = function(success, failure){
		$.wiki.Perspective.prototype.onEnter.call(this);

		console.log("Entered summery view");
	};

	$.wiki.SummaryPerspective = SummaryPerspective;

})(jQuery);

