/*
 * Dialog for marking document for publishing
 *
 */
(function($){

    class PubmarkDialog extends $.wiki.cls.GenericDialog {
        constructor(element, options) {
            if (!options.revision  && options.revision != 0)
                throw "PubmarkDialog needs a revision number.";

            super(element);
            this.ctx = $.wiki.exitContext();
            this.clearForm();

            /* fill out hidden fields */
            this.$form = $('form', element);

            $("input[name='pubmark-id']", this.$form).val(CurrentDocument.id);
            $("input[name='pubmark-revision']", this.$form).val(options.revision);

        }

        cancelAction() {
            $.wiki.enterContext(this.ctx);
            this.hide();
        }

        saveAction() {
            var self = this;

            self.$elem.block({
                message: "Oznaczanie wersji",
                fadeIn: 0,
            });

            CurrentDocument.pubmark({
                form: self.$form,
                success: function(doc, changed, info){
                    self.$elem.block({
                        message: info,
                        timeout: 2000,
                        fadeOut: 0,
                        onUnblock: function(){
                            self.hide();
                            $.wiki.enterContext(self.ctx);
                        }
                    });
                },
                failure: function(doc, info){
                    console.log("Failure", info);
                    self.reportErrors(info);
                    self.$elem.unblock();
                }
            });
        }
    }

    /* make it global */
    $.wiki.cls.PubmarkDialog = PubmarkDialog;
})(jQuery);
