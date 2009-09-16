/*
 * UI related Editor methods
 */
Editor.prototype.setupUI = function() {
    // set up the UI visually and attach callbacks
    var self = this;

    var resize_start = function(event, mydata) {
        $(document).bind('mousemove', mydata, resize_changed).
        bind('mouseup', mydata, resize_stop);

        $('.panel-overlay', mydata.root).css('display', 'block');
        return false;
    }
    var resize_changed =  function(event) {
        var old_width = parseInt(event.data.overlay.css('width'));
        var delta = event.pageX + event.data.hotspot_x - old_width;

        if(old_width + delta < 12) delta = 12 - old_width;
        if(old_width + delta > $(window).width()) 
            delta = $(window).width() - old_width;
        
        event.data.overlay.css({
            'width': old_width + delta
        });

        if(event.data.overlay.next) {
            var left = parseInt(event.data.overlay.next.css('left'));
            event.data.overlay.next.css('left', left+delta);
        }

        return false;
    };

    var resize_stop = function(event) {
        $(document).unbind('mousemove', resize_changed).unbind('mouseup', resize_stop);
        // $('.panel-content', event.data.root).css('display', 'block');
        var overlays = $('.panel-content-overlay', event.data.root);
        $('.panel-content-overlay', event.data.root).each(function(i) {
            if( $(this).data('panel').hasClass('last-panel') )
                $(this).data('panel').css({
                    'left': $(this).css('left'),
                    'right': $(this).css('right')
                });
            else
                $(this).data('panel').css({
                    'left': $(this).css('left'),
                    'width': $(this).css('width')
                });
        });
        $('.panel-overlay', event.data.root).css('display', 'none');
        $(event.data.root).trigger('stopResize');
    };

    /*
     * Prepare panels (overlays & stuff)
     */
    /* create an overlay */
    var panel_root = self.rootDiv;
    var overlay_root = $("<div class='panel-overlay'></div>");
    panel_root.append(overlay_root);

    var prev = null;

    $('*.panel-wrap', panel_root).each( function()
    {
        var panel = $(this);
        var handle = $('.panel-slider', panel);
        var overlay = $("<div class='panel-content-overlay panel-wrap'>&nbsp;</div>");
        overlay_root.append(overlay);
        overlay.data('panel', panel);
        overlay.data('next', null);

        if (prev) prev.next = overlay;

        if( panel.hasClass('last-panel') )
        {
            overlay.css({
                'left': panel.css('left'),
                'right': panel.css('right')
            });
        }
        else {
            overlay.css({
                'left': panel.css('left'),
                'width': panel.css('width')
            });
            // $.log('Has handle: ' + panel.attr('id'));
            overlay.append(handle.clone());
            /* attach the trigger */
            handle.mousedown(function(event) {
                var touch_data = {
                    root: panel_root,
                    overlay: overlay,
                    hotspot_x: event.pageX - handle.position().left
                };

                $(this).trigger('hpanel:panel-resize-start', touch_data);
                return false;
            });
            $('.panel-content', panel).css('right',
                (handle.outerWidth() || 10) + 'px');
            $('.panel-content-overlay', panel).css('right',
                (handle.outerWidth() || 10) + 'px');
        };

        prev = overlay;
    });

    panel_root.bind('hpanel:panel-resize-start', resize_start);
    self.rootDiv.bind('stopResize', function() {
        self.savePanelOptions();      
    });
    
    /*
     * Connect panel actions
     */
    $('#panels > *.panel-wrap').each(function() {
        var panelWrap = $(this);
        // $.log('wrap: ', panelWrap);
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

        self.rootDiv.bind('stopResize', function() {
            panel.callHook('toolbarResized');
        });
    });

    $(document).bind('panel:contentChanged', function() {
        self.onContentChanged.apply(self, arguments)
    });  

    /*
     * Connect various buttons
     */

    $('#toolbar-button-quick-save').click( function (event, data) {
        self.saveToBranch();
    } );

    $('#toolbar-button-save').click( function (event, data) {
        $('#commit-dialog').jqmShow( {callback: $.fbind(self, self.saveToBranch)} );
    } );

    $('#toolbar-button-update').click( function (event, data) {
        if (self.updateUserBranch()) {
            // commit/update can be called only after proper, save
            // this means all panels are clean, and will get refreshed
            // do this only, when there are any changes to local branch
            self.refreshPanels();
        }
    } );

    /* COMMIT DIALOG */
    $('#commit-dialog').
    jqm({
        modal: true,
        onShow: $.fbind(self, self.loadRelatedIssues)        
    });

    $('#toolbar-button-commit').click( function (event, data) {
        $('#commit-dialog').jqmShow( {callback: $.fbind(self, self.sendMergeRequest)} );
    } );
    
    /* STATIC BINDS */
    $('#commit-dialog-cancel-button').click(function() {
        $('#commit-dialog-error-empty-message').hide();
        $('#commit-dialog').jqmHide();
    });   
    

    /* SPLIT DIALOG */
    $('#split-dialog').jqm({
        modal: true,
        onShow: $.fbind(self, self.loadSplitDialog)
    }).
    jqmAddClose('button.dialog-close-button');

// $('#split-dialog').   
}

