/*
 * Dialog for reverting document on the server
 *
 */
(function($) {

    class RevertDialog extends $.wiki.cls.GenericDialog {
        constructor(element, options) {
            let ctx = $.wiki.exitContext();
            super(element);
            this.ctx = ctx;
            this.clearForm();

            /* fill out hidden fields */
            this.$form = $('form', element);

            $("input[name='textrevert-revision']", this.$form).val(options.revision);
        }

        cancelAction() {
            $.wiki.enterContext(this.ctx);
            this.hide();
        };

        revertAction() {
            var self = this;

            self.$elem.block({
                message: "Przywracanie...",
                fadeIn: 0,
            });
            $.wiki.blocking = self.$elem;

            try {
                CurrentDocument.revertToVersion({
                    form: self.$form,
                    success: function(e, msg) {
                        self.$elem.block({
                            message: msg,
                            timeout: 2000,
                            fadeOut: 0,
                            onUnblock: function() {
                                self.hide();
                                $.wiki.enterContext(self.ctx);
                            }
                        });
                    },
                    'failure': function(e, info) {
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
    $.wiki.cls.RevertDialog = RevertDialog;
})(jQuery);
