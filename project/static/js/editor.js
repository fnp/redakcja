function Hotkey(code) {
    this.code = code
    this.has_alt = ((code & 0x01 << 8) != 0)
    this.has_ctrl = ((code & 0x01 << 9) != 0)
    this.has_shift = ((code & 0x01 << 10) != 0)
    this.character = String.fromCharCode(code & 0xff)
}

Hotkey.prototype.toString = function() {
    mods = []
    if(this.has_alt) mods.push('Alt')
    if(this.has_ctrl) mods.push('Ctrl')
    if(this.has_shift) mods.push('Shift')
    mods.push('"'+this.character+'"')
    return mods.join('+')
}

function Panel(panelWrap) {
    var self = this;
    self.hotkeys = [];
    self.wrap = panelWrap;
    self.contentDiv = $('.panel-content', panelWrap);
    self.instanceId = Math.ceil(Math.random() * 1000000000);
    // $.log('new panel - wrap: ', self.wrap);
	
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

Panel.prototype._endload = function () {
    // this needs to be here, so we
    this.connectToolbar();
    this.callHook('toolbarResized');
}  

Panel.prototype.load = function (url) {
    // $.log('preparing xhr load: ', this.wrap);
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
            $(self.contentDiv).html("<p>Wystapił błąd podczas wczytywania panelu.</p>");
        }
    });
}

