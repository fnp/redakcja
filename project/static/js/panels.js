function loadPanel(target, url) {
    $.log('ajax', url, 'into', target);
    $(document).trigger('panel:unload', target);
    $.ajax({
        url: url,
        dataType: 'html',
        success: function(data, textStatus) {
            $.log(target, 'ajax success');
            $(target).html(data);
            $.log(target, 'triggering panel:load');
            $(document).trigger('panel:load', target);
            // panel(target);
        },
        error: function(request, textStatus, errorThrown) {
            $.log('ajax', url, target, 'error:', textStatus, errorThrown);
        }
    });
}

// Funkcja do tworzenia nowych paneli
function panel(load, unload) {
    var self = null;
    var eventId = Math.ceil(Math.random() * 1000000000);
    
    unloadHandler = function(event, panel) {
        if (self && self == panel) {
            $.log('Panel', panel, 'unloading');
            $(document).unbind('panel:unload.' + eventId);
            $(panel).html('');
            unload(event, panel);
            $.log('Panel', panel, 'unloaded');
            return false;
        }
    };
    
    $(document).one('panel:load', function(event, panel) {
        self = panel;
        $.log('Panel', panel, 'loading');
        $(document).bind('panel:unload.' + eventId, unloadHandler);
        load(event, panel);
        $.log('Panel', panel, 'loaded');
    });
}

$(function() {
    $('#panels').makeHorizPanel({});
    $('#panels').css('top', ($('#header').outerHeight() ) + 'px');
   	
    $('.panel-toolbar select').change(function() {
        loadPanel($('.panel-content', $(this).parent().parent()), $(this).val())
    });
});
