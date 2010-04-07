/* 
 * Dialog for saving document to the server
 * 
 */
(function($) {
	
	function SaveDialog(element) {
		$.wiki.cls.GenericDialog.call(this, element);
		this.ctx = $.wiki.exitContext();
	};
	
	SaveDialog.prototype = new $.wiki.cls.GenericDialog();
	
	SaveDialog.prototype 
	
	SaveDialog.prototype.saveAction = function() {
			var self = this;				
			
			self.$elem.block({
				message: "Zapisywanie..."
			});
			
			try {
				
				CurrentDocument.save({
					comment: $("#komentarz").text(),
					success: function(doc, changed, info){
						self.$elem.block({
							message: info,
							timeout: 1000,
							fadeOut: 0, 
							onUnblock: function() {															
								self.hide();
							}
						});
					},
					failure: function(doc, info) {
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
