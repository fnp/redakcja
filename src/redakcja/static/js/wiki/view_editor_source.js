(function($) {

    function CodeMirrorPerspective(options) {
	var old_callback = options.callback;
        options.callback = function(){
	    var self = this;

	    this.codemirror = CodeMirror.fromTextArea($(
                '#codemirror_placeholder').get(0), {
                    mode: 'xml',
                    lineWrapping: true,
		    lineNumbers: true,
		    readOnly: CurrentDocument.readonly || false,
                    identUnit: 0,
                });


	    $('#source-editor').keydown(function(event) {
		if(!event.altKey)
		    return;

		var c = event.key;
		var button = $("#source-editor button[data-ui-accesskey='"+c+"']");
		if(button.length == 0)
		    return;
                button.get(0).click();
                event.preventDefault();
	    });

	    $('#source-editor .toolbar').toolbarize({
		actionContext: self.codemirror
	    });

	    // textarea is no longer needed
	    $('#codemirror_placeholder').remove();
	    old_callback.call(self);
	}

        $.wiki.Perspective.call(this, options);
    };


    CodeMirrorPerspective.prototype = new $.wiki.Perspective();

    CodeMirrorPerspective.prototype.freezeState = function() {
        this.config().position =  this.codemirror.getScrollInfo().top;
    };

    CodeMirrorPerspective.prototype.unfreezeState = function () {
        this.codemirror.scrollTo(0, this.config().position || 0);
    };

	CodeMirrorPerspective.prototype.onEnter = function(success, failure) {
		$.wiki.Perspective.prototype.onEnter.call(this);

		this.codemirror.setValue(this.doc.text);

		this.unfreezeState(this._uistate);

		if(success) success();
	}

	CodeMirrorPerspective.prototype.onExit = function(success, failure) {
		this.freezeState();

		$.wiki.Perspective.prototype.onExit.call(this);
	    this.doc.setText(this.codemirror.getValue());

            if ($('.vsplitbar').hasClass('active') && $('#SearchPerspective').hasClass('active')) {
                $.wiki.switchToTab('#ScanGalleryPerspective');
            }

	    if(success) success();
	}

	$.wiki.CodeMirrorPerspective = CodeMirrorPerspective;

})(jQuery);
