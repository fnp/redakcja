(function($) {

    class CodeMirrorPerspective extends $.wiki.Perspective {
        constructor(options) {
            super(options);
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
        }

        onEnter(success, failure) {
            super.onEnter();
            this.codemirror.setValue(this.doc.text);
            this.codemirror.scrollTo(0, this.config().position || 0);

            if(success) success();
        }

        onExit(success, failure) {
            super.onExit();
            this.config().position =  this.codemirror.getScrollInfo().top;
            this.doc.setText(this.codemirror.getValue());

            $.wiki.exitTab('#SearchPerspective');

            if(success) success();
        }
    }

    $.wiki.CodeMirrorPerspective = CodeMirrorPerspective;

})(jQuery);
