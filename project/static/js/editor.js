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
			self.markChanged();

		return false; 		
	});
}

Panel.prototype.callHook = function(hookName) {
	if(this.hooks && this.hooks[hookName])
	{	
//		arguments.shift();
		$.log('calling hook: ', hookName, 'with args: ', arguments);
		return this.hooks[hookName].apply(this, arguments);
	}
}

Panel.prototype.load = function (url) {
    $.log('preparing xhr load: ', this.wrap);
    $(document).trigger('panel:unload', this);
	var self = this;
	self.current_url = url;

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
        $(this.contentDiv).html('');
		this.callHook('unload');
		this.hooks = null; // flush the hooks
		return false;
    };
}

Panel.prototype.refresh = function(event, data) {
	$('.change-notification', this.wrap).fadeOut();
	$.log('refreshing view for panel ', this.current_url);
	this.load(this.current_url);
//	if( this.callHook('refresh') )
} 

Panel.prototype.otherPanelChanged = function(other) {
	$.log('panel ', other, ' changed.');
	$('.change-notification', this.wrap).fadeIn();
	this.callHook('dirty');
}	

Panel.prototype.markChanged = function () {
	if(!this.wrap.hasClass('changed') ) // TODO: is this needed ?
		this.wrap.addClass('changed');
}

Panel.prototype.changed = function () {
	return this.wrap.hasClass('changed');
}

Panel.prototype.unmarkChanged = function () {
	this.wrap.removeClass('changed');
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
	self.rootDiv = panelRoot;

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
	var self = this;
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
		url: saveInfo.url,
		dataType: 'json',
		success: function(data, textStatus) {
			if (data.result != 'ok')
				$.log('save errors: ', data.errors)
			else 
				self.refreshPanels(changed_panel);
		},
		error: function(rq, tstat, err) {
		 	$.log('save error', rq, tstat, err);
		},
		type: 'POST',
		data: saveInfo.postData
	});
};

Editor.prototype.refreshPanels = function(goodPanel) {
	var self = this;
	var panels = $('#' + self.rootDiv.attr('id') +' > *.panel-wrap', self.rootDiv.parent());

	panels.each(function() {
		var panel = $(this).data('ctrl');
		$.log(this, panel);
		if ( panel.changed() )
			panel.unmarkChanged();
		else 
			panel.refresh();
	});
};		

$(function() {
	editor = new Editor();

	// do the layout
	editor.loadConfig();
	editor.setupUI();
});
