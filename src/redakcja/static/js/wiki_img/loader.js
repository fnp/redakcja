if (!window.console) {
    window.console = {
        log: function(){
        }
    }
}

DEFAULT_PERSPECTIVE = "#MotifsPerspective";

$(function()
{
	var tabs = $('ol#tabs li');
	var gallery = null;
	CurrentDocument = new $.wikiapi.WikiDocument("document-meta");

	$.blockUI.defaults.baseZ = 10000;

    function initialize()
	{
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
            event.preventDefault();
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


        /*$(window).resize(function(){
            $('iframe').height($(window).height() - $('#tabs').outerHeight() - $('#source-editor .toolbar').outerHeight());
        });

        $(window).resize();*/

        /*$('.vsplitbar').toggle(
			function() {
				$.wiki.state.perspectives.ScanGalleryPerspective.show = true;
				$('#sidebar').show();
				$('.vsplitbar').css('right', 480).addClass('active');
				$('#editor .editor').css('right', 510);
				$(window).resize();
				$.wiki.perspectiveForTab('#tabs-right .active').onEnter();
			},
			function() {
			    var active_right = $.wiki.perspectiveForTab('#tabs-right .active');
				$.wiki.state.perspectives.ScanGalleryPerspective.show = false;
				$('#sidebar').hide();
				$('.vsplitbar').css('right', 0).removeClass('active');
				$(".vsplitbar-title").html("&uarr;&nbsp;" + active_right.vsplitbar + "&nbsp;&uarr;");
				$('#editor .editor').css('right', 30);
				$(window).resize();
				active_right.onExit();
			}
		);*/

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

				console.log("Initial tab is:", active_tab)
				$.wiki.switchToTab(active_tab);
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


