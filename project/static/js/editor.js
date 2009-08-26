function Panel(panelWrap) {
	var self = this;
	self.wrap = panelWrap;
	self.contentDiv = $('.panel-content', panelWrap);
	self.instanceId = Math.ceil(Math.random() * 1000000000);
	$.log('new panel - wrap: ', self.wrap);

	
	$(document).bind('panel:unload.' + self.instanceId, 
			function(event, data) { self.unload(event, data); });	

	$(document).bind('panel:contentChanged', function(event, data) {
		$.log(self, ' got changed event from: ', data);
		if(self != data) 
			self.otherPanelChanged(event.target);
		else 
			self.changed();

		return false; 		
	});

}

Panel.prototype.callHook = function(hookName) {
	if(this.hooks && this.hooks[hookName])
	{	
//		arguments.shift();
		$.log('calling hook: ', hookName, 'with args: ', arguments);
		this.hooks[hookName].apply(this, arguments);
	}
}

Panel.prototype.load = function (url) {
    $.log('preparing xhr load: ', this.wrap);
    $(document).trigger('panel:unload', this);
	var self = this;

    $.ajax({
        url: url,
        dataType: 'html',
		success: function(data, tstat) {
			panel_hooks = null;
			$(self.contentDiv).html(data);
			self.hooks = panel_hooks;			
			panel_hooks = null;
			self.callHook('load');
		},
        error: function(request, textStatus, errorThrown) {
            $.log('ajax', url, this.target, 'error:', textStatus, errorThrown);
        }
    });
}

Panel.prototype.unload = function(event, data) {
	$.log('got unload signal', this, ' target: ', data);

	if( data == this ) {
		$.log('unloading', this);
		$(document).unbind('panel:unload.' + this.instanceId);
        $(this.contentDiv).html('');
		this.callHook('unload');
		this.hooks = null; // flush the hooks
		return false;
    };
}

Panel.prototype.otherPanelChanged = function(other) {
	$.log('panel ', other, ' changed.');
	$('.change-notification', this.wrap).fadeIn();
	this.callHook('dirty');
}	

Panel.prototype.changed = function () {
	this.wrap.addClass('changed');
}

Panel.prototype.saveInfo = function() {
	var saveInfo = {};
	this.callHook('saveInfo', saveInfo);
	return saveInfo;
}


function Editor() {
	// editor initialization
	// this is probably a good place to set config
}

Editor.prototype.setupUI = function() {
	// set up the UI visually and attach callbacks
	var self = this;
	var panelRoot = $('#panels');

	panelRoot.makeHorizPanel({}); // TODO: this probably doesn't belong into jQuery
    panelRoot.css('top', ($('#header').outerHeight() ) + 'px');

	$('#panels > *.panel-wrap').each(function() {
		var panelWrap = $(this);
		$.log('wrap: ', panelWrap);
		panelWrap.data('ctrl', new Panel(panelWrap)); // attach controllers to wraps

	    $('.panel-toolbar select', panelWrap).change(function() {
			panelWrap.data('ctrl').load( $(this).val() );
	    });
	});	

	$('#toolbar-button-save').click( function (event, data) { self.saveToBranch(); } );


}

Editor.prototype.loadConfig = function() {
	// load options from cookie 
}

Editor.prototype.saveToBranch = function() {
	var changed_panel = $('.panel-wrap.changed');
	$.log('Saving to local branch - panel:', changed_panel);

	if( changed_panel.length == 0) {
		$.log('Nothing to save.');
		return; /* no changes */
	}

	if( changed_panel.length > 1) {
		alert('Błąd: więcej niż jeden panel został zmodyfikowany. Nie można zapisać.');
		return;
	}

	saveInfo = changed_panel.data('ctrl').saveInfo();

	$.ajax({
		url: location.href + (saveInfo.part || ''),
		dataType: (saveInfo.dataType || 'text'),
		success: function(data, textStatus) {
			$.log('Success:', data);
		},
		error: function(rq, tstat, err) {
		 	$.log('save error', rq, tstat, err);
		},
		type: 'POST',
		data: (saveInfo.content || '')
	});
};

$(function() {
	editor = new Editor();

	// do the layout
	editor.loadConfig();
	editor.setupUI();
});
