/* COMMENT */
(function($) {
	
	function CodeMirrorPerspective(options) 
	{
		var old_callback = options.callback;        
        options.callback = function(){		
			var self = this;
			
			this.codemirror = CodeMirror.fromTextArea('codemirror_placeholder', {
				parserfile: 'parsexml.js',
				path: STATIC_URL + "js/lib/codemirror/",
				stylesheet: STATIC_URL + "css/xmlcolors_15032010.css",
				parserConfig: {
					useHTMLKludges: false
				},
				iframeClass: 'xml-iframe',
				textWrapping: true,
				lineNumbers: false,
				width: "100%",
				tabMode: 'spaces',
				indentUnit: 0,
				initCallback: function(){
					
					 self.codemirror.grabKeys(function(event) {			
						if (event.button) {
							$(event.button).trigger('click');
							event.button = null;
						}
					}, function(event) {
						/* CM reports characters 2 times - as event and as code */  
						if((typeof event) != "object")
							return false;
							
						if(!event.altKey)
							return false;	
						
						var c = String.fromCharCode(event.keyCode).toLowerCase();							
						var button = $("#source-editor button[data-ui-accesskey='"+c+"']");						
						if(button.length == 0)
							return false;
							
						/* it doesn't matter which button we pick - all do the same */
						event.button = button[0];
						return true; 									
					}); 
					
					$('#source-editor .toolbar button').click(function(event){
						event.preventDefault();
						var params = eval("(" + $(this).attr('data-ui-action-params') + ")");
						scriptletCenter.scriptlets[$(this).attr('data-ui-action')](self.codemirror, params);
					});
					
					$('.toolbar select').change(function(event){
						var slug = $(this).val();
						
						$('.toolbar-buttons-container').hide().filter('[data-group=' + slug + ']').show();
						$(window).resize();
					});
					
					$('.toolbar-buttons-container').hide();
					$('.toolbar select').change();
					
					console.log("Initialized CodeMirror");
					// textarea is no longer needed
					$('codemirror_placeholder').remove();
					old_callback.call(self);
				}
			});	
		};
		
		$.wiki.Perspective.call(this, options);
	};
	
	
	CodeMirrorPerspective.prototype = new $.wiki.Perspective();
	
	CodeMirrorPerspective.prototype.freezeState = function() {
		
	};
	
	CodeMirrorPerspective.prototype.onEnter = function(success, failure) {
		$.wiki.Perspective.prototype.onEnter.call(this);
	
		console.log('Entering', this.doc);
		this.codemirror.setCode(this.doc.text);
		if(success) success();
	}
	
	CodeMirrorPerspective.prototype.onExit = function(success, failure) {
		$.wiki.Perspective.prototype.onExit.call(this);
	
		console.log('Exiting', this.doc);
		this.doc.setText(this.codemirror.getCode());
		if(success) success();
	}
	
	$.wiki.CodeMirrorPerspective = CodeMirrorPerspective;
		
})(jQuery);
