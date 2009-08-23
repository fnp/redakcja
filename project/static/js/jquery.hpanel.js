(function($){
    
	/* behaviour */
	$.hpanel = {
        settings: {},
		current_data: {},
        resize_start: function(event, mydata) {
			console.log('Panel ' + mydata.panel.attr('id') + ' started resizing');
			$(document).bind('mousemove', mydata, $.hpanel.resize_changed).
				bind('mouseup', mydata, $.hpanel.resize_stop); 
			$('iframe').bind('mousemove', mydata, $.hpanel.resize_changed).
				bind('mouseup', mydata, $.hpanel.resize_stop); 
			return false;
		},
		resize_changed: function(event) {
			var old_width = parseInt(event.data.panel.css('width'));
			var delta = event.pageX + event.data.hotspot_x - old_width;
			event.data.panel.css({'width': old_width + delta});

			if(event.data.panel.next_panel) {
				var left = parseInt(event.data.panel.next_panel.css('left'));
				console.log('left: ' + left + ' new_left: ' + (left+delta) );
				event.data.panel.next_panel.css('left', left+delta);
			}

            return false; 
        },
        resize_stop: function(event) {
            $(document).unbind('mousemove', $.hpanel.resize_changed).unbind('mouseup', $.hpanel.resize_stop);
	    $('iframe').unbind('mousemove', $.hpanel.resize_changed).unbind('mouseup', $.hpanel.resize_stop);
            $('body').css('cursor', 'auto');
        }
    };
    
    $.fn.make_hpanel = function(options) 
	{
		console.log('Making an hpanel out of "#' +  $(this).attr('id') + '"'); 
		var root = $(this)
		var all_panels = $('.panel-wrap', root)
		console.log('Panels: ' + all_panels);

		var prev = null;

		all_panels.each(function(i) {
			var panel = $(all_panels[i]);
			var handle = $('.panel-slider', panel) 

			panel.next_panel = null;
			if (prev) prev.next_panel = panel;

			/* attach the trigger */
	        handle.mousedown(function(event) {
				var touch_data = {
					panel_root: root, 
					panel: panel, 
					hotspot_x: event.pageX - handle.position().left
				};
				$(this).trigger('hpanel:panel-resize-start', touch_data);
				return false;
			});
			prev = panel;
        });

		root.bind('hpanel:panel-resize-start', $.hpanel.resize_start);
    };
})(jQuery);

