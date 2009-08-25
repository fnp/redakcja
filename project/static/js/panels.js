function Panel(target) {
	var self = this;
	this.target = target;
	this.instanceId = Math.ceil(Math.random() * 1000000000);
	$.log('new panel - target: ', this.target);
	$(document).bind('panel:unload.' + this.instanceId, 
			function(event, data) { self.unload(event, data); });	
}

Panel.prototype.load = function (url) {
    $.log('preparing xhr load: ', this.target);
    $('.change-notification', $(this.target).parent()).fadeOut();
    $(document).trigger('panel:unload', this.target);
	var self = this;

    $.ajax({
        url: url,
        dataType: 'html',
		success: function(data, tstat) {
			load_callback = unload_callback = null;
			$(self.target).html(data);
			self._onUnload = unload_callback;
			
			if(load_callback != null) {
				$.log('Invoking panel load callback.');
				load_callback(self);
			}
		},
        error: function(request, textStatus, errorThrown) {
            $.log('ajax', url, this.target, 'error:', textStatus, errorThrown);
        }
    });
}

Panel.prototype.unload = function(event, data) {
	$.log('got unload signal', this.target, ' target: ', data);
	if(this.target == data) {
		$(document).unbind('panel:unload.' + this.instanceId);
        $(this.target).html('');
		if(this._onUnload != null) this._onUnload(this);
		return false;
    };
}


/* 
 * Return the data that should be saved 
 */
Panel.prototype.saveData = function() {
	return "";
}


$(function() {
    $('#panels').makeHorizPanel({});
    $('#panels').css('top', ($('#header').outerHeight() ) + 'px');

	$('.panel-content').each(function() {
		var ctrl = new Panel(this);
		$(this).data('ctrl', ctrl);
	});
   	
    $('.panel-toolbar select').change(function() {
		var panel = $('.panel-content', $(this).parent().parent());
		$(panel).data('ctrl').load( $(this).val() );
    });
});
