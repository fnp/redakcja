function Panel(panelWrap) {
    var self = this;
    self.hotkeys = [];
    self.wrap = panelWrap;
    self.contentDiv = $('.panel-content', panelWrap);
    self.instanceId = Math.ceil(Math.random() * 1000000000);
    $.log('new panel - wrap: ', self.wrap);
	
    $(document).bind('panel:unload.' + self.instanceId,
        function(event, data) {
            self.unload(event, data);
        });

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
    var args = $.makeArray(arguments)
    var hookName = args.splice(0,1)[0]
    var noHookAction = args.splice(0,1)[0]
    var result = false;

    $.log('calling hook: ', hookName, 'with args: ', args);
    if(this.hooks && this.hooks[hookName])
        result = this.hooks[hookName].apply(this, args);
    else if (noHookAction instanceof Function)
        result = noHookAction(args);
    return result;
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
            self.connectToolbar();
            self.callHook('load');
            self.callHook('toolbarResized');
        },
        error: function(request, textStatus, errorThrown) {
            $.log('ajax', url, this.target, 'error:', textStatus, errorThrown);
            $(self.contentDiv).html("<p>Wystapił błąd podczas wczytywania panelu.");
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
    var self = this;
    reload = function() {
        $.log('hard reload for panel ', self.current_url);
        self.load(self.current_url);
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

Panel.prototype.connectToolbar = function()
{
    var self = this;
    self.hotkeys = [];
    
    // check if there is a one
    var toolbar = $("div.toolbar", this.contentDiv);
    $.log('Connecting toolbar', toolbar);
    if(toolbar.length == 0) return;

    // connect group-switch buttons
    var group_buttons = $('*.toolbar-tabs-container button', toolbar);

    $.log('Found groups:', group_buttons);

    group_buttons.each(function() {
        var group = $(this);
        var group_name = group.attr('ui:group');
        $.log('Connecting group: ' + group_name);

        group.click(function() {
            // change the active group
            var active = $("*.toolbar-tabs-container button.active", toolbar);
            if (active != group) {
                active.removeClass('active');                
                group.addClass('active');
                $(".toolbar-button-groups-container p", toolbar).each(function() {
                    if ( $(this).attr('ui:group') != group_name) 
                        $(this).hide();
                    else
                        $(this).show();
                });
                self.callHook('toolbarResized');
            }
        });        
    });

    // connect action buttons
    var action_buttons = $('*.toolbar-button-groups-container button', toolbar);
    action_buttons.each(function() {
        var button = $(this);
        var hk = button.attr('ui:hotkey');

        var callback = function() {
           editor.callScriptlet(button.attr('ui:action'),
                self, eval(button.attr('ui:action-params')) );
        };

        // connect button
        button.click(callback);
        
        // connect hotkey
        if(hk) self.hotkeys[parseInt(hk)] = callback;

        // tooltip
        if (button.attr('ui:tooltip') )
        {
            var tooltip = button.attr('ui:tooltip');
            if(hk) tooltip += ' [Alt+'+hk+']';

            button.wTooltip({
                delay: 1000,
                style: {
                    border: "1px solid #7F7D67",
                    opacity: 0.9,
                    background: "#FBFBC6",
                    padding: "1px",
                    fontSize: "12px"
                },
                content: tooltip
            });
        }
    });
}

Panel.prototype.hotkeyPressed = function(event)
{
    var callback = this.hotkeys[event.keyCode];
    if(callback) callback();
}

Panel.prototype.isHotkey = function(event) {
    if( event.altKey && (this.hotkeys[event.keyCode] != null) )
        return true;
    return false;
}

//
Panel.prototype.fireEvent = function(name) {
    $(document).trigger('panel:'+name, this);
}

function Editor()
{
    this.rootDiv = $('#panels');
    this.popupQueue = [];
    this.autosaveTimer = null;
    this.scriplets = {};
}

Editor.prototype.setupUI = function() {
    // set up the UI visually and attach callbacks
    var self = this;
   
    self.rootDiv.makeHorizPanel({}); // TODO: this probably doesn't belong into jQuery
    // self.rootDiv.css('top', ($('#header').outerHeight() ) + 'px');
    
    $('#panels > *.panel-wrap').each(function() {
        var panelWrap = $(this);
        $.log('wrap: ', panelWrap);
        var panel = new Panel(panelWrap);
        panelWrap.data('ctrl', panel); // attach controllers to wraps
        panel.load($('.panel-toolbar select', panelWrap).val());
        
        $('.panel-toolbar select', panelWrap).change(function() {
            var url = $(this).val();
            panelWrap.data('ctrl').load(url);
            self.savePanelOptions();
        });

        $('.panel-toolbar button.refresh-button', panelWrap).click(
            function() { 
                panel.refresh();
            } );
    });

    $(document).bind('panel:contentChanged', function() {
        self.onContentChanged.apply(self, arguments)
    });
    
    $('#toolbar-button-save').click( function (event, data) { 
        self.saveToBranch();
    } );
    $('#toolbar-button-commit').click( function (event, data) { 
        self.sendPullRequest();
    } );
    self.rootDiv.bind('stopResize', function() { 
        self.savePanelOptions()
    });
}

Editor.prototype.loadConfig = function() {
    // Load options from cookie
    var defaultOptions = {
        panels: [
        {
            name: 'htmleditor',
            ratio: 0.5
        },

        {
            name: 'gallery',
            ratio: 0.5
        }
        ],
        lastUpdate: 0
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
                right: 0
            });
        } else {
            $(this).css({
                left: totalWidth,
                width: panelWidth
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
    self.options.lastUpdate = (new Date()).getTime() / 1000;
    $.log($.toJSON(self.options));
    $.cookie('options', $.toJSON(self.options), {
        expires: 7,
        path: '/'
    });
}

Editor.prototype.saveToBranch = function(msg) 
{
    var changed_panel = $('.panel-wrap.changed');
    var self = this;
    $.log('Saving to local branch - panel:', changed_panel);

    if(!msg) msg = "Zapis z edytora platformy.";

    if( changed_panel.length == 0) {
        $.log('Nothing to save.');
        return true; /* no changes */
    }

    if( changed_panel.length > 1) {
        alert('Błąd: więcej niż jeden panel został zmodyfikowany. Nie można zapisać.');
        return false;
    }

    saveInfo = changed_panel.data('ctrl').saveInfo();
    var postData = ''
    
    if(saveInfo.postData instanceof Object)
        postData = $.param(saveInfo.postData);
    else
        postData = saveInfo.postData;

    postData += '&' + $.param({
        'commit_message': msg
    })

    $.ajax({
        url: saveInfo.url,
        dataType: 'json',
        success: function(data, textStatus) {
            if (data.result != 'ok')
                self.showPopup('save-error', data.errors[0]);
            else {
                self.refreshPanels(changed_panel);
                $('#toolbar-button-save').attr('disabled', 'disabled');
                $('#toolbar-button-commit').removeAttr('disabled');
                if(self.autosaveTimer)
                    clearTimeout(self.autosaveTimer);

                self.showPopup('save-successful');
            }
        },
        error: function(rq, tstat, err) {
            self.showPopup('save-error');
        },
        type: 'POST',
        data: postData
    });

    return true;
};

Editor.prototype.autoSave = function() 
{
    this.autosaveTimer = null;
    // first check if there is anything to save
    $.log('Autosave');
    this.saveToBranch("Automatyczny zapis z edytora platformy.");
}

Editor.prototype.onContentChanged = function(event, data) {
    var self = this;

    $('#toolbar-button-save').removeAttr('disabled');
    $('#toolbar-button-commit').attr('disabled', 'disabled');
    
    if(this.autosaveTimer) return;
    this.autosaveTimer = setTimeout( function() {
        self.autoSave();
    }, 300000 );
};

Editor.prototype.refreshPanels = function(goodPanel) {
    var self = this;
    var panels = $('#' + self.rootDiv.attr('id') +' > *.panel-wrap', self.rootDiv.parent());

    panels.each(function() {
        var panel = $(this).data('ctrl');
        $.log('Refreshing: ', this, panel);
        if ( panel.changed() )
            panel.unmarkChanged();
        else
            panel.refresh();
    });
};		


Editor.prototype.sendPullRequest = function () {
    if( $('.panel-wrap.changed').length != 0)        
        alert("There are unsaved changes - can't make a pull request.");

    this.showPopup('not-implemented');
/*
	$.ajax({
		url: '/pull-request',
		dataType: 'json',
		success: function(data, textStatus) {
            $.log('data: ' + data);
		},
		error: function(rq, tstat, err) {
		 	$.log('commit error', rq, tstat, err);
		},
		type: 'POST',
		data: {}
	}); */
}

Editor.prototype.showPopup = function(name, text) 
{
    var self = this;
    self.popupQueue.push( [name, text] )

    if( self.popupQueue.length > 1) 
        return;

    var box = $('#message-box > #' + name);
    $('*.data', box).html(text);
    box.fadeIn();
 
    self._nextPopup = function() {
        var elem = self.popupQueue.pop()
        if(elem) {
            var box = $('#message-box > #' + elem[0]);

            box.fadeOut(300, function() {
                $('*.data', box).html();
    
                if( self.popupQueue.length > 0) {
                    box = $('#message-box > #' + self.popupQueue[0][0]);
                    $('*.data', box).html(self.popupQueue[0][1]);
                    box.fadeIn();
                    setTimeout(self._nextPopup, 5000);
                }
            });
        }
    }

    setTimeout(self._nextPopup, 5000);
}

Editor.prototype.registerScriptlet = function(scriptlet_id, scriptlet_func)
{
    // I briefly assume, that it's verified not to break the world on SS
    if (!this[scriptlet_id])
        this[scriptlet_id] = scriptlet_func;
}

Editor.prototype.callScriptlet = function(scriptlet_id, panel, params) {
    var func = this[scriptlet_id]
    if(!func)
        throw 'No scriptlet named "' + scriptlet_id + '" found.';

    return func(this, panel, params);
}
  
$(function() {
    $.fbind = function (self, func) {
        return function() { return func.apply(self, arguments); };
    };
    
    editor = new Editor();

    // do the layout
    editor.loadConfig();
    editor.setupUI();
});
