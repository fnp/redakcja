(function($){
	
	function SummaryPerspective(options) {
		var old_callback = options.callback;        
        options.callback = function(){
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