Panel.prototype.unload = function(event, data) {
    // $.log('got unload signal', this, ' target: ', data);
    if( data == this ) {        
        $(this.contentDiv).html('');

        // disconnect the toolbar
        $('div.panel-toolbar span.panel-toolbar-extra', this.wrap).empty();
        
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
    $.log('Panel ', this, ' is aware that ', other, ' changed.');
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
    // $.log('Connecting toolbar', toolbar);
    if(toolbar.length == 0) return;

    // move the extra
    var extra_buttons = $('span.panel-toolbar-extra', toolbar);
    var placeholder = $('div.panel-toolbar span.panel-toolbar-extra', this.wrap);
    placeholder.replaceWith(extra_buttons);
    placeholder.hide();

    var action_buttons = $('button', extra_buttons);

    // connect group-switch buttons
    var group_buttons = $('*.toolbar-tabs-container button', toolbar);

    // $.log('Found groups:', group_buttons);

    group_buttons.each(function() {
        var group = $(this);
        var group_name = group.attr('ui:group');
        // $.log('Connecting group: ' + group_name);

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
    var allbuttons = $.makeArray(action_buttons)
    $.merge(allbuttons,
        $.makeArray($('*.toolbar-button-groups-container button', toolbar)) );
        
    $(allbuttons).each(function() {
        var button = $(this);
        var hk = button.attr('ui:hotkey');
        if(hk) hk = new Hotkey( parseInt(hk) );

        try {
            var params = $.evalJSON(button.attr('ui:action-params'));
        } catch(object) {
            $.log('JSON exception in ', button, ': ', object);
            button.attr('disabled', 'disabled');
            return;
        }

        var callback = function() {
            editor.callScriptlet(button.attr('ui:action'), self, params);
        };

        // connect button
        button.click(callback);
       
        // connect hotkey
        if(hk) {
            self.hotkeys[hk.code] = callback;
        // $.log('hotkey', hk);
        }
        
        // tooltip
        if (button.attr('ui:tooltip') )
        {
            var tooltip = button.attr('ui:tooltip');
            if(hk) tooltip += ' ['+hk+']';

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
    code = event.keyCode;
    if(event.altKey) code = code | 0x100;
    if(event.ctrlKey) code = code | 0x200;
    if(event.shiftKey) code = code | 0x400;

    var callback = this.hotkeys[code];
    if(callback) callback();
}

Panel.prototype.isHotkey = function(event) {
    code = event.keyCode;
    if(event.altKey) code = code | 0x100;
    if(event.ctrlKey) code = code | 0x200;
    if(event.shiftKey) code = code | 0x400;

    if(this.hotkeys[code] != null)
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
        $('.panel-toolbar option', this).each(function() {
            if ($(this).attr('p:panel-name') == self.options.panels[index].name) {
                $(this).parent('select').val($(this).attr('value'));
            }
        });
    });   
}

Editor.prototype.savePanelOptions = function() {
    var self = this;
    var panels = [];
    $('.panel-wrap', self.rootDiv).not('.panel-content-overlay').each(function() {
        panels.push({
            name: $('.panel-toolbar option:selected', this).attr('p:panel-name'),
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

    self.showPopup('save-waiting', '', -1);

    $.ajax({
        url: saveInfo.url,
        dataType: 'json',
        success: function(data, textStatus) {
            if (data.result != 'ok') {
                self.showPopup('save-error', (data.errors && data.errors[0]) || 'Nieznany błąd X_X.');
            }
            else {
                self.refreshPanels();


                if(self.autosaveTimer)
                    clearTimeout(self.autosaveTimer);

                if (data.warnings == null)
                    self.showPopup('save-successful');
                else
                    self.showPopup('save-warn', data.warnings[0]);
            }
            
            self.advancePopupQueue();
        },
        error: function(rq, tstat, err) {
            self.showPopup('save-error', '- bład wewnętrzny serwera.');
            self.advancePopupQueue();
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
    $('#toolbar-button-update').attr('disabled', 'disabled');
    
    if(this.autosaveTimer) return;
    this.autosaveTimer = setTimeout( function() {
        self.autoSave();
    }, 300000 );
};

Editor.prototype.updateUserBranch = function() {
    if( $('.panel-wrap.changed').length != 0)
        alert("There are unsaved changes - can't update.");

    var self = this;
    $.ajax({
        url: $('#toolbar-button-update').attr('ui:ajax-action'),
        dataType: 'json',
        success: function(data, textStatus) {
            switch(data.result) {
                case 'done':
                    self.showPopup('generic-yes', 'Plik uaktualniony.');
                    self.refreshPanels()
                    break;
                case 'nothing-to-do':
                    self.showPopup('generic-info', 'Brak zmian do uaktualnienia.');
                    break;
                default:
                    self.showPopup('generic-error', data.errors && data.errors[0]);
            }
        },
        error: function(rq, tstat, err) {
            self.showPopup('generic-error', 'Błąd serwera: ' + err);
        },
        type: 'POST',
        data: {}
    });
}

Editor.prototype.sendMergeRequest = function (message) {
    if( $('.panel-wrap.changed').length != 0)        
        alert("There are unsaved changes - can't commit.");

    var self =  this;    

    $('#commit-dialog-related-issues input:checked').
        each(function() { message += ' refs #' + $(this).val(); });  
    
    $.ajax({        
        url: $('#commit-dialog form').attr('action'),
        dataType: 'json',
        success: function(data, textStatus) {
            switch(data.result) {
                case 'done':
                    self.showPopup('generic-yes', 'Łączenie zmian powiodło się.');

                    if(data.localmodified)
                        self.refreshPanels()
                        
                    break;
                case 'nothing-to-do':
                    self.showPopup('generic-info', 'Brak zmian do połaczenia.');
                    break;
                default:
                    self.showPopup('generic-error', data.errors && data.errors[0]);
            }
        },
        error: function(rq, tstat, err) {
            self.showPopup('generic-error', 'Błąd serwera: ' + err);
        },
        type: 'POST',
        data: {
            'message': message
        }
    }); 
}

Editor.prototype.postSplitRequest = function(s, f)
{
    $.ajax({
        url: $('#split-dialog form').attr('action'),
        dataType: 'html',
        success: s,
        error: f,
        type: 'POST',
        data: $('#split-dialog form').serialize()
    });
};


Editor.prototype.allPanels = function() {
    return $('#' + this.rootDiv.attr('id') +' > *.panel-wrap', this.rootDiv.parent());
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
        return function() { 
            return func.apply(self, arguments);
        };
    };
    
    editor = new Editor();

    // do the layout
    editor.loadConfig();
    editor.setupUI();
});
