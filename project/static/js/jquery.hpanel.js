(function($){
    
	/* behaviour */
	$.hpanel = {
        settings: {},
		current_data: {},
        resize_start: function(event, mydata) {
			$(document).bind('mousemove', mydata, $.hpanel.resize_changed).
				bind('mouseup', mydata, $.hpanel.resize_stop); 

			$('.panel-overlay', mydata.root).css('display', 'block');
			return false;
		},
		resize_changed: function(event) {
			var old_width = parseInt(event.data.overlay.css('width'));
			var delta = event.pageX + event.data.hotspot_x - old_width;
			event.data.overlay.css({'width': old_width + delta});

			if(event.data.overlay.next) {
				var left = parseInt(event.data.overlay.next.css('left'));
				event.data.overlay.next.css('left', left+delta);
			}

            return false; 
        },
        resize_stop: function(event) {
            $(document).unbind('mousemove', $.hpanel.resize_changed).unbind('mouseup', $.hpanel.resize_stop);
			// $('.panel-content', event.data.root).css('display', 'block');
			var overlays = $('.panel-content-overlay', event.data.root);
			$('.panel-content-overlay', event.data.root).each(function(i) {
				if( $(this).data('panel').hasClass('last-panel') )
					$(this).data('panel').css({
						'left': $(this).css('left'), 'right': $(this).css('right')}); 
				else
					$(this).data('panel').css({
						'left': $(this).css('left'), 'width': $(this).css('width')}); 
			});
			$('.panel-overlay', event.data.root).css('display', 'none');
            $(event.data.root).trigger('stopResize');
        }
    };
    
    $.fn.makeHorizPanel = function(options) 
	{
		var root = $(this)
		var all_panels = $('.panel-wrap', root)

		/* create an overlay */
		var overlay_root = $("<div class='panel-overlay'></div>");
		root.append(overlay_root);

		var prev = null;

		all_panels.each(function(i) {
			var panel = $(this);
			var handle = $('.panel-slider', panel);
			var overlay = $("<div class='panel-content-overlay panel-wrap'><p>Panel #"+i+"</p></div>");
			overlay_root.append(overlay);
			overlay.data('panel', panel);
			overlay.data('next', null);

			if( panel.hasClass('last-panel') )				
				overlay.css({'left': panel.css('left'), 'right': panel.css('right')});
			else
				overlay.css({'left': panel.css('left'), 'width': panel.css('width')});

			if (prev) prev.next = overlay;

			if(handle.length != 0) {
				$.log('Has handle: ' + panel.attr('id') );
				overlay.append(handle.clone());
				/* attach the trigger */
				handle.mousedown(function(event) {
					var touch_data = {
						root: root, overlay: overlay,
						hotspot_x: event.pageX - handle.position().left
					};

					$(this).trigger('hpanel:panel-resize-start', touch_data);
					return false;
				});
				$('.panel-content', panel).css('right', 
					(handle.outerWidth() || 10) + 'px');
				$('.panel-content-overlay', panel).css('right',
					(handle.outerWidth() || 10) + 'px');
			}
				
			prev = overlay;
        });

	root.bind('hpanel:panel-resize-start', $.hpanel.resize_start);
    };
})(jQuery);

