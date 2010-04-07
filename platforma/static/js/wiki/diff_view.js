(function($){
	
	function DiffPerspective(options) {
		var old_callback = options.callback || function() {};        
        options.callback = function(){
			old_callback.call(this);
		};		
		
		$.wiki.Perspective.call(this, options);
    };
    
    DiffPerspective.prototype = new $.wiki.Perspective();
    
    DiffPerspective.prototype.freezeState = function(){
        // must 
    };
	
	DiffPerspective.prototype.onEnter = function(success, failure){
		$.wiki.Perspective.prototype.onEnter.call(this);
		
		console.log("Entered diff view");
	};
	
	$.wiki.DiffPerspective = DiffPerspective;
	
})(jQuery);