Editor.prototype.loadRelatedIssues = function(hash)
{
    var self = this;
    var c = $('#commit-dialog-related-issues');

    $('#commit-dialog-save-button').click( function (event, data)
    {
        if( $('#commit-dialog-message').val().match(/^\s*$/)) {
            $('#commit-dialog-error-empty-message').fadeIn();
        }
        else {
            $('#commit-dialog-error-empty-message').hide();
            $('#commit-dialog').jqmHide();

            var message = $('#commit-dialog-message').val();
            $('#commit-dialog-related-issues input:checked').
                each(function() { message += ' refs #' + $(this).val(); });
            $.log("COMMIT APROVED", hash.t);
            hash.t.callback(message);
        }

        return false;
    });

    $("div.loading-box", c).show();
    $("div.fatal-error-box", c).hide();
    $("div.container-box", c).hide();
    
    $.getJSON( c.attr('ui:ajax-src') + '?callback=?',
    function(data, status)
    {
        var fmt = '';
        $(data).each( function() {
            fmt += '<label><input type="checkbox" checked="checked"'
            fmt += ' value="' + this.id + '" />' + this.subject +'</label>\n'
        });
        $("div.container-box", c).html(fmt);
        $("div.loading-box", c).hide();
        $("div.container-box", c).show();        
    });   
    
    hash.w.show();
}

Editor.prototype.loadSplitDialog = function(hash)
{
    var self = this;    
    
    $("div.loading-box", hash.w).show();
    $("div.fatal-error-box", hash.w).hide();
    $('div.container-box', hash.w).hide();
    hash.w.show();

    function onFailure(rq, tstat, err) {
        $('div.container-box', hash.w).html('');
        $("div.loading-box", hash.w).hide();
        $("div.fatal-error-box", hash.w).show();
        hash.t.failure();
    };

    function onSuccess(data, status) {
        // put the form into the window
        $('div.container-box', hash.w).html(data);
        $("div.loading-box", hash.w).hide();
        $('form input[name=splitform-splittext]', hash.w).val(hash.t.selection);
        $('form input[name=splitform-fulltext]', hash.w).val(hash.t.fulltext);
        $('div.container-box', hash.w).show();

        // connect buttons
        $('#split-dialog-button-accept').click(function() {
            self.postSplitRequest(onSuccess, onFailure);
            return false;
        });

        $('#split-dialog-button-close').click(function() {
            hash.w.jqmHide();
            $('div.container-box', hash.w).html('');
            hash.t.failure();
        });

        $('#split-dialog-button-dismiss').click(function() {
            hash.w.jqmHide();
            $('div.container-box', hash.w).html('');
            hash.t.success();
        });

        if($('#id_splitform-autoxml').is(':checked'))
            $('#split-form-dc-subform').show();
        else
            $('#split-form-dc-subform').hide();

        $('#id_splitform-autoxml').change(function() {            
            if( $(this).is(':checked') )
                $('#split-form-dc-subform').show();
            else
                $('#split-form-dc-subform').hide();
        });
    };   

    $.ajax({
        url: 'split',
        dataType: 'html',
        success: onSuccess,
        error: onFailure,
        type: 'GET',
        data: {}
    });
}

/* Refreshing routine */
Editor.prototype.refreshPanels = function() {
    var self = this;

    self.allPanels().each(function() {
        var panel = $(this).data('ctrl');
        $.log('Refreshing: ', this, panel);
        if ( panel.changed() )
            panel.unmarkChanged();
        else
            panel.refresh();
    });

    $('button.provides-save').attr('disabled', 'disabled');
    $('button.requires-save').removeAttr('disabled');
};

/*
 * Pop-up messages
 */
Editor.prototype.showPopup = function(name, text, timeout)
{
    timeout = timeout || 4000;
    var self = this;
    self.popupQueue.push( [name, text, timeout] )

    if( self.popupQueue.length > 1)
        return;

    var box = $('#message-box > #' + name);
    $('*.data', box).html(text || '');
    box.fadeIn(100);

    if(timeout > 0)
        setTimeout( $.fbind(self, self.advancePopupQueue), timeout);
};

Editor.prototype.advancePopupQueue = function() {
    var self = this;
    var elem = this.popupQueue.shift();
    if(elem) {
        var box = $('#message-box > #' + elem[0]);

        box.fadeOut(100, function()
        {
            $('*.data', box).html('');

            if( self.popupQueue.length > 0) {
                var ibox = $('#message-box > #' + self.popupQueue[0][0]);
                $('*.data', ibox).html(self.popupQueue[0][1] || '');
                ibox.fadeIn(100);
                if(self.popupQueue[0][2] > 0)
                    setTimeout( $.fbind(self, self.advancePopupQueue), self.popupQueue[0][2]);
            }
        });
    }
};


