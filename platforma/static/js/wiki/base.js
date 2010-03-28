(function($) 
{	
	$.wiki = {};
	
	$.wiki.Perspective = function(document, callback) {
		// initialization
	};
	
	$.wiki.Perspective.toString = function() {
		return this.perspective_id;
	}
	
	$.wiki.Perspective.prototype.onEnter = function () {
		// called when perspective in initialized
		if (this.perspective_id) {
			document.location.hash = '#' + this.perspective_id;
		}
			 
		console.log(document.location.hash);
	};
	
	$.wiki.Perspective.prototype.onExit = function () {
		// called when user switches to another perspective 
	};	 
	
	$.wiki.Perspective.prototype.freezeState = function () {
		// free UI state (don't store data here)
	};
	
	$.wiki.Perspective.prototype.unfreezeState = function (frozenState) {
		// restore UI state
	};
	
	$.wiki.renderStub = function($container, $stub, data) 
	{
		var $elem = $stub.clone();
		$elem.removeClass('row-stub');
		$container.append($elem);
	
		$('*[data-stub-value]', $elem).each(function() {
			var $this = $(this);
			var field = $this.attr('data-stub-value');
			var value = data[field];
		
			if(value === null || value === undefined) return;
			 
			if(!$this.attr('data-stub-target')) {
				$this.text(value);			
			} 		
			else {
				$this.attr($this.attr('data-stub-target'), value);
				$this.removeAttr('data-stub-target');
				$this.removeAttr('data-stub-value');			
			}		
		});
	
		$elem.show();
		return $elem;						
	};
		
})(jQuery);
