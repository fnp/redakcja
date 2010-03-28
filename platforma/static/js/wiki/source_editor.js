/* COMMENT */
(function($) {
	
	function CodeMirrorPerspective(doc, callback) 
	{
		this.perspective_id = 'CodeMirrorPerspective';
		this.doc = doc; // document model
		
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
			lineNumbers: true,
			width: "100%",
			tabMode: 'spaces',
			indentUnit: 0,
			initCallback: function() {
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
				callback.call(self);
			}	
		});
	};
	
	
	CodeMirrorPerspective.prototype = new $.wiki.Perspective();
	
	CodeMirrorPerspective.prototype.freezeState = function() {
		
	};
	
	CodeMirrorPerspective.prototype.onEnter = function(success, failure) {
		$.wiki.Perspective.prototype.onEnter.call(this);
	
		console.log(this.doc);
		this.codemirror.setCode(this.doc.text);
		if(success) success();
	}
	
	CodeMirrorPerspective.prototype.onExit = function(success, failure) {
		$.wiki.Perspective.prototype.onExit.call(this);
	
		console.log(this.doc);
		this.doc.setText(this.codemirror.getCode());
		if(success) success();
	}
	
	$.wiki.CodeMirrorPerspective = CodeMirrorPerspective;
		
})(jQuery);
