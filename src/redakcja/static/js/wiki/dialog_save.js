/*
 * Dialog for saving document to the server
 *
 */
(function($) {

    class SaveDialog extends $.wiki.cls.GenericDialog {
        constructor(element, options) {
            let ctx = $.wiki.exitContext();
            super(element);
            this.ctx = ctx;
            this.clearForm();

            /* fill out hidden fields */
            this.$form = $('form', element);

            $("input[name='textsave-parent_revision']", this.$form).val(CurrentDocument.revision);
        }

        cancelAction() {
            $.wiki.enterContext(this.ctx);
            this.hide();
        }

        saveAction() {
            var self = this;

            self.$elem.block({
                message: "Zapisywanie... <br/><button id='save-hide'>ukryj</button>",
                fadeIn: 0,
            });
            $.wiki.blocking = self.$elem;

            try {

                CurrentDocument.save({
                    form: self.$form,
                    success: function(doc, changed, info){
                        self.$elem.block({
                            message: info,
                            timeout: 2000,
                            fadeOut: 0,
                            onUnblock: function() {
                                self.hide();
                                $.wiki.enterContext(self.ctx);
                            }
                        });
                    },
                    failure: function(doc, info) {
                        console.log("Failure", info);
                        self.reportErrors(info);
                        self.$elem.unblock();
                    }
                });
            } catch(e) {
                console.log('Exception:', e)
                self.$elem.unblock();
            }
        }
    }

    /* make it global */
    $.wiki.cls.SaveDialog = SaveDialog;
})(jQuery);
