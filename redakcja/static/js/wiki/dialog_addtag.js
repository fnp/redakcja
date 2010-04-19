/*
 * Dialog for saving document to the server
 *
 */
(function($){

    function AddTagDialog(element, options){
        if (!options.revision  && options.revision != 0)
            throw "AddTagDialog needs a revision number.";

        this.ctx = $.wiki.exitContext();
        this.clearForm();

        /* fill out hidden fields */
        this.$form = $('form', element);

        $("input[name='addtag-id']", this.$form).val(CurrentDocument.id);
        $("input[name='addtag-revision']", this.$form).val(options.revision);

        $.wiki.cls.GenericDialog.call(this, element);
    };

    AddTagDialog.prototype = $.extend(new $.wiki.cls.GenericDialog(), {
        cancelAction: function(){
            $.wiki.enterContext(this.ctx);
            this.hide();
        },

        saveAction: function(){
            var self = this;

            self.$elem.block({
                message: "Dodawanie tagu",
                fadeIn: 0,
            });

            CurrentDocument.setTag({
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
    });

    /* make it global */
    $.wiki.cls.AddTagDialog = AddTagDialog;
})(jQuery);
