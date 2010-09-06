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
				stylesheet: STATIC_URL + "css/xmlcolors_20100906.css",
				parserConfig: {
					useHTMLKludges: false
				},
				iframeClass: 'xml-iframe',
				textWrapping: true,
				lineNumbers: true,
				width: "100%",
				height: "100%",
				tabMode: 'spaces',
				indentUnit: 0,
				readOnly: CurrentDocument.readonly || false,
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

					$('#source-editor .toolbar').toolbarize({
					    actionContext: self.codemirror
					});

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
		this.config().position = this.codemirror.win.scrollY || 0;
	};

	CodeMirrorPerspective.prototype.unfreezeState = function () {
		this.codemirror.win.scroll(0, this.config().position || 0);
	};

	CodeMirrorPerspective.prototype.onEnter = function(success, failure) {
		$.wiki.Perspective.prototype.onEnter.call(this);

		console.log('Entering', this.doc);
		this.codemirror.setCode(this.doc.text);

		/* fix line numbers bar */
		var $nums = $('.CodeMirror-line-numbers');
	    var barWidth = $nums.width();

		$(this.codemirror.frame.contentDocument.body).css('padding-left', barWidth);
		// $nums.css('left', -barWidth);

		$(window).resize();
		this.unfreezeState(this._uistate);

		if(success) success();
	}

	CodeMirrorPerspective.prototype.onExit = function(success, failure) {
		this.freezeState();

		$.wiki.Perspective.prototype.onExit.call(this);
		console.log('Exiting', this.doc);
		this.doc.setText(this.codemirror.getCode());

        if ($('.vsplitbar').hasClass('active') && $('#SearchPerspective').hasClass('active')) {
            $.wiki.switchToTab('#ScanGalleryPerspective');
        }

		if(success) success();
	}

	$.wiki.CodeMirrorPerspective = CodeMirrorPerspective;

})(jQuery);
