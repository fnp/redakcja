if (!window.console) {
    window.console = {
        log: function(){
        }
    }
}

var DEFAULT_PERSPECTIVE = "#VisualPerspective";

$(function()
{
	var tabs = $('ol#tabs li');
	var gallery = null;
	CurrentDocument = new $.wikiapi.WikiDocument("document-meta");

	$.blockUI.defaults.baseZ = 10000;

    function initialize()
	{
        var splitter = $('#splitter'),
            editors = $('#editor .editor'),
            vsplitbar = $('.vsplitbar'),
            sidebar = $('#sidebar'),
            dragLayer = $('#drag-layer'),
            vsplitbarWidth = vsplitbar.outerWidth(),
            isHolding = false;

        // Moves panes so that left border of the vsplitbar lands x pixels from the left border of the splitter
        function setSplitbarAt(x) {
            var right = splitterWidth - x;
            editors.each(function() {
                this.style.right = right + 'px';
            });
            vsplitbar[0].style.right = sidebar[0].style.width = (right - vsplitbarWidth) + 'px';
        };

		$(document).keydown(function(event) {
			console.log("Received key:", event);
		});

		/* The save button */
        $('#save-button').click(function(event){
            event.preventDefault();
			$.wiki.showDialog('#save_dialog');
        });

		$('.editor').hide();

		/*
		 * TABS
		 */
        $('.tabs li').live('click', function(event, callback) {
			$.wiki.switchToTab(this);
        });

		$('#tabs li > .tabclose').live('click', function(event, callback) {
			var $tab = $(this).parent();

			if($tab.is('.active'))
				$.wiki.switchToTab(DEFAULT_PERSPECTIVE);

			var p = $.wiki.perspectiveForTab($tab);
			p.destroy();

			return false;
        });


        $(window).resize(function(){
            $('iframe').height($(window).height() - $('#tabs').outerHeight() - $('#source-editor .toolbar').outerHeight());
            splitterWidth = splitter.width();
        });

        $(window).resize();

        vsplitbar.toggle(
			function() {
				$.wiki.state.perspectives.ScanGalleryPerspective.show = true;
				setSplitbarAt(splitterWidth - (480 + vsplitbarWidth));
				$('.vsplitbar').addClass('active');
				$(window).resize();
				$.wiki.perspectiveForTab('#tabs-right .active').onEnter();
			},
			function() {
			    var active_right = $.wiki.perspectiveForTab('#tabs-right .active');
				$.wiki.state.perspectives.ScanGalleryPerspective.show = false;
				$(".vsplitbar-title").html("&uarr;&nbsp;" + active_right.vsplitbar + "&nbsp;&uarr;");
				setSplitbarAt(splitterWidth - vsplitbarWidth);
				$('.vsplitbar').removeClass('active');
				$(window).resize();
				active_right.onExit();
			}
		);


        /* Splitbar dragging support */
        vsplitbar
            .mousedown(function(e) {
                e.preventDefault();
                isHolding = true;
            })
            .mousemove(function(e) {
                if(isHolding) {
                    dragLayer.show(); // We don't show it up until now so that we don't lose single click events on vsplitbar
                }
            });
        dragLayer.mousemove(function(e) {
            setSplitbarAt(e.clientX - vsplitbarWidth/2);
        });
        $('body').mouseup(function(e) {
            dragLayer.hide();
            isHolding = false;
        });


		if($.wiki.state.perspectives.ScanGalleryPerspective.show){
            $('.vsplitbar').trigger('click');
            $(".vsplitbar-title").html("&darr;&nbsp;GALERIA&nbsp;&darr;");
        } else {
            $(".vsplitbar-title").html("&uarr;&nbsp;GALERIA&nbsp;&uarr;");
        }
        window.onbeforeunload = function(e) {
            if($.wiki.isDirty()) {
				e.returnValue = "Na stronie mogą być nie zapisane zmiany.";
				return "Na stronie mogą być nie zapisane zmiany.";
			};
        };

		console.log("Fetching document's text");

		$(document).bind('wlapi_document_changed', function(event, doc) {
			try {
				$('#document-revision').text(doc.revision);
			} catch(e) {
				console.log("Failed handler", e);
			}
		});

		CurrentDocument.fetch({
			success: function(){
				console.log("Fetch success");
				$('#loading-overlay').fadeOut();
				var active_tab = document.location.hash || DEFAULT_PERSPECTIVE;

				if(active_tab == "#ScanGalleryPerspective")
					active_tab = DEFAULT_PERSPECTIVE;

				console.log("Initial tab is:", active_tab)
				$.wiki.switchToTab(active_tab);

                /* every 5 minutes check for a newer version */
                var revTimer = setInterval(function() {
                        CurrentDocument.checkRevision({outdated: function(){
                            $('#header').addClass('out-of-date');
                            clearInterval(revTimer);
                        }});
                    }, 300000);
			},
			failure: function() {
				$('#loading-overlay').fadeOut();
				alert("FAILURE");
			}
		});
    }; /* end of initialize() */


	/* Load configuration */
	$.wiki.loadConfig();

	var initAll = function(a, f) {
		if (a.length == 0) return f();

		$.wiki.initTab({
			tab: a.pop(),
			doc: CurrentDocument,
			callback: function(){
				initAll(a, f);
			}
		});
	};


	/*
	 * Initialize all perspectives
	 */
	initAll( $.makeArray($('.tabs li')), initialize);
	console.log(location.hash);
});
