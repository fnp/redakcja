function loadPanel(target, url) {
    $.log('ajax', url, 'into', target);
    $('.change-notification', $(target).parent()).fadeOut();
    $(document).trigger('panel:unload', target);
    $.ajax({
        url: url,
        dataType: 'html',
        success: function(data, textStatus) {
            $(target).html(data);
            $(document).trigger('panel:load', target);
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
            $(document).unbind('panel:unload.' + eventId);
            $(panel).html('');
            unload(event, panel);
            return false;
        }
    };
    
    $(document).one('panel:load', function(event, panel) {
        self = panel;
        $(document).bind('panel:unload.' + eventId, unloadHandler);
        load(event, panel);
    });
}

$(function() {
    $('#panels').makeHorizPanel({});
    $('#panels').css('top', ($('#header').outerHeight() ) + 'px');
   	
    $('.panel-toolbar select').change(function() {
        loadPanel($('.panel-content', $(this).parent().parent()), $(this).val())
    });
});
