/*
 * Dialog for reverting document on the server
 *
 */
(function($) {

    function RevertDialog(element, options) {
        this.ctx = $.wiki.exitContext();
        this.clearForm();

        /* fill out hidden fields */
        this.$form = $('form', element);

        $("input[name='textrevert-revision']", this.$form).val(options.revision);

        $.wiki.cls.GenericDialog.call(this, element);
    };

    RevertDialog.prototype = new $.wiki.cls.GenericDialog();

    RevertDialog.prototype.cancelAction = function() {
        $.wiki.enterContext(this.ctx);
        this.hide();
    };

    RevertDialog.prototype.revertAction = function() {
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
    }; /* end of revert dialog */

    /* make it global */
    $.wiki.cls.RevertDialog = RevertDialog;
})(jQuery);
