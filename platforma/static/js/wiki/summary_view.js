(function($){
	
	function SummaryPerspective(doc, callback) {
		this.perspective_id = 'SummaryPerspective';
		this.doc = doc;
		
		callback.call(this);
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

