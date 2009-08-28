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

Panel.prototype.callHook = function() {
    args = $.makeArray(arguments)
    var hookName = args.splice(0,1)[0]
    var noHookAction = args.splice(0,1)[0]

	$.log('calling hook: ', hookName, 'with args: ', args);
	if(this.hooks && this.hooks[hookName])
	{	        
		return this.hooks[hookName].apply(this, args);
	}
    else if (noHookAction instanceof Function)
        return noHookAction(args);
    else return false;
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
    reload = function() {
    	$.log('hard reload for panel ', this.current_url);
    	this.load(this.current_url);
        return true;
    }

    if( this.callHook('refresh', reload) )
    	$('.change-notification', this.wrap).fadeOut();
} 

Panel.prototype.otherPanelChanged = function(other) {
	$.log('panel ', other, ' changed.');
	if(!this.callHook('dirty'))
        $('.change-notification', this.wrap).fadeIn();
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
	this.callHook('saveInfo', null, saveInfo);
	return saveInfo;
}


function Editor() {
	this.rootDiv = $('#panels');
}

Editor.prototype.setupUI = function() {
	// set up the UI visually and attach callbacks
	var self = this;
   
	self.rootDiv.makeHorizPanel({}); // TODO: this probably doesn't belong into jQuery
    self.rootDiv.css('top', ($('#header').outerHeight() ) + 'px');
    
	$('#panels > *.panel-wrap').each(function() {
		var panelWrap = $(this);
		$.log('wrap: ', panelWrap);
		panel = new Panel(panelWrap);
		panelWrap.data('ctrl', panel); // attach controllers to wraps
        panel.load($('.panel-toolbar select', panelWrap).val());
        
        $('.panel-toolbar select', panelWrap).change(function() {
            var url = $(this).val();
            panelWrap.data('ctrl').load(url);
            self.savePanelOptions();
        });
    });

	$(document).bind('panel:contentChanged', function(event, data) {
        $('#toolbar-button-save').removeAttr('disabled');
	});
    
    $('#toolbar-button-save').click( function (event, data) { self.saveToBranch(); } );
    self.rootDiv.bind('stopResize', function() { self.savePanelOptions() });
}

Editor.prototype.loadConfig = function() {
    // Load options from cookie
    var defaultOptions = {
        panels: [
            {name: 'htmleditor', ratio: 0.5},
            {name: 'gallery', ratio: 0.5}
        ]
    }
    
    try {
    	var cookie = $.cookie('options');
        this.options = $.secureEvalJSON(cookie);
        if (!this.options) {
            this.options = defaultOptions;
        }
    } catch (e) {    
        this.options = defaultOptions;
    }
    $.log(this.options);
    
    this.loadPanelOptions();
}

Editor.prototype.loadPanelOptions = function() {
    var self = this;
    var totalWidth = 0;
    
    $('.panel-wrap', self.rootDiv).each(function(index) {
        var panelWidth = self.options.panels[index].ratio * self.rootDiv.width();
        if ($(this).hasClass('last-panel')) {
            $(this).css({
                left: totalWidth,
                right: 0,
            });
        } else {
            $(this).css({
                left: totalWidth,
                width: panelWidth,
            });
            totalWidth += panelWidth;               
        }
        $.log('panel:', this, $(this).css('left'));
        $('.panel-toolbar select', this).val(
            $('.panel-toolbar option[name=' + self.options.panels[index].name + ']', this).attr('value')
        )
    });   
}

Editor.prototype.savePanelOptions = function() {
    var self = this;
    var panels = [];
    $('.panel-wrap', self.rootDiv).not('.panel-content-overlay').each(function() {
        panels.push({
            name: $('.panel-toolbar option:selected', this).attr('name'),
            ratio: $(this).width() / self.rootDiv.width()
        })
    });
    self.options.panels = panels;
    $.log($.toJSON(self.options));
    $.cookie('options', $.toJSON(self.options), { expires: 7, path: '/'});
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
            $('#toolbar-button-save').attr('disabled', 'disabled');
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
