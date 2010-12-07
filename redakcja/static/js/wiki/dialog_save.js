/*
 * Dialog for saving document to the server
 *
 */
(function($) {

	function SaveDialog(element) {
		this.ctx = $.wiki.exitContext();
		this.clearForm();

		/* fill out hidden fields */
		this.$form = $('form', element);

		$("input[name='textsave-parent_revision']", this.$form).val(CurrentDocument.revision);

		$.wiki.cls.GenericDialog.call(this, element);
	};

	SaveDialog.prototype = new $.wiki.cls.GenericDialog();

	SaveDialog.prototype.cancelAction = function() {
		$.wiki.enterContext(this.ctx);
		this.hide();
	};

	SaveDialog.prototype.saveAction = function() {
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
	}; /* end of save dialog */

	/* make it global */
	$.wiki.cls.SaveDialog = SaveDialog;
})(jQuery);
