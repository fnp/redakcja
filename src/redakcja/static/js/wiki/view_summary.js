(function($){

	function SummaryPerspective(options) {
		var old_callback = options.callback || function() {};

		options.callback = function() {
			var self = this;

			// first time page is rendered
        	$('#summary-cover-refresh').click(function() {
				self.refreshCover();
			});

        	old_callback.call(this);
		}

		$.wiki.Perspective.call(this, options);
    };

    SummaryPerspective.prototype = new $.wiki.Perspective();

	SummaryPerspective.prototype.refreshCover = function() {
		$('#summary-cover-refresh').attr('disabled', 'disabled');
		this.doc.refreshCover({
			success: function(text) {
				$('#summary-cover').attr('src', text);
			$('#summary-cover-refresh').removeAttr('disabled');
			}
		});
	};

    SummaryPerspective.prototype.showCharCount = function() {
        var cc;
        try {
            cc = this.doc.getLength();
            $('#charcount_untagged').hide();
        }
        catch (e) {
            $('#charcount_untagged').show();
            cc = this.doc.text.replace(/\s{2,}/g, ' ').length;
        }
        $('#charcount').html(cc);
        $('#charcount_pages').html((Math.round(cc/18)/100).toLocaleString());
    }

    SummaryPerspective.prototype.freezeState = function(){
        // must
    };

	SummaryPerspective.prototype.onEnter = function(success, failure){
		$.wiki.Perspective.prototype.onEnter.call(this);
		
		this.showCharCount();

		console.log("Entered summery view");
	};

	$.wiki.SummaryPerspective = SummaryPerspective;

})(jQuery);

